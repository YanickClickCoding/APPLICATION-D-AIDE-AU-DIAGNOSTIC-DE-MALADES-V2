"""
SignesVitaux database model
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..database import Base


class SignesVitaux(Base):
    """SignesVitaux model - corresponds to 'signes_vitaux' table"""
    
    __tablename__ = "signes_vitaux"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Foreign Keys
    consultation_id = Column(CHAR(36), ForeignKey("consultations.consultation_id"), nullable=False)
    infirmier_id = Column(Integer, ForeignKey("infirmiers.infirmier_id"))
    
    # Vital Signs
    tension_systolique = Column(Integer)  # mmHg
    tension_diastolique = Column(Integer)  # mmHg
    frequence_cardiaque = Column(Integer)  # bpm
    temperature = Column(Float)  # °C
    frequence_respiratoire = Column(Integer)  # /min
    saturation_oxygene = Column(Float)  # %
    poids = Column(Float)  # kg
    taille = Column(Float)  # cm
    imc = Column(Float)  # kg/m²
    glycemie = Column(Float)  # g/L
    
    # Timestamp
    date_enregistrement = Column(DateTime, server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="signes_vitaux")
    infirmier = relationship("Infirmier", back_populates="signes_vitaux")
    
    def __repr__(self):
        return f"<SignesVitaux(id={self.id}, temp={self.temperature}, sat_o2={self.saturation_oxygene})>"
