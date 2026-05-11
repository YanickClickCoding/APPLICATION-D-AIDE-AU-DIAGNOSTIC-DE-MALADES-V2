"""
Patients API Router (US-001, US-004)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..database import get_db
from ..models import Patient
from ..schemas.patient_schema import PatientCreate, PatientResponse, PatientUpdate

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(patient: PatientCreate, db: Session = Depends(get_db)):
    """
    US-001: Enregistrement d'un nouveau patient
    """
    # Vérifier si le patient existe déjà (par numéro sécu)
    if patient.numero_securite_sociale:
        existing = db.query(Patient).filter(
            Patient.numero_securite_sociale == patient.numero_securite_sociale
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un patient avec ce numéro de sécurité sociale existe déjà"
            )
    
    # Créer le patient
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    
    return db_patient


@router.get("", response_model=List[PatientResponse])
def list_patients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Liste tous les patients
    """
    patients = db.query(Patient).offset(skip).limit(limit).all()
    return patients


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Récupère un patient par son ID (INT)
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db)
):
    """
    Met à jour un patient
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Mettre à jour les champs
    update_data = patient_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(patient, field, value)
    
    db.commit()
    db.refresh(patient)
    
    return patient


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    Supprime un patient et toutes ses données associées (consultations, dossier médical, etc.)
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient non trouvé"
        )
    
    # Récupérer le nom pour le message de confirmation
    nom_complet = f"{patient.prenoms} {patient.nom}"
    
    # Supprimer le patient (les consultations et autres données seront supprimées en cascade)
    db.delete(patient)
    db.commit()
    
    return {
        "success": True,
        "message": f"Patient {nom_complet} et toutes ses données associées ont été supprimés"
    }
