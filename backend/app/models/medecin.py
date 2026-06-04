"""
Medecin database model - Adapté au schéma MySQL existant
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class Medecin(Base):
    """Medecin model - corresponds to 'medecins' table"""
    
    __tablename__ = "medecins"
    
    # Primary Key
    medecin_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Personal Information
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    specialite = Column(String(150), nullable=False)
    telephone = Column(String(20), nullable=False)
    disponible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    consultations = relationship("Consultation", back_populates="medecin")
    diagnostics = relationship("Diagnostic", back_populates="medecin")
    ordonnances = relationship("Ordonnance", back_populates="medecin")
    suivis = relationship("Suivi", back_populates="medecin")
    
    def __repr__(self):
        return f"<Medecin(id={self.medecin_id}, nom='{self.nom}', specialite='{self.specialite}')>"
