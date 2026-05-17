"""
Patient Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class DossierMedicalInfo(BaseModel):
    dossier_id: int
    numero_dossier: str
    antecedents_familiaux: Optional[str] = None
    antecedents_personnels: Optional[str] = None
    allergies: Optional[str] = None

    class Config:
        from_attributes = True


class PatientBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenoms: str = Field(..., min_length=1, max_length=150)
    date_naissance: date
    sexe: str = Field(..., pattern="^(M|F)$")
    groupe_sanguin: Optional[str] = None
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    adresse: Optional[str] = None


class PatientCreate(PatientBase):
    """Schema pour créer un patient (US-001)"""
    pass


class PatientUpdate(BaseModel):
    """Schema pour mettre à jour un patient"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenoms: Optional[str] = Field(None, min_length=1, max_length=150)
    date_naissance: Optional[date] = None
    sexe: Optional[str] = Field(None, pattern="^(M|F)$")
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = None
    adresse: Optional[str] = None
    groupe_sanguin: Optional[str] = None


class PatientResponse(PatientBase):
    """Schema pour retourner un patient"""
    patient_id: int  # INT AUTO_INCREMENT
    created_at: datetime
    # Pas de min_length sur la réponse — la BDD peut contenir des valeurs vides
    nom: str = Field(..., max_length=100)
    prenoms: str = Field(..., max_length=150)
    dossier_medical: Optional[DossierMedicalInfo] = None

    class Config:
        from_attributes = True
