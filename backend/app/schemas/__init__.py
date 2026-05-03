"""
Pydantic schemas for request/response validation
"""
from .patient_schema import PatientCreate, PatientResponse, PatientUpdate
from .consultation_schema import (
    ConsultationCreate,
    ConsultationResponse,
    SymptomeInput,
    SignesVitauxInput
)
from .diagnostic_schema import (
    DiagnosticCreate,
    DiagnosticApprove,
    DiagnosticReject,
    DiagnosticResponse,
    PredictionRequest,
    PredictionResponse
)
from .user_schema import UserCreate, UserLogin, UserResponse, Token

__all__ = [
    "PatientCreate",
    "PatientResponse",
    "PatientUpdate",
    "ConsultationCreate",
    "ConsultationResponse",
    "SymptomeInput",
    "SignesVitauxInput",
    "DiagnosticCreate",
    "DiagnosticApprove",
    "DiagnosticReject",
    "DiagnosticResponse",
    "PredictionRequest",
    "PredictionResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token"
]
