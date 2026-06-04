"""Suivi model"""
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base

class Suivi(Base):
    __tablename__ = "suivis"
    suivi_id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"))
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.diagnostic_id"))
    traitement_id = Column(Integer, ForeignKey("traitements.traitement_id"))
    dossier_id = Column(Integer, ForeignKey("dossiers_medicaux.dossier_id"), nullable=False)
    numero_suivi = Column(String(50), nullable=False, unique=True)
    date_suivi = Column(Date, nullable=False)
    etat_general = Column(ENUM('EXCELLENT', 'BON', 'STABLE', 'DECLINE', 'CRITIQUE'))
    amelioration = Column(ENUM('EXCELLENTE', 'BON', 'MOYEN', 'MAUVAIS', 'DECLINE'))
    pourcentage_amelioration = Column(Float)
    adherence_traitement = Column(Float)
    statut = Column(ENUM('EN_COURS', 'TERMINE_SUCCES', 'TERMINE_ECHEC', 'A_REPRENDRE'), default='EN_COURS')
    prochaine_consultation = Column(Date)
    
    patient = relationship("Patient", back_populates="suivis")
    medecin = relationship("Medecin", back_populates="suivis")
    consultation = relationship("Consultation", back_populates="suivis")
    diagnostic = relationship("Diagnostic", back_populates="suivis")
    traitement = relationship("Traitement", back_populates="suivis")
    dossier_medical = relationship("DossierMedical", back_populates="suivis")
