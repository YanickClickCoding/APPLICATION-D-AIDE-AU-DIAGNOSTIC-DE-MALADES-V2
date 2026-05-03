"""
Patient Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime
from uuid import UUID


class PatientBase(BaseModel):
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    date_naissance: date
    sexe: str = Field(..., pattern="^(M|F)$")
    numero_securite_sociale: Optional[str] = Field(None, max_length=15)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    adresse: Optional[str] = Field(None, max_length=255)
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)


class PatientCreate(PatientBase):
    """Schema pour créer un patient (US-001)"""
    pass


class PatientUpdate(BaseModel):
    """Schema pour mettre à jour un patient"""
    nom: Optional[str] = Field(None, min_length=1, max_length=100)
    prenom: Optional[str] = Field(None, min_length=1, max_length=100)
    telephone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    adresse: Optional[str] = Field(None, max_length=255)
    ville: Optional[str] = Field(None, max_length=100)
    code_postal: Optional[str] = Field(None, max_length=10)


class PatientResponse(PatientBase):
    """Schema pour retourner un patient"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
