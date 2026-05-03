"""
Consultation database model - Adapté au schéma MySQL existant
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, ENUM
from sqlalchemy.sql import func
from ..database import Base


class Consultation(Base):
    """Consultation model - corresponds to 'consultations' table"""
    
    __tablename__ = "consultations"
    
    # Primary Key
    consultation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Patient Info (simplifié dans la table actuelle)
    nom_patient = Column(String(200), nullable=False)
    
    # Consultation Info
    date_heure = Column(DateTime, nullable=False)
    motif = Column(Text, nullable=False)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"))
    statut = Column(
        ENUM('en attente', 'en cours', 'terminée'),
        default='en attente'
    )
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    medecin = relationship("Medecin", back_populates="consultations")
    symptomes = relationship("Symptome", back_populates="consultation", cascade="all, delete-orphan")
    signes_vitaux = relationship("SignesVitaux", back_populates="consultation", cascade="all, delete-orphan")
    examens = relationship("Examen", back_populates="consultation", cascade="all, delete-orphan")
    diagnostics = relationship("Diagnostic", back_populates="consultation", cascade="all, delete-orphan")
    analyses_ia = relationship("AnalyseIA", back_populates="consultation", cascade="all, delete-orphan")
    suivis = relationship("Suivi", back_populates="consultation")
    
    def __repr__(self):
        return f"<Consultation(id={self.consultation_id}, patient='{self.nom_patient}', statut='{self.statut}')>"
