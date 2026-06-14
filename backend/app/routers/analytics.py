"""
Analytics API Router (US-034, US-036, US-044)
Dashboard et statistiques
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List, Optional
from datetime import datetime, timedelta, date
import io, base64

import matplotlib
matplotlib.use("Agg")          # pas d'interface graphique côté serveur
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from ..database import get_db
from ..models import Patient, Consultation, Diagnostic, AnalyseIA, Medecin, Infirmier
from .auth import get_current_user, get_current_non_admin

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# ── Palette cohérente avec l'application ──────────────────────────────────────
PALETTE_BARS = [
    "#4F46E5", "#7C3AED", "#DB2777", "#059669", "#D97706",
    "#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6",
]
BG_COLOR   = "#F9FAFB"
TEXT_COLOR = "#1F2937"
GRID_COLOR = "#E5E7EB"


def _fig_to_b64(fig: plt.Figure) -> str:
    """Convertit une figure matplotlib en chaîne base64."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight",
                facecolor=BG_COLOR, edgecolor="none")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return encoded


def _parse_periode(date_debut: Optional[str], date_fin: Optional[str]):
    """
    Convertit les bornes ISO (YYYY-MM-DD) en datetimes inclusifs
    [date_debut 00:00:00, date_fin 23:59:59.999999]. Retourne (None, None) sans filtre.
    """
    try:
        debut = datetime.combine(date.fromisoformat(date_debut), datetime.min.time()) if date_debut else None
        fin = datetime.combine(date.fromisoformat(date_fin), datetime.max.time()) if date_fin else None
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Format de date invalide — attendu YYYY-MM-DD",
        )
    if debut and fin and debut > fin:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_debut doit être antérieure ou égale à date_fin",
        )
    return debut, fin


def _entre(query, colonne, debut: Optional[datetime], fin: Optional[datetime]):
    """Applique le filtre de période sur la colonne datetime donnée."""
    if debut is not None:
        query = query.filter(colonne >= debut)
    if fin is not None:
        query = query.filter(colonne <= fin)
    return query


@router.get("/dashboard")
def get_dashboard_stats(
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict:
    """
    US-044: Dashboard avec statistiques globales.
    date_debut / date_fin (YYYY-MM-DD, optionnels) filtrent toutes les statistiques
    sur la période : patients par date de création, consultations par date_heure,
    diagnostics par date de leur consultation.
    """
    debut, fin = _parse_periode(date_debut, date_fin)

    # KPI 1: Nombre total de patients (créés dans la période)
    total_patients = _entre(
        db.query(func.count(Patient.patient_id)), Patient.created_at, debut, fin
    ).scalar() or 0

    # KPI 2: Nombre de patients ce mois
    first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    patients_this_month = db.query(func.count(Patient.patient_id)).filter(
        Patient.created_at >= first_day_month
    ).scalar()

    def count_consultations(statut: Optional[str] = None) -> int:
        q = _entre(db.query(func.count(Consultation.consultation_id)), Consultation.date_heure, debut, fin)
        if statut is not None:
            q = q.filter(Consultation.statut == statut)
        return q.scalar() or 0

    # KPI 3: Nombre de consultations
    total_consultations = count_consultations()

    # KPI 3b: Consultations par statut
    consultations_en_attente = count_consultations("en attente")
    consultations_en_cours = count_consultations("en cours")
    consultations_terminees = count_consultations("terminée")
    consultations_en_attente_medecin = count_consultations("en_attente_medecin")

    # Les diagnostics n'ont pas de date propre : on les rattache à la date de leur consultation
    def diag_query(*colonnes):
        q = db.query(*colonnes)
        if debut is not None or fin is not None:
            q = q.join(Consultation, Diagnostic.consultation_id == Consultation.consultation_id)
            q = _entre(q, Consultation.date_heure, debut, fin)
        return q

    # KPI 4: Nombre de diagnostics
    total_diagnostics = diag_query(func.count(Diagnostic.diagnostic_id)).scalar() or 0

    # KPI 5: Taux d'approbation
    diagnostics_approuves = diag_query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0

    taux_approbation = (diagnostics_approuves / total_diagnostics * 100) if total_diagnostics > 0 else 0

    # KPI 6: Confiance moyenne (si la colonne existe)
    # Note: La table diagnostics utilise 'certitude' pas 'confiance'
    avg_confidence = diag_query(func.avg(Diagnostic.certitude)).scalar() or 0

    # KPI 7: Consultations aujourd'hui
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    consultations_aujourd_hui = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.date_heure >= today_start,
        Consultation.date_heure <= today_end
    ).scalar() or 0

    # KPI 9: Diagnostics IA rejetés
    diagnostics_rejetes = diag_query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "REJETÉ"
    ).scalar() or 0

    # Tendance patients par jour (période filtrée, sinon 7 derniers jours)
    tendance_depuis = debut if debut is not None else datetime.now() - timedelta(days=7)
    daily_patients_q = db.query(
        func.date(Patient.created_at).label('date'),
        func.count(Patient.patient_id).label('count')
    ).filter(
        Patient.created_at >= tendance_depuis
    )
    if fin is not None:
        daily_patients_q = daily_patients_q.filter(Patient.created_at <= fin)
    daily_patients = daily_patients_q.group_by(func.date(Patient.created_at)).all()

    # Top 5 diagnostics (utiliser nom_maladie)
    top_diagnostics = diag_query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.diagnostic_id).label('count')
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).order_by(
        func.count(Diagnostic.diagnostic_id).desc()
    ).limit(5).all()

    return {
        "periode": {
            "date_debut": date_debut,
            "date_fin": date_fin,
            "filtre_actif": debut is not None or fin is not None,
        },
        "kpis": {
            "total_patients": total_patients,
            "patients_ce_mois": patients_this_month,
            "total_consultations": total_consultations,
            "consultations_en_attente": consultations_en_attente,
            "consultations_en_attente_medecin": consultations_en_attente_medecin,
            "consultations_en_cours": consultations_en_cours,
            "consultations_terminees": consultations_terminees,
            "total_diagnostics": total_diagnostics,
            "taux_approbation": round(taux_approbation, 2),
            "confiance_moyenne": round(float(avg_confidence) * 100, 2),
            "consultations_aujourd_hui": consultations_aujourd_hui,
            "diagnostics_approuves": diagnostics_approuves,
            "diagnostics_rejetes": diagnostics_rejetes
        },
        "tendance_patients": [
            {"date": str(row.date), "count": row.count}
            for row in daily_patients
        ],
        "top_diagnostics": [
            {"diagnostic": row.nom_maladie, "count": row.count}
            for row in top_diagnostics
        ]
    }


@router.get("/series")
def get_daily_series(
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict:
    """
    Séries quotidiennes pour la page Analytique.
    Retourne, jour par jour sur la période (par défaut les 30 derniers jours) :
    consultations, nouveaux patients, diagnostics IA, diagnostics approuvés
    et taux d'approbation. Les jours sans activité sont remplis à zéro.
    """
    debut, fin = _parse_periode(date_debut, date_fin)
    if fin is None:
        fin = datetime.combine(date.today(), datetime.max.time())
    if debut is None:
        # Sans borne de début : remonter au tout premier enregistrement
        # (plus ancienne consultation ou plus ancien patient) pour couvrir
        # l'intégralité de l'historique. Repli sur 30 jours si la base est vide.
        premiere_consultation = db.query(func.min(Consultation.date_heure)).scalar()
        premier_patient = db.query(func.min(Patient.created_at)).scalar()
        premieres = [d for d in (premiere_consultation, premier_patient) if d is not None]
        if premieres:
            debut = datetime.combine(min(premieres).date(), datetime.min.time())
        else:
            debut = datetime.combine(fin.date() - timedelta(days=29), datetime.min.time())

    nb_jours = (fin.date() - debut.date()).days + 1
    if nb_jours > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Période trop longue — maximum 1000 jours",
        )
    jours = [debut.date() + timedelta(days=i) for i in range(nb_jours)]

    def par_jour(rows) -> Dict[str, int]:
        # func.date() renvoie un str sous SQLite, un objet date ailleurs — on normalise en ISO
        return {str(r.date): r.count for r in rows}

    consultations = par_jour(
        _entre(
            db.query(func.date(Consultation.date_heure).label("date"),
                     func.count(Consultation.consultation_id).label("count")),
            Consultation.date_heure, debut, fin,
        ).group_by(func.date(Consultation.date_heure)).all()
    )

    patients = par_jour(
        _entre(
            db.query(func.date(Patient.created_at).label("date"),
                     func.count(Patient.patient_id).label("count")),
            Patient.created_at, debut, fin,
        ).group_by(func.date(Patient.created_at)).all()
    )

    def diag_par_jour(statut: Optional[str] = None) -> Dict[str, int]:
        q = db.query(func.date(Consultation.date_heure).label("date"),
                     func.count(Diagnostic.diagnostic_id).label("count")
        ).join(Consultation, Diagnostic.consultation_id == Consultation.consultation_id)
        q = _entre(q, Consultation.date_heure, debut, fin)
        if statut is not None:
            q = q.filter(Diagnostic.statut == statut)
        return par_jour(q.group_by(func.date(Consultation.date_heure)).all())

    diagnostics = diag_par_jour()
    approuves = diag_par_jour("CONFIRMÉ")
    rejetes = diag_par_jour("REJETÉ")

    serie_consultations = [consultations.get(j.isoformat(), 0) for j in jours]
    serie_patients = [patients.get(j.isoformat(), 0) for j in jours]
    serie_diagnostics = [diagnostics.get(j.isoformat(), 0) for j in jours]
    serie_approuves = [approuves.get(j.isoformat(), 0) for j in jours]
    serie_rejetes = [rejetes.get(j.isoformat(), 0) for j in jours]
    serie_taux = [
        round(a / d * 100, 1) if d > 0 else 0
        for a, d in zip(serie_approuves, serie_diagnostics)
    ]

    total_diag = sum(serie_diagnostics)
    total_approuves = sum(serie_approuves)

    return {
        "periode": {
            "date_debut": debut.date().isoformat(),
            "date_fin": fin.date().isoformat(),
        },
        "dates": [j.isoformat() for j in jours],
        "consultations": serie_consultations,
        "patients": serie_patients,
        "diagnostics": serie_diagnostics,
        "diagnostics_approuves": serie_approuves,
        "diagnostics_rejetes": serie_rejetes,
        "taux_approbation": serie_taux,
        "totaux": {
            "consultations": sum(serie_consultations),
            "patients": sum(serie_patients),
            "diagnostics": total_diag,
            "diagnostics_approuves": total_approuves,
            "diagnostics_rejetes": sum(serie_rejetes),
            "taux_approbation": round(total_approuves / total_diag * 100, 1) if total_diag > 0 else 0,
        },
    }


@router.get("/diagnostics/distribution")
def get_diagnostics_distribution(db: Session = Depends(get_db)) -> Dict:
    """
    US-036: Distribution des diagnostics
    """
    # Compter par diagnostic (utiliser nom_maladie au lieu de diagnostic_final)
    distribution = db.query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.diagnostic_id).label('count')
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).all()
    
    total = sum([row.count for row in distribution])
    
    return {
        "diagnostics": [
            {
                "nom": row.nom_maladie,
                "count": row.count,
                "pourcentage": round(row.count / total * 100, 2) if total > 0 else 0
            }
            for row in distribution
        ],
        "total": total
    }


@router.get("/performance/model")
def get_model_performance(db: Session = Depends(get_db)) -> Dict:
    """
    US-038: Performance du modèle
    """
    # Précision par niveau de sévérité (pas de niveau_confiance dans le schéma)
    high_confidence = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.severite == "CRITIQUE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0

    medium_confidence = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.severite == "GRAVE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0

    low_confidence = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.severite == "MODERE",
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0

    # Taux de rejet
    total_diagnostics = db.query(func.count(Diagnostic.diagnostic_id)).scalar() or 0
    rejetes = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "REJETÉ"
    ).scalar() or 0
    
    taux_rejet = (rejetes / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    return {
        "par_confiance": {
            "high": high_confidence,
            "medium": medium_confidence,
            "low": low_confidence
        },
        "taux_rejet": round(taux_rejet, 2),
        "total_diagnostics": total_diagnostics
    }


@router.get("/consultations/recent")
def get_recent_consultations(
    limit: int = 10,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> List[Dict]:
    """
    Consultations récentes avec patient_id pour accès au dossier.
    Exclut les consultations orphelines (patient supprimé hors API).
    date_debut / date_fin (YYYY-MM-DD, optionnels) limitent la liste à la période.
    Accès interdit aux administrateurs (données médicales individuelles).
    """
    debut, fin = _parse_periode(date_debut, date_fin)
    consultations = (
        _entre(
            db.query(Consultation).join(Patient, Consultation.patient_id == Patient.patient_id),
            Consultation.date_heure, debut, fin,
        )
        .order_by(Consultation.date_heure.desc())
        .limit(limit)
        .all()
    )
    
    return [
        {
            "id": c.consultation_id,
            "patient_id": c.patient_id,
            "nom_patient": c.nom_patient,
            "date": c.date_heure.isoformat(),
            "date_heure": c.date_heure.isoformat(),
            "motif": c.motif,
            "statut": c.statut,
            "medecin_id": c.medecin_id,
        }
        for c in consultations
    ]


@router.get("/personnel/disponible")
def get_personnel_disponible(db: Session = Depends(get_db)) -> Dict:
    """
    Personnel médical disponible (médecins et infirmiers).
    Retourne tous les médecins disponibles de la table 'medecins'.
    Les utilisateurs avec role='medecin' créés via l'admin sont automatiquement
    synchronisés vers la table 'medecins' à la création.
    """
    medecins_dispo = db.query(Medecin).filter(Medecin.disponible == True).order_by(Medecin.nom).all()
    total_medecins = db.query(func.count(Medecin.medecin_id)).scalar() or 0

    # Infirmiers disponibles
    infirmiers_dispo = db.query(Infirmier).filter(Infirmier.disponible == True).all()
    total_infirmiers = db.query(func.count(Infirmier.infirmier_id)).scalar() or 0

    return {
        "medecins": {
            "disponibles": len(medecins_dispo),
            "total": total_medecins,
            "liste": [
                {
                    "id": m.medecin_id,
                    "nom": m.nom,
                    "prenoms": m.prenoms,
                    "specialite": m.specialite,
                    "telephone": m.telephone,
                }
                for m in medecins_dispo
            ],
        },
        "infirmiers": {
            "disponibles": len(infirmiers_dispo),
            "total": total_infirmiers,
            "liste": [
                {
                    "id": i.infirmier_id,
                    "nom": i.nom,
                    "prenoms": i.prenoms,
                    "telephone": i.telephone,
                    "email": i.email,
                }
                for i in infirmiers_dispo
            ],
        },
    }


# ══════════════════════════════════════════════════════════════════════════════
#  RÉPARTITION GÉOGRAPHIQUE DES MALADIES (carte du monde dynamique)
#
#  Deux informations DISTINCTES :
#   1. Les POURCENTAGES par continent = distribution mondiale de la maladie selon
#      l'OMS (donnée externe). Pour les maladies à distribution connue, on utilise
#      les vrais % OMS (table MALADIE_OMS). Pour les autres (la plupart), on
#      estime la répartition au prorata de la population de chaque continent.
#   2. Le NOMBRE DE CAS = cas réellement diagnostiqués dans l'application (base).
#  La carte ne mélange donc plus les deux : les barres = OMS, le bas = nos cas.
# ══════════════════════════════════════════════════════════════════════════════

# Les 5 continents affichés sur la carte. Ordre = ordre d'affichage des barres.
CONTINENTS = ["Afrique", "Europe", "Amérique", "Asie", "Océanie"]

# Poids de population mondiale par continent (~2023, en %). Sert d'estimation de
# répartition pour les maladies ubiquitaires sans donnée OMS spécifique.
POP_CONTINENT = {
    "Asie": 59.0, "Afrique": 18.0, "Amérique": 13.0, "Europe": 9.0, "Océanie": 1.0,
}

# Distribution OMS (% des cas/charge mondiale par continent) pour les maladies à
# répartition géographique marquée. Valeurs approchées d'après les rapports OMS.
# Les % reflètent la CHARGE MONDIALE réelle (cas importés inclus) : aucun
# continent n'est à 0 % strict, car des cas importés (voyageurs) y surviennent.
# Chaque dict somme ~100. Maladie ABSENTE => estimation par population.
MALADIE_OMS = {
    # Europe ~0,1 % = cas importés (paludisme du voyageur), pas de transmission locale.
    "Paludisme":    {"Afrique": 94.9, "Asie": 2.5, "Amérique": 2.0, "Océanie": 0.5, "Europe": 0.1},
    "Tuberculose":  {"Asie": 58.0, "Afrique": 25.0, "Europe": 8.0, "Amérique": 8.0, "Océanie": 1.0},
    "VIH/SIDA":     {"Afrique": 67.0, "Asie": 18.0, "Amérique": 10.0, "Europe": 4.0, "Océanie": 1.0},
    "Dengue":       {"Asie": 70.0, "Amérique": 16.0, "Afrique": 9.0, "Océanie": 4.0, "Europe": 1.0},
    "Choléra":      {"Afrique": 60.0, "Asie": 35.0, "Amérique": 4.0, "Europe": 0.5, "Océanie": 0.5},
    "Typhoïde":     {"Asie": 70.0, "Afrique": 25.0, "Amérique": 4.0, "Europe": 0.5, "Océanie": 0.5},
    "Hépatite A":   {"Asie": 45.0, "Afrique": 35.0, "Amérique": 15.0, "Europe": 4.0, "Océanie": 1.0},
    "Hépatite B":   {"Asie": 60.0, "Afrique": 25.0, "Amérique": 8.0, "Europe": 6.0, "Océanie": 1.0},
    "Hépatite C":   {"Asie": 45.0, "Afrique": 20.0, "Europe": 20.0, "Amérique": 14.0, "Océanie": 1.0},
    "Rougeole":     {"Afrique": 50.0, "Asie": 40.0, "Amérique": 5.0, "Europe": 4.0, "Océanie": 1.0},
}


def _repartition_oms(nom_maladie: str) -> tuple[Optional[dict], str]:
    """
    Renvoie (répartition %, source) pour une maladie, par ordre de priorité :
      1. données OMS LIVE en cache (synchronisées depuis l'API GHO)  -> "OMS (live)"
      2. table OMS statique de référence si répertoriée               -> "OMS"
      3. AUCUNE donnée OMS pour cette maladie -> (None, "aucune").
    On n'invente PAS de répartition (plus d'estimation par population) : sans
    source OMS, la carte n'affiche aucun pourcentage.
    """
    # 1. Cache OMS d'actualité (mis à jour en arrière-plan au démarrage).
    try:
        from ..services.who_data_sync import get_cached_who_data
        live = get_cached_who_data().get(nom_maladie)
        if live:
            return {c: float(live.get(c, 0.0)) for c in CONTINENTS}, "OMS (live)"
    except Exception:
        pass
    # 2. Table OMS statique.
    if nom_maladie in MALADIE_OMS:
        return {c: MALADIE_OMS[nom_maladie].get(c, 0.0) for c in CONTINENTS}, "OMS"
    # 3. Pas de données OMS : ne rien afficher.
    return None, "aucune"


def _liste_maladies(db: Session) -> List[str]:
    """
    Liste complète des maladies du dataset/modèle (avec noms d'affichage
    normalisés, ex. "Malaria" -> "Paludisme"). Repli sur les maladies présentes
    en base si le modèle n'est pas chargé.
    """
    try:
        from ..ml.model_manager import model_manager, DISEASE_DISPLAY_NAMES
        classes = model_manager.get_model_info().get("classes", [])
        liste = sorted({DISEASE_DISPLAY_NAMES.get(str(c), str(c)) for c in classes})
        if liste:
            return liste
    except Exception:
        pass
    return [
        m[0] for m in db.query(Diagnostic.nom_maladie)
        .distinct().order_by(Diagnostic.nom_maladie).all()
    ]


@router.get("/diagnostics-par-continent")
def diagnostics_par_continent(
    maladie: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Dict:
    """
    Répartition géographique pour la carte du monde du dashboard.
    - `maladie` (optionnel) : restreint à une maladie précise.

    Les pourcentages par continent reflètent la distribution mondiale OMS de la
    maladie. Si AUCUNE donnée OMS n'existe pour la maladie, aucun pourcentage
    n'est renvoyé (source = "aucune"). Le `total` = cas RÉELS diagnostiqués.
    """
    # Cas réels diagnostiqués (pour le total).
    q = db.query(func.count(Diagnostic.diagnostic_id))
    if maladie:
        q = q.filter(Diagnostic.nom_maladie == maladie)
    total_cas = q.scalar() or 0

    # Répartition OMS : si une maladie est sélectionnée, sa distribution ; sinon
    # moyenne des distributions des maladies diagnostiquées QUI ONT des données OMS.
    if maladie:
        repartition, source = _repartition_oms(maladie)
    else:
        diag = db.query(Diagnostic.nom_maladie, func.count(Diagnostic.diagnostic_id)) \
                 .group_by(Diagnostic.nom_maladie).all()
        acc = {c: 0.0 for c in CONTINENTS}
        total_poids = 0
        for nom, nb in diag:
            rep, _ = _repartition_oms(nom)
            if rep is None:          # maladie sans données OMS : on l'ignore
                continue
            for c in CONTINENTS:
                acc[c] += rep[c] * nb
            total_poids += nb
        if total_poids:
            repartition = {c: acc[c] / total_poids for c in CONTINENTS}
            source = "OMS"
        else:
            repartition = None       # aucune maladie diagnostiquée n'a de donnée OMS
            source = "aucune"

    # Aucune donnée OMS : renvoyer une réponse vide (la carte n'affiche rien).
    if repartition is None:
        return {
            "maladie": maladie,
            "total": total_cas,
            "source": "aucune",
            "continents": [],
            "maladies": _liste_maladies(db),
        }

    somme = sum(repartition.values()) or 1.0
    maxpct = max(repartition.values()) or 1.0

    return {
        "maladie": maladie,
        "total": total_cas,        # cas RÉELS diagnostiqués (app)
        "source": source,          # "OMS", "OMS (live)" ou "aucune"
        "continents": [
            {
                "nom": c,
                # pourcentage = distribution mondiale OMS
                "pourcentage": round(repartition[c] / somme * 100, 1),
                # intensité (0–1) pour la couleur : poids OMS relatif du continent
                "intensite": round(repartition[c] / maxpct, 3),
            }
            for c in CONTINENTS
        ],
        "maladies": _liste_maladies(db),
    }


# ══════════════════════════════════════════════════════════════════════════════
#  GRAPHIQUES MATPLOTLIB
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/charts/top-diagnostics")
def chart_top_diagnostics(limit: int = 10, db: Session = Depends(get_db)):
    """
    Graphique matplotlib : barres horizontales des N maladies les plus diagnostiquées.
    Retourne { image: "<base64 PNG>" }
    """
    rows = db.query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.diagnostic_id).label("count")
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).order_by(
        func.count(Diagnostic.diagnostic_id).desc()
    ).limit(limit).all()

    if not rows:
        # Graphique vide élégant
        fig, ax = plt.subplots(figsize=(9, 5), facecolor=BG_COLOR)
        ax.set_facecolor(BG_COLOR)
        ax.text(0.5, 0.5, "Aucun diagnostic enregistré",
                ha="center", va="center", fontsize=14,
                color="#9CA3AF", transform=ax.transAxes)
        ax.axis("off")
        return {"image": _fig_to_b64(fig)}

    labels = [r.nom_maladie for r in rows][::-1]
    values = [r.count for r in rows][::-1]
    colors = [PALETTE_BARS[i % len(PALETTE_BARS)] for i in range(len(labels))][::-1]

    # Hauteur réduite de moitié (0.55 -> 0.28 par barre) : graphique plus compact,
    # toujours pleine largeur. min 2.2 au lieu de 4.
    fig, ax = plt.subplots(figsize=(9, max(2.2, len(labels) * 0.28)), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    bars = ax.barh(labels, values, color=colors, height=0.62, zorder=3)

    # Annotations de valeur à droite de chaque barre
    for bar, val in zip(bars, values):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f"{val}", va="center", ha="left",
                fontsize=10, fontweight="bold", color=TEXT_COLOR)

    ax.set_xlabel("Nombre de cas", fontsize=10, color="#6B7280", labelpad=8)
    ax.tick_params(axis="y", labelsize=10, colors=TEXT_COLOR)
    ax.tick_params(axis="x", labelsize=9, colors="#6B7280")
    ax.xaxis.grid(True, color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_xlim(0, max(values) * 1.2)
    fig.tight_layout(pad=1.5)

    return {"image": _fig_to_b64(fig)}


@router.get("/charts/statuts")
def chart_statuts(db: Session = Depends(get_db)):
    """
    Graphique matplotlib : donut chart répartition des diagnostics (Confirmés / Rejetés / Provisoires).
    Retourne { image: "<base64 PNG>" }
    """
    confirmes  = db.query(func.count(Diagnostic.diagnostic_id)).filter(Diagnostic.statut == "CONFIRMÉ").scalar()  or 0
    rejetes    = db.query(func.count(Diagnostic.diagnostic_id)).filter(Diagnostic.statut == "REJETÉ").scalar()    or 0
    provisoires = db.query(func.count(Diagnostic.diagnostic_id)).filter(Diagnostic.statut == "PROVISOIRE").scalar() or 0
    total = confirmes + rejetes + provisoires

    fig, ax = plt.subplots(figsize=(6, 5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    if total == 0:
        ax.text(0.5, 0.5, "Aucun diagnostic enregistré",
                ha="center", va="center", fontsize=13,
                color="#9CA3AF", transform=ax.transAxes)
        ax.axis("off")
        return {"image": _fig_to_b64(fig)}

    sizes  = [confirmes, rejetes, provisoires]
    labels = ["Confirmés", "Rejetés", "Provisoires"]
    colors = ["#10B981", "#EF4444", "#F59E0B"]
    explode = [0.04, 0.04, 0.04]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=None, colors=colors, explode=explode,
        autopct=lambda p: f"{p:.1f}%" if p > 2 else "",
        startangle=140, pctdistance=0.78,
        wedgeprops=dict(width=0.52, edgecolor="white", linewidth=2)
    )
    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("white")

    # Légende manuelle
    legend_patches = [
        mpatches.Patch(color=c, label=f"{l}  ({v})")
        for c, l, v in zip(colors, labels, sizes) if v > 0
    ]
    ax.legend(handles=legend_patches, loc="lower center",
              bbox_to_anchor=(0.5, -0.08), ncol=3,
              fontsize=10, frameon=False)

    # Texte central
    ax.text(0, 0, f"{total}\ndiag.", ha="center", va="center",
            fontsize=13, fontweight="bold", color=TEXT_COLOR)

    fig.tight_layout(pad=1.0)
    return {"image": _fig_to_b64(fig)}


@router.get("/charts/confiance")
def chart_confiance(db: Session = Depends(get_db)):
    """
    Graphique matplotlib : barres verticales — distribution de la certitude IA
    par tranches (0-33 %, 33-66 %, 66-100 %).
    Retourne { image: "<base64 PNG>" }
    """
    rows = db.query(Diagnostic.certitude).filter(
        Diagnostic.certitude.isnot(None)
    ).all()

    fig, ax = plt.subplots(figsize=(7, 4.5), facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)

    if not rows:
        ax.text(0.5, 0.5, "Aucune donnée de certitude",
                ha="center", va="center", fontsize=13,
                color="#9CA3AF", transform=ax.transAxes)
        ax.axis("off")
        return {"image": _fig_to_b64(fig)}

    values = [r.certitude * 100 for r in rows if r.certitude is not None]

    faible   = sum(1 for v in values if v < 33)
    moyenne  = sum(1 for v in values if 33 <= v < 66)
    elevee   = sum(1 for v in values if v >= 66)

    tranches = ["Faible\n(< 33 %)", "Moyenne\n(33–66 %)", "Élevée\n(≥ 66 %)"]
    counts   = [faible, moyenne, elevee]
    cols     = ["#EF4444", "#F59E0B", "#10B981"]

    bars = ax.bar(tranches, counts, color=cols, width=0.5, zorder=3,
                  edgecolor="white", linewidth=1.5)

    for bar, val in zip(bars, counts):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.15,
                    str(val), ha="center", va="bottom",
                    fontsize=12, fontweight="bold", color=TEXT_COLOR)

    ax.set_ylabel("Nombre de diagnostics", fontsize=10, color="#6B7280", labelpad=8)
    ax.tick_params(axis="x", labelsize=10, colors=TEXT_COLOR)
    ax.tick_params(axis="y", labelsize=9, colors="#6B7280")
    ax.yaxis.grid(True, color=GRID_COLOR, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_ylim(0, max(counts, default=1) * 1.25 + 1)
    fig.tight_layout(pad=1.5)
    return {"image": _fig_to_b64(fig)}
