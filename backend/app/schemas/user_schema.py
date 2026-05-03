"""
User Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    """Schema pour créer un utilisateur"""
    nom: str = Field(..., min_length=1, max_length=100)
    prenom: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    mot_de_passe: str = Field(..., min_length=8, max_length=100)
    role: str = Field(..., pattern="^(admin|medecin|infirmier)$")


class UserLogin(BaseModel):
    """Schema pour login"""
    email: EmailStr
    mot_de_passe: str


class UserResponse(BaseModel):
    """Schema pour retourner un utilisateur"""
    id: int
    nom: str
    prenom: str
    email: str
    role: str
    actif: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema pour retourner un token JWT"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
