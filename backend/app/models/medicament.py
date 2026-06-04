"""Medicament model"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base

class Medicament(Base):
    __tablename__ = "medicaments"
    medicament_id = Column(Integer, primary_key=True, autoincrement=True)
    ordonnance_id = Column(Integer, ForeignKey("ordonnances.ordonnance_id"), nullable=False)
    nom_commercial = Column(String(255), nullable=False)
    denomination_commune = Column(String(255))
    dosage = Column(String(100))
    forme = Column(ENUM('COMPRIME', 'INJECTION', 'SIROP', 'CREME', 'COLLYRE', 'POUDRE', 'PATCH', 'SPRAY', 'CAPSULE', 'SOLUTION'))
    quantite = Column(Integer)
    frequence = Column(String(100))
    voie_administration = Column(ENUM('ORALE', 'INTRAVEINEUSE', 'CUTANEE', 'INTRAMUSCULAIRE', 'OPHTALMIQUE', 'NASALE', 'INHALATION', 'SOUS-CUTANEE', 'RECTALE'))
    duree_jours = Column(Integer)
    
    ordonnance = relationship("Ordonnance", back_populates="medicaments")
