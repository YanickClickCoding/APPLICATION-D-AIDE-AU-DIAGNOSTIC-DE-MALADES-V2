"""Suivi model"""
from sqlalchemy import Column, String, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, ENUM
from ..database import Base

class Suivi(Base):
    __tablename__ = "suivis"
    id = Column(CHAR(36), primary_key=True)
    patient_id = Column(CHAR(36), ForeignKey("patients.id"), nullable=False)
    medecin_id = Column(CHAR(36), ForeignKey("medecins.medecin_id"), nullable=False)
    consultation_id = Column(CHAR(36), ForeignKey("consultations.consultation_id"))
    diagnostic_id = Column(CHAR(36), ForeignKey("diagnostics.id"))
    traitement_id = Column(CHAR(36), ForeignKey("traitements.id"))
    dossier_id = Column(CHAR(36), ForeignKey("dossiers_medicaux.id"), nullable=False)
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
