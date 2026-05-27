"""Ordonnance model"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class Ordonnance(Base):
    __tablename__ = "ordonnances"
    ordonnance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    traitement_id = Column(Integer, ForeignKey("traitements.traitement_id"), nullable=False, unique=True)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=True)  # NULL si médecin non assigné
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    dossier_id = Column(Integer, ForeignKey("dossiers_medicaux.dossier_id"), nullable=False)
    posologie_generale = Column(Text)
    date_emission = Column(DateTime, server_default=func.now())
    renouvelable = Column(Boolean, default=False)
    
    traitement = relationship("Traitement", back_populates="ordonnance")
    medecin = relationship("Medecin", back_populates="ordonnances")
    patient = relationship("Patient", back_populates="ordonnances")
    dossier_medical = relationship("DossierMedical", back_populates="ordonnances")
    medicaments = relationship("Medicament", back_populates="ordonnance", cascade="all, delete-orphan")
