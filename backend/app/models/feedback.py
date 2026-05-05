"""
Doctor Feedback Model
Feedback des médecins sur les prédictions ML
Requirement: 12.2
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class DoctorFeedback(Base):
    """
    Modèle pour le feedback des médecins sur les prédictions
    Permet d'évaluer la qualité des prédictions ML
    """
    __tablename__ = "doctor_feedback"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Relations
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False, index=True)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=False, index=True)
    prediction_id = Column(Integer, nullable=True)  # ID de la prédiction évaluée
    
    # Évaluation de qualité (1-5 étoiles)
    quality_rating = Column(Integer, nullable=False)  # 1=très mauvais, 5=excellent
    
    # Aspects spécifiques
    accuracy_rating = Column(Integer, nullable=True)  # Précision du diagnostic
    explainability_rating = Column(Integer, nullable=True)  # Clarté de l'explication
    usefulness_rating = Column(Integer, nullable=True)  # Utilité clinique
    
    # Commentaires textuels
    comments = Column(Text, nullable=True)
    
    # Suggestions d'amélioration
    suggestions = Column(Text, nullable=True)
    
    # Diagnostic suggéré par le médecin (si différent)
    suggested_diagnosis = Column(String(200), nullable=True)
    
    # Catégorie de feedback
    feedback_category = Column(String(50), nullable=True)  # positive, negative, neutral
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relations ORM
    consultation = relationship("Consultation", foreign_keys=[consultation_id])
    medecin = relationship("Medecin", foreign_keys=[medecin_id])
    
    def __repr__(self):
        return f"<DoctorFeedback(id={self.id}, quality={self.quality_rating}/5, medecin_id={self.medecin_id})>"
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "consultation_id": self.consultation_id,
            "medecin_id": self.medecin_id,
            "prediction_id": self.prediction_id,
            "quality_rating": self.quality_rating,
            "accuracy_rating": self.accuracy_rating,
            "explainability_rating": self.explainability_rating,
            "usefulness_rating": self.usefulness_rating,
            "comments": self.comments,
            "suggestions": self.suggestions,
            "suggested_diagnosis": self.suggested_diagnosis,
            "feedback_category": self.feedback_category,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
