"""
DossierMedical database model
"""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..database import Base


class DossierMedical(Base):
    """DossierMedical model - corresponds to 'dossiers_medicaux' table"""
    
    __tablename__ = "dossiers_medicaux"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Foreign Key
    patient_id = Column(CHAR(36), ForeignKey("patients.id"), nullable=False, unique=True)
    
    # Medical Record Info
    numero_dossier = Column(String(50), nullable=False, unique=True)
    antecedents_familiaux = Column(Text)
    antecedents_personnels = Column(Text)
    allergies = Column(Text)
    
    # Timestamp
    date_creation = Column(DateTime, server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="dossier_medical")
    diagnostics = relationship("Diagnostic", back_populates="dossier_medical")
    ordonnances = relationship("Ordonnance", back_populates="dossier_medical")
    suivis = relationship("Suivi", back_populates="dossier_medical")
    
    def __repr__(self):
        return f"<DossierMedical(id={self.id}, numero='{self.numero_dossier}')>"
