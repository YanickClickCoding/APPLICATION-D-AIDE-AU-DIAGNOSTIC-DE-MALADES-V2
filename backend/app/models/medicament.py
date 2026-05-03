"""Medicament model"""
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, ENUM
from ..database import Base

class Medicament(Base):
    __tablename__ = "medicaments"
    id = Column(CHAR(36), primary_key=True)
    ordonnance_id = Column(CHAR(36), ForeignKey("ordonnances.id"), nullable=False)
    nom_commercial = Column(String(255), nullable=False)
    denomination_commune = Column(String(255))
    dosage = Column(String(100))
    forme = Column(ENUM('COMPRIME', 'INJECTION', 'SIROP', 'CREME'))
    quantite = Column(Integer)
    frequence = Column(String(100))
    voie_administration = Column(ENUM('ORALE', 'INTRAVEINEUSE', 'CUTANEE', 'INTRAMUSCULAIRE'))
    duree_jours = Column(Integer)
    
    ordonnance = relationship("Ordonnance", back_populates="medicaments")
