"""Traitement model"""
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base

class Traitement(Base):
    __tablename__ = "traitements"
    traitement_id = Column(Integer, primary_key=True, autoincrement=True)
    diagnostic_id = Column(Integer, ForeignKey("diagnostics.diagnostic_id"), nullable=False)
    nom_traitement = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(ENUM('MEDICAMENTEUX', 'CHIRURGICAL', 'PHYSIQUE', 'PSYCHOLOGIQUE'))
    duree_jours = Column(Integer)
    date_debut = Column(Date)
    date_fin = Column(Date)
    statut = Column(ENUM('PRESCRIT', 'EN_COURS', 'TERMINE', 'ABANDONNE', 'ECHEC'), default='PRESCRIT')
    objective_therapeutique = Column(Text)
    
    diagnostic = relationship("Diagnostic", back_populates="traitements")
    ordonnance = relationship("Ordonnance", back_populates="traitement", uselist=False)
    suivis = relationship("Suivi", back_populates="traitement")
