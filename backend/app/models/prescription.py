"""
Prescription Model
Modèle pour les prescriptions médicales avec contre-indications
Requirement: 6.5
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Prescription(Base):
    """
    Modèle pour les prescriptions médicales
    Gère les médicaments, contre-indications et signatures électroniques
    """
    __tablename__ = "prescriptions"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Relations
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False, index=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=True, index=True)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=False, index=True)
    
    # Diagnostic associé
    diagnostic = Column(String(200), nullable=False)
    
    # Médicaments prescrits (JSON array)
    # Format: [{"nom": "Paracétamol", "dosage": "500mg", "frequence": "3x/jour", "duree": "7 jours"}]
    medications = Column(JSON, nullable=False)
    
    # Contre-indications détectées (JSON array)
    # Format: [{"type": "allergie", "substance": "Pénicilline", "severity": "HIGH"}]
    contraindications = Column(JSON, nullable=True)
    
    # Allergies du patient (JSON array)
    patient_allergies = Column(JSON, nullable=True)
    
    # Interactions médicamenteuses détectées (JSON array)
    drug_interactions = Column(JSON, nullable=True)
    
    # Avertissements et alertes
    warnings = Column(JSON, nullable=True)  # Liste d'avertissements
    has_critical_warning = Column(Boolean, default=False)  # Alerte critique
    
    # Instructions spéciales
    special_instructions = Column(Text, nullable=True)
    
    # Signature électronique
    is_signed = Column(Boolean, default=False)
    signed_by = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=True)
    signed_at = Column(DateTime, nullable=True)
    signature_hash = Column(String(256), nullable=True)  # Hash de la signature
    
    # Statut
    status = Column(String(50), default="draft")  # draft, signed, delivered, cancelled
    
    # Notes médicales
    medical_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    delivered_at = Column(DateTime, nullable=True)
    
    # Relations ORM
    patient = relationship("Patient", foreign_keys=[patient_id])
    consultation = relationship("Consultation", foreign_keys=[consultation_id])
    medecin = relationship("Medecin", foreign_keys=[medecin_id])
    signer = relationship("Medecin", foreign_keys=[signed_by])
    
    def __repr__(self):
        return f"<Prescription(id={self.id}, patient_id={self.patient_id}, diagnostic={self.diagnostic}, status={self.status})>"
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "patient_id": self.patient_id,
            "consultation_id": self.consultation_id,
            "medecin_id": self.medecin_id,
            "diagnostic": self.diagnostic,
            "medications": self.medications,
            "contraindications": self.contraindications,
            "patient_allergies": self.patient_allergies,
            "drug_interactions": self.drug_interactions,
            "warnings": self.warnings,
            "has_critical_warning": self.has_critical_warning,
            "special_instructions": self.special_instructions,
            "is_signed": self.is_signed,
            "signed_by": self.signed_by,
            "signed_at": self.signed_at.isoformat() if self.signed_at else None,
            "signature_hash": self.signature_hash,
            "status": self.status,
            "medical_notes": self.medical_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None
        }
