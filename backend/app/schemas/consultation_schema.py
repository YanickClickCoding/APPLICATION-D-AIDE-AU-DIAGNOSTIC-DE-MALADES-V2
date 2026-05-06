"""
Consultation Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class SymptomeInput(BaseModel):
    """Schema pour saisir un symptôme (US-002)"""
    nom: str = Field(..., description="Nom du symptôme (fievre, toux, mal_gorge, etc.)")
    present: bool = Field(..., description="Le symptôme est-il présent?")
    severite: Optional[str] = Field(None, pattern="^(leger|modere|grave)$", description="Sévérité si présent")
    duree_jours: Optional[int] = Field(None, ge=0, description="Depuis combien de jours?")


class SignesVitauxInput(BaseModel):
    """Schema pour saisir les signes vitaux (US-003)"""
    saturation_o2: Optional[float] = Field(None, ge=70, le=100, description="Saturation O2 (%)")
    frequence_cardiaque: Optional[int] = Field(None, ge=40, le=200, description="Fréquence cardiaque (bpm)")
    temperature: Optional[float] = Field(None, ge=35.0, le=42.0, description="Température (°C)")
    tension_arterielle_systolique: Optional[int] = Field(None, ge=70, le=250, description="Tension systolique (mmHg)")
    tension_arterielle_diastolique: Optional[int] = Field(None, ge=40, le=150, description="Tension diastolique (mmHg)")
    poids: Optional[float] = Field(None, ge=0, le=300, description="Poids (kg)")
    taille: Optional[float] = Field(None, ge=0, le=250, description="Taille (cm)")


class ConsultationCreate(BaseModel):
    """Schema pour créer une consultation"""
    patient_id: UUID
    medecin_id: int
    motif: str = Field(..., min_length=1, max_length=500)
    symptomes: List[SymptomeInput] = Field(..., min_items=1, description="Au moins 1 symptôme requis")
    signes_vitaux: SignesVitauxInput
    antecedents: Optional[str] = Field(None, max_length=1000)
    allergies: Optional[str] = Field(None, max_length=500)


class ConsultationResponse(BaseModel):
    """Schema pour retourner une consultation"""
    consultation_id: int
    patient_id: Optional[int] = None  # INT, peut être null
    nom_patient: str
    date_heure: datetime
    motif: str
    statut: str
    medecin_id: Optional[int] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
