"""
ML Prediction API Router (US-014, US-015, US-016, US-020, US-021)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import json
import asyncio
from functools import partial

from ..database import get_db
from ..models import Consultation, Symptome, SignesVitaux, AnalyseIA, Diagnostic, Examen
from ..schemas.diagnostic_schema import (
    PredictionRequest,
    PredictionResponse,
    DiagnosticCreate,
    DiagnosticApprove,
    DiagnosticReject,
    DiagnosticResponse,
    DirectPredictionRequest,
)
from ..ml.model_manager import model_manager
from .auth import get_current_user, get_current_non_admin

router = APIRouter(
    prefix="/ml",
    tags=["ML Prediction"],
    dependencies=[Depends(get_current_user)],
)

# Router public séparé — pas de dépendance auth (symptomes, synonymes, antecedents)
public_router = APIRouter(
    prefix="/ml",
    tags=["ML Public"],
)


def extract_patient_data(consultation_id: int, db: Session) -> Dict:
    """
    Extrait les données de consultation et les formate dans la structure
    attendue par model_manager.predict() / _build_feature_vector().

    Retourne:
    {
        "age": int,
        "duree_symptomes_jours": int,
        "sexe": "M" | "F",
        "severite": "LEGER" | "MODERE" | "SEVERE",
        "vitaux": { ... },
        "symptomes": [list of str],
        "examens": [{"nom": str, "valeur_numerique": float, "unite_mesure": str}]
    }
    """
    # --- Consultation ---
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == consultation_id
    ).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée",
        )

    # --- Symptômes ---
    symptomes = db.query(Symptome).filter(
        Symptome.consultation_id == str(consultation_id)
    ).all()

    symptome_names = [s.nom for s in symptomes if s.nom]

    # Durée maximale des symptômes déclarés
    durees = [s.duree_jours for s in symptomes if s.duree_jours]
    duree_symptomes = max(durees) if durees else 7

    # Sévérité globale (prend la plus grave)
    sev_order = {"SEVERE": 3, "MODERE": 2, "LEGER": 1}
    severites = [s.severite for s in symptomes if s.severite and s.severite in sev_order]
    if severites:
        severite = max(severites, key=lambda s: sev_order.get(s, 0))
    else:
        severite = "MODERE"

    # --- Signes vitaux ---
    signes = db.query(SignesVitaux).filter(
        SignesVitaux.consultation_id == str(consultation_id)
    ).first()

    vitaux = {}
    if signes:
        vitaux = {
            "tension_systolique":    signes.tension_systolique,
            "tension_diastolique":   signes.tension_diastolique,
            "frequence_cardiaque":   signes.frequence_cardiaque,
            "frequence_respiratoire": signes.frequence_respiratoire,
            "temperature":           signes.temperature,
            "saturation_oxygene":    signes.saturation_oxygene,
            "imc":                   signes.imc,
        }

    # --- Examens biologiques ---
    examens_db = db.query(Examen).filter(
        Examen.consultation_id == str(consultation_id),
        Examen.type == "BIOLOGIE",
    ).all()

    examens = [
        {
            "nom":              e.nom,
            "valeur_numerique": e.valeur_numerique,
            "unite_mesure":     e.unite_mesure or "",
        }
        for e in examens_db
        if e.valeur_numerique is not None
    ]

    # --- Âge --- (la table consultations ne stocke pas directement l'âge/patient)
    age = 40  # valeur par défaut raisonnable

    return {
        "age":                  age,
        "duree_symptomes_jours": duree_symptomes,
        "sexe":                 "M",   # À améliorer si un lien patient est ajouté
        "severite":             severite,
        "vitaux":               vitaux,
        "symptomes":            symptome_names,
        "examens":              examens,
    }


@router.post("/predict", response_model=PredictionResponse)
async def predict_diagnosis(request: PredictionRequest, db: Session = Depends(get_db), _=Depends(get_current_non_admin)):
    """
    US-014, US-015: Prédire le diagnostic pour une consultation
    """
    if not model_manager.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML non chargé. Veuillez entraîner ou charger un modèle.",
        )

    consultation_data = extract_patient_data(request.consultation_id, db)

    # Exécution dans un thread pool pour ne pas bloquer la boucle asyncio
    loop = asyncio.get_event_loop()
    prediction = await loop.run_in_executor(None, model_manager.predict, consultation_data)

    # Enregistrer l'analyse IA
    db_analyse = AnalyseIA(
        consultation_id=request.consultation_id,
        diagnostic_propose=prediction["diagnostic_propose"],
        confiance=prediction["confiance"],
        diagnostics_alternatifs=json.dumps(
            prediction["diagnostics_alternatifs"], ensure_ascii=False
        ),
    )
    db.add(db_analyse)
    db.commit()

    return prediction


@router.post("/predict-direct", response_model=PredictionResponse)
async def predict_direct(request: DirectPredictionRequest, _=Depends(get_current_non_admin)):
    """
    Prédiction directe à partir des données brutes du formulaire,
    sans enregistrement préalable en base de données.
    """
    if not model_manager.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML non chargé. Veuillez entraîner ou charger un modèle.",
        )

    consultation_data = {
        "age":                   request.age,
        "duree_symptomes_jours": request.duree_symptomes_jours,
        "sexe":                  request.sexe,
        "severite":              request.severite,
        "vitaux":                request.vitaux,
        "symptomes":             request.symptomes,
        "examens": [
            {
                "nom":              e.nom,
                "valeur_numerique": e.valeur_numerique,
                "unite_mesure":     e.unite_mesure or "",
            }
            for e in request.examens
            if e.valeur_numerique is not None
        ],
        "antecedents_personnels": request.antecedents_personnels,
        "antecedents_familiaux":  request.antecedents_familiaux,
        "allergies":              request.allergies,
    }

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model_manager.predict, consultation_data)


@router.post("/explain", response_model=Dict)
async def explain_diagnosis(request: PredictionRequest, db: Session = Depends(get_db), _=Depends(get_current_non_admin)):
    """
    US-016: Expliquer pourquoi ce diagnostic a été proposé
    """
    if not model_manager.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML non chargé",
        )

    consultation_data = extract_patient_data(request.consultation_id, db)
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, model_manager.explain_prediction, consultation_data)


@router.post("/diagnostics", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostic(diagnostic: DiagnosticCreate, db: Session = Depends(get_db), _=Depends(get_current_non_admin)):
    """Créer un diagnostic après prédiction"""
    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == diagnostic.consultation_id
    ).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée",
        )

    db_diagnostic = Diagnostic(
        consultation_id=diagnostic.consultation_id,
        diagnostic_propose=diagnostic.diagnostic_propose,
        confiance=diagnostic.confiance,
        niveau_confiance=diagnostic.niveau_confiance,
        diagnostics_alternatifs=diagnostic.diagnostics_alternatifs,
        explication=diagnostic.explication,
        statut="en_attente",
    )
    db.add(db_diagnostic)
    db.commit()
    db.refresh(db_diagnostic)

    return db_diagnostic


@router.post("/diagnostics/{diagnostic_id}/approve", response_model=DiagnosticResponse)
def approve_diagnostic(
    diagnostic_id: str,
    approval: DiagnosticApprove,
    db: Session = Depends(get_db),
    _=Depends(get_current_non_admin),
):
    """US-020: Approuver un diagnostic proposé par l'IA"""
    from uuid import UUID

    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == UUID(diagnostic_id)).first()
    if not diagnostic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic non trouvé")

    if diagnostic.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diagnostic déjà {diagnostic.statut}",
        )

    from datetime import datetime

    diagnostic.statut = "approuve"
    diagnostic.diagnostic_final = diagnostic.diagnostic_propose
    diagnostic.approuve_par = approval.medecin_id
    diagnostic.date_approbation = datetime.now()
    diagnostic.notes_medicales = approval.notes_medicales

    consultation = db.query(Consultation).filter(
        Consultation.consultation_id == diagnostic.consultation_id
    ).first()
    if consultation:
        consultation.statut = "terminée"

    db.commit()
    db.refresh(diagnostic)

    return diagnostic


@router.post("/diagnostics/{diagnostic_id}/reject", response_model=DiagnosticResponse)
def reject_diagnostic(
    diagnostic_id: str,
    rejection: DiagnosticReject,
    db: Session = Depends(get_db),
    _=Depends(get_current_non_admin),
):
    """US-021: Rejeter un diagnostic et proposer le diagnostic correct"""
    from uuid import UUID

    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == UUID(diagnostic_id)).first()
    if not diagnostic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Diagnostic non trouvé")

    if diagnostic.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diagnostic déjà {diagnostic.statut}",
        )

    from datetime import datetime

    diagnostic.statut = "rejete"
    diagnostic.diagnostic_final = rejection.diagnostic_correct
    diagnostic.approuve_par = rejection.medecin_id
    diagnostic.date_approbation = datetime.now()
    diagnostic.raison_rejet = rejection.raison_rejet
    diagnostic.notes_medicales = rejection.explication_medicale

    db.commit()
    db.refresh(diagnostic)

    return diagnostic


@router.get("/model/info")
def get_model_info():
    """Informations sur le modèle chargé"""
    return model_manager.get_model_info()


@public_router.get("/synonymes")
def get_synonymes():
    """
    Retourne le dictionnaire synonymes → terme canonique.
    Utilisé par le frontend pour la recherche bidirectionnelle dans le dropdown.
    Merge dictionnaire statique + custom admin.
    """
    from ..ml.model_manager import SYNONYMES_SYMPTOMES, ModelManager
    custom = ModelManager._charger_synonymes_custom()
    merged = {**custom, **SYNONYMES_SYMPTOMES}
    # Construire la carte inverse : canonique → [synonymes]
    inverse: dict[str, list[str]] = {}
    for syn, canonique in merged.items():
        inverse.setdefault(canonique, []).append(syn)
    return {"synonymes": merged, "inverse": inverse, "total": len(merged)}


@public_router.get("/symptomes")
def get_symptomes_list():
    """
    Retourne tous les symptômes connus du modèle ML — sans authentification requise.
    Lit d'abord le cache JSON (mis à jour après chaque entraînement), sinon calcule depuis le modèle.
    """
    import os as _os

    _CACHE = "./ml_models/symptomes_cache.json"
    # Essayer plusieurs chemins pour le cache
    cache_candidates = [_CACHE, "../ml_models/symptomes_cache.json",
        _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))),
                      "..", "ml_models", "symptomes_cache.json")]
    for path in cache_candidates:
        if _os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                return {"symptomes": data["symptomes"], "total": data["total"],
                        "updated_at": data.get("updated_at"), "source": "cache"}
            except Exception:
                break

    # Fallback : calculer depuis le modèle en mémoire
    if not model_manager.model_loaded or not model_manager.trainer.feature_names:
        return {"symptomes": [], "total": 0}

    def fix_mojibake(s: str) -> str:
        try:
            return s.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return s

    symptomes = sorted({
        fix_mojibake(feat[8:].replace("_", " "))
        for feat in model_manager.trainer.feature_names
        if feat.startswith("symptom_")
    })
    return {"symptomes": symptomes, "total": len(symptomes), "source": "model"}


@public_router.get("/antecedents")
def get_antecedents_list():
    """
    Retourne :
    - maladies  : les 122+ maladies du modèle ML (pour antécédents perso/familiaux)
    - allergenes: liste standardisée d'allergènes médicaux et environnementaux
    Sans authentification requise.
    """
    # Maladies du modèle (antécédents)
    if model_manager.model_loaded and model_manager.predictor:
        maladies = sorted(model_manager.predictor.label_encoder.classes_.tolist())
    else:
        maladies = []

    # Allergènes standardisés (médicaments + environnement + alimentaire)
    allergenes = sorted([
        # Médicaments
        "Amoxicilline", "Ampicilline", "Aspirine", "Atropine",
        "Carbamazépine", "Ciprofloxacine", "Codéine",
        "Diclofénac", "Érythromycine",
        "Ibuprofène", "Iode (produit de contraste)",
        "Kétoprofène", "Latex",
        "Méthotrexate", "Morphine",
        "Naproxène", "AINS (anti-inflammatoires non stéroïdiens)",
        "Pénicilline", "Phénobarbital", "Phénytoïne",
        "Quinolones", "Rifampicine",
        "Streptomycine", "Sulfamides", "Sulfonamides",
        "Tétracyclines",
        # Environnement
        "Acariens", "Abeilles (venin)", "Blattes",
        "Guêpes (venin)",
        "Moisissures", "Nickel",
        "Plumes d'oiseaux", "Pollens de graminées", "Pollens d'arbres",
        "Poils de chat", "Poils de chien", "Poils d'animaux",
        # Alimentaire
        "Arachides", "Céleri", "Crustacés",
        "Fruits à coque", "Fruits de mer",
        "Gluten (céréales)", "Graines de sésame",
        "Lait de vache", "Lupin",
        "Moutarde", "Mollusques",
        "Noix", "Œufs", "Poisson", "Soja",
    ])

    return {
        "maladies": maladies,
        "allergenes": allergenes,
        "total_maladies": len(maladies),
        "total_allergenes": len(allergenes),
    }
