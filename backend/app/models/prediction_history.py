"""
Prediction History Model
Historique des prédictions ML pour chaque patient
Requirement: 5.1
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class PredictionHistory(Base):
    """
    Modèle pour l'historique des prédictions ML
    Enregistre toutes les prédictions faites pour chaque patient
    """
    __tablename__ = "prediction_history"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Relations
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=True, index=True)
    
    # Prédiction
    predicted_disease = Column(String(200), nullable=False)
    confidence = Column(Float, nullable=False)  # Score de confiance (0-1)
    confidence_level = Column(String(50), nullable=True)  # 'HIGH', 'MEDIUM', 'LOW'
    
    # Probabilités pour toutes les classes
    prediction_probabilities = Column(JSON, nullable=True)  # {"Grippe": 0.85, "COVID-19": 0.10, ...}
    
    # Features utilisées pour la prédiction
    feature_values = Column(JSON, nullable=True)  # Valeurs des features au moment de la prédiction
    top_features = Column(JSON, nullable=True)  # Top 5 features importantes pour cette prédiction
    
    # Métadonnées du modèle
    model_version = Column(String(50), nullable=True)  # Version du modèle utilisé
    model_accuracy = Column(Float, nullable=True)  # Précision du modèle au moment de la prédiction
    
    # Validation médicale
    is_validated = Column(Integer, default=0)  # 0 = en attente, 1 = approuvé, -1 = rejeté
    validated_by = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    validation_notes = Column(Text, nullable=True)
    
    # Diagnostic réel (si différent de la prédiction)
    actual_disease = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations ORM
    patient = relationship("Patient", back_populates="prediction_history")
    consultation = relationship("Consultation", back_populates="prediction_history")
    validator = relationship("Medecin", foreign_keys=[validated_by])
    
    def __repr__(self):
        return f"<PredictionHistory(id={self.id}, patient_id={self.patient_id}, predicted={self.predicted_disease}, confidence={self.confidence:.2f})>"
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "consultation_id": self.consultation_id,
            "predicted_disease": self.predicted_disease,
            "confidence": self.confidence,
            "confidence_level": self.confidence_level,
            "prediction_probabilities": self.prediction_probabilities,
            "feature_values": self.feature_values,
            "top_features": self.top_features,
            "model_version": self.model_version,
            "model_accuracy": self.model_accuracy,
            "is_validated": self.is_validated,
            "validated_by": self.validated_by,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "validation_notes": self.validation_notes,
            "actual_disease": self.actual_disease,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
