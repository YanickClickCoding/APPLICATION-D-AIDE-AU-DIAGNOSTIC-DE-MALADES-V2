"""Ordonnance model"""
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..database import Base

class Ordonnance(Base):
    __tablename__ = "ordonnances"
    id = Column(CHAR(36), primary_key=True)
    traitement_id = Column(CHAR(36), ForeignKey("traitements.id"), nullable=False, unique=True)
    medecin_id = Column(CHAR(36), ForeignKey("medecins.medecin_id"), nullable=False)
    patient_id = Column(CHAR(36), ForeignKey("patients.id"), nullable=False)
    dossier_id = Column(CHAR(36), ForeignKey("dossiers_medicaux.id"), nullable=False)
    posologie_generale = Column(Text)
    date_emission = Column(DateTime, server_default=func.now())
    renouvelable = Column(Boolean, default=False)
    
    traitement = relationship("Traitement", back_populates="ordonnance")
    medecin = relationship("Medecin", back_populates="ordonnances")
    patient = relationship("Patient", back_populates="ordonnances")
    dossier_medical = relationship("DossierMedical", back_populates="ordonnances")
    medicaments = relationship("Medicament", back_populates="ordonnance", cascade="all, delete-orphan")
