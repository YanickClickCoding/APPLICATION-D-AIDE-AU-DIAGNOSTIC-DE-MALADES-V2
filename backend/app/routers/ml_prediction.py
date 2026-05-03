"""
ML Prediction API Router (US-014, US-015, US-016, US-020, US-021)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import json

from ..database import get_db
from ..models import Consultation, Symptome, SignesVitaux, AnalyseIA, Diagnostic
from ..schemas.diagnostic_schema import (
    PredictionRequest,
    PredictionResponse,
    DiagnosticCreate,
    DiagnosticApprove,
    DiagnosticReject,
    DiagnosticResponse
)
from ..ml.model_manager import model_manager

router = APIRouter(prefix="/ml", tags=["ML Prediction"])


def extract_patient_data(consultation_id: int, db: Session) -> Dict:
    """
    Extrait les données du patient depuis la consultation
    """
    # Récupérer la consultation
    consultation = db.query(Consultation).filter(Consultation.id == consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    
    # Récupérer les symptômes
    symptomes = db.query(Symptome).filter(Symptome.consultation_id == consultation_id).all()
    
    # Récupérer les signes vitaux
    signes = db.query(SignesVitaux).filter(SignesVitaux.consultation_id == consultation_id).first()
    
    # Construire le dictionnaire de données
    patient_data = {}
    
    # Symptômes (binaires)
    symptome_names = ['fievre', 'toux', 'mal_gorge', 'fatigue_musculaire', 'mal_tete', 'difficulte_respiration']
    for name in symptome_names:
        symptome = next((s for s in symptomes if s.nom == name), None)
        patient_data[name] = 1 if (symptome and symptome.present) else 0
    
    # Signes vitaux
    if signes:
        patient_data['saturation_o2'] = signes.saturation_o2 or 98.0
        patient_data['frequence_cardiaque'] = signes.frequence_cardiaque or 75
        patient_data['temperature'] = signes.temperature or 37.0
        patient_data['tension_arterielle_systolique'] = signes.tension_arterielle_systolique or 120
        patient_data['tension_arterielle_diastolique'] = signes.tension_arterielle_diastolique or 80
    else:
        # Valeurs par défaut
        patient_data['saturation_o2'] = 98.0
        patient_data['frequence_cardiaque'] = 75
        patient_data['temperature'] = 37.0
        patient_data['tension_arterielle_systolique'] = 120
        patient_data['tension_arterielle_diastolique'] = 80
    
    # Âge (calculé depuis date de naissance du patient)
    if consultation.patient and consultation.patient.date_naissance:
        from datetime import date
        today = date.today()
        age = today.year - consultation.patient.date_naissance.year
        patient_data['age'] = age
    else:
        patient_data['age'] = 40  # Valeur par défaut
    
    return patient_data


@router.post("/predict", response_model=PredictionResponse)
def predict_diagnosis(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    US-014, US-015: Prédire le diagnostic pour une consultation
    """
    # Vérifier que le modèle est chargé
    if not model_manager.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML non chargé. Veuillez entraîner ou charger un modèle."
        )
    
    # Extraire les données du patient
    patient_data = extract_patient_data(request.consultation_id, db)
    
    # Faire la prédiction
    prediction = model_manager.predict(patient_data)
    
    # Enregistrer l'analyse IA
    db_analyse = AnalyseIA(
        consultation_id=request.consultation_id,
        diagnostic_propose=prediction["diagnostic_propose"],
        confiance=prediction["confiance"],
        diagnostics_alternatifs=json.dumps(prediction["diagnostics_alternatifs"], ensure_ascii=False)
    )
    db.add(db_analyse)
    db.commit()
    
    return prediction


@router.post("/explain", response_model=Dict)
def explain_diagnosis(request: PredictionRequest, db: Session = Depends(get_db)):
    """
    US-016: Expliquer pourquoi ce diagnostic a été proposé
    """
    if not model_manager.model_loaded:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Modèle ML non chargé"
        )
    
    # Extraire les données
    patient_data = extract_patient_data(request.consultation_id, db)
    
    # Obtenir l'explication
    explanation = model_manager.explain_prediction(patient_data)
    
    return explanation


@router.post("/diagnostics", response_model=DiagnosticResponse, status_code=status.HTTP_201_CREATED)
def create_diagnostic(diagnostic: DiagnosticCreate, db: Session = Depends(get_db)):
    """
    Créer un diagnostic après prédiction
    """
    # Vérifier que la consultation existe
    consultation = db.query(Consultation).filter(Consultation.id == diagnostic.consultation_id).first()
    if not consultation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consultation non trouvée"
        )
    
    # Créer le diagnostic
    db_diagnostic = Diagnostic(
        consultation_id=diagnostic.consultation_id,
        diagnostic_propose=diagnostic.diagnostic_propose,
        confiance=diagnostic.confiance,
        niveau_confiance=diagnostic.niveau_confiance,
        diagnostics_alternatifs=diagnostic.diagnostics_alternatifs,
        explication=diagnostic.explication,
        statut="en_attente"
    )
    db.add(db_diagnostic)
    db.commit()
    db.refresh(db_diagnostic)
    
    return db_diagnostic


@router.post("/diagnostics/{diagnostic_id}/approve", response_model=DiagnosticResponse)
def approve_diagnostic(
    diagnostic_id: str,
    approval: DiagnosticApprove,
    db: Session = Depends(get_db)
):
    """
    US-020: Approuver un diagnostic proposé par l'IA
    """
    from uuid import UUID
    
    # Récupérer le diagnostic
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == UUID(diagnostic_id)).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic non trouvé"
        )
    
    # Vérifier qu'il n'est pas déjà approuvé/rejeté
    if diagnostic.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diagnostic déjà {diagnostic.statut}"
        )
    
    # Approuver
    from datetime import datetime
    diagnostic.statut = "approuve"
    diagnostic.diagnostic_final = diagnostic.diagnostic_propose
    diagnostic.approuve_par = approval.medecin_id
    diagnostic.date_approbation = datetime.now()
    diagnostic.notes_medicales = approval.notes_medicales
    
    # Mettre à jour le statut de la consultation
    consultation = db.query(Consultation).filter(Consultation.id == diagnostic.consultation_id).first()
    if consultation:
        consultation.statut = "terminee"
    
    db.commit()
    db.refresh(diagnostic)
    
    return diagnostic


@router.post("/diagnostics/{diagnostic_id}/reject", response_model=DiagnosticResponse)
def reject_diagnostic(
    diagnostic_id: str,
    rejection: DiagnosticReject,
    db: Session = Depends(get_db)
):
    """
    US-021: Rejeter un diagnostic et proposer le diagnostic correct
    """
    from uuid import UUID
    
    # Récupérer le diagnostic
    diagnostic = db.query(Diagnostic).filter(Diagnostic.id == UUID(diagnostic_id)).first()
    if not diagnostic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagnostic non trouvé"
        )
    
    # Vérifier qu'il n'est pas déjà approuvé/rejeté
    if diagnostic.statut != "en_attente":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Diagnostic déjà {diagnostic.statut}"
        )
    
    # Rejeter
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
    """
    Informations sur le modèle chargé
    """
    return model_manager.get_model_info()
