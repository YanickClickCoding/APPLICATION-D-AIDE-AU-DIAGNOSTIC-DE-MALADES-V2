"""
Diagnostic Pydantic schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class PredictionRequest(BaseModel):
    """Schema pour demander une prédiction (US-014)"""
    consultation_id: int
    # Les données seront extraites de la consultation


class AlternativeDiagnostic(BaseModel):
    """Diagnostic alternatif"""
    diagnostic: str
    confiance: float = Field(..., ge=0, le=1)


class PredictionResponse(BaseModel):
    """Schema pour retourner une prédiction (US-014, US-015)"""
    diagnostic_propose: str
    confiance: float = Field(..., ge=0, le=1, description="Score de confiance (0-1)")
    niveau_confiance: str = Field(..., pattern="^(high|medium|low)$")
    couleur_confiance: str = Field(..., pattern="^(green|yellow|red)$")
    diagnostics_alternatifs: List[AlternativeDiagnostic]
    temps_prediction_secondes: float
    timestamp: datetime
    
    # Explainabilité (US-016)
    explication: Optional[str] = None
    features_importantes: Optional[List[Dict[str, Any]]] = None


class DiagnosticCreate(BaseModel):
    """Schema pour créer un diagnostic après prédiction"""
    consultation_id: int
    diagnostic_propose: str
    confiance: float = Field(..., ge=0, le=1)
    niveau_confiance: str
    diagnostics_alternatifs: Optional[str] = None  # JSON string
    explication: Optional[str] = None


class DiagnosticApprove(BaseModel):
    """Schema pour approuver un diagnostic (US-020)"""
    medecin_id: int
    notes_medicales: Optional[str] = Field(None, max_length=2000)


class DiagnosticReject(BaseModel):
    """Schema pour rejeter un diagnostic (US-021)"""
    medecin_id: int
    diagnostic_correct: str = Field(..., min_length=1, max_length=200)
    raison_rejet: str = Field(..., pattern="^(trop_confiant|donnees_manquantes|autre)$")
    explication_medicale: Optional[str] = Field(None, max_length=2000)


class DiagnosticResponse(BaseModel):
    """Schema pour retourner un diagnostic"""
    id: UUID
    consultation_id: int
    diagnostic_propose: str
    confiance: float
    niveau_confiance: str
    statut: str
    diagnostic_final: Optional[str] = None
    approuve_par: Optional[int] = None
    date_approbation: Optional[datetime] = None
    notes_medicales: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
