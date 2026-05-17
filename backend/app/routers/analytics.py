"""
Analytics API Router (US-034, US-036, US-044)
Dashboard et statistiques
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, List
from datetime import datetime, timedelta
import io, base64

import matplotlib
matplotlib.use("Agg")          # pas d'interface graphique côté serveur
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

from ..database import get_db
from ..models import Patient, Consultation, Diagnostic, AnalyseIA, Medecin, Infirmier

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


@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)) -> Dict:
    """
    US-044: Dashboard avec statistiques globales
    """
    # KPI 1: Nombre total de patients
    total_patients = db.query(func.count(Patient.patient_id)).scalar()

    # KPI 2: Nombre de patients ce mois
    first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    patients_this_month = db.query(func.count(Patient.patient_id)).filter(
        Patient.created_at >= first_day_month
    ).scalar()
    
    # KPI 3: Nombre de consultations
    total_consultations = db.query(func.count(Consultation.consultation_id)).scalar()
    
    # KPI 3b: Consultations par statut
    consultations_en_attente = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "en attente"
    ).scalar() or 0
    
    consultations_en_cours = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "en cours"
    ).scalar() or 0
    
    consultations_terminees = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "terminée"
    ).scalar() or 0
    
    consultations_en_attente_medecin = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.statut == "en_attente_medecin"
    ).scalar() or 0
    
    # KPI 4: Nombre de diagnostics
    total_diagnostics = db.query(func.count(Diagnostic.diagnostic_id)).scalar() or 0

    # KPI 5: Taux d'approbation
    diagnostics_approuves = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    taux_approbation = (diagnostics_approuves / total_diagnostics * 100) if total_diagnostics > 0 else 0
    
    # KPI 6: Confiance moyenne (si la colonne existe)
    # Note: La table diagnostics utilise 'certitude' pas 'confiance'
    avg_confidence = db.query(func.avg(Diagnostic.certitude)).scalar() or 0
    
    # KPI 7: Consultations aujourd'hui
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    consultations_aujourd_hui = db.query(func.count(Consultation.consultation_id)).filter(
        Consultation.date_heure >= today_start,
        Consultation.date_heure <= today_end
    ).scalar() or 0
    
    # KPI 8: Diagnostics IA approuvés
    diagnostics_approuves = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "CONFIRMÉ"
    ).scalar() or 0
    
    # KPI 9: Diagnostics IA rejetés
    diagnostics_rejetes = db.query(func.count(Diagnostic.diagnostic_id)).filter(
        Diagnostic.statut == "REJETÉ"
    ).scalar() or 0
    
    # Tendance patients par jour (7 derniers jours)
    seven_days_ago = datetime.now() - timedelta(days=7)
    daily_patients = db.query(
        func.date(Patient.created_at).label('date'),
        func.count(Patient.patient_id).label('count')
    ).filter(
        Patient.created_at >= seven_days_ago
    ).group_by(func.date(Patient.created_at)).all()

    # Top 5 diagnostics (utiliser nom_maladie)
    top_diagnostics = db.query(
        Diagnostic.nom_maladie,
        func.count(Diagnostic.diagnostic_id).label('count')
    ).filter(
        Diagnostic.nom_maladie.isnot(None)
    ).group_by(Diagnostic.nom_maladie).order_by(
        func.count(Diagnostic.diagnostic_id).desc()
    ).limit(5).all()
    
    return {
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
def get_recent_consultations(limit: int = 10, db: Session = Depends(get_db)) -> List[Dict]:
    """
    Consultations récentes avec patient_id pour accès au dossier.
    Exclut les consultations orphelines (patient supprimé hors API).
    """
    consultations = (
        db.query(Consultation)
        .join(Patient, Consultation.patient_id == Patient.patient_id)
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

    fig, ax = plt.subplots(figsize=(9, max(4, len(labels) * 0.55)), facecolor=BG_COLOR)
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
