"""Examen model"""
from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base

class Examen(Base):
    __tablename__ = "examens"
    examen_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    type = Column(ENUM('CLINIQUE', 'IMAGERIE', 'BIOLOGIE', 'ELECTROCARDIOGRAMME'))
    nom = Column(String(255), nullable=False)
    description = Column(Text)
    resultats = Column(Text)
    valeur_numerique = Column(Float)
    unite_mesure = Column(String(20))
    statut = Column(ENUM('DEMANDE', 'EN_COURS', 'REALISE', 'ANALYSE'), default='DEMANDE')
    date_examen = Column(Date)
    
    consultation = relationship("Consultation", back_populates="examens")
