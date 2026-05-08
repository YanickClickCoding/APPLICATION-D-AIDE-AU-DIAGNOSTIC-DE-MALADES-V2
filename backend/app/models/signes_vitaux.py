"""
SignesVitaux database model
"""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class SignesVitaux(Base):
    """SignesVitaux model - corresponds to 'signes_vitaux' table"""

    __tablename__ = "signes_vitaux"

    # Primary Key
    signes_vitaux_id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Foreign Keys
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    infirmier_id = Column(Integer, ForeignKey("infirmiers.infirmier_id"))

    # Vital Signs
    tension_systolique = Column(Integer)
    tension_diastolique = Column(Integer)
    frequence_cardiaque = Column(Integer)
    temperature = Column(Float)
    frequence_respiratoire = Column(Integer)
    saturation_oxygene = Column(Float)
    poids = Column(Float)
    taille = Column(Float)
    imc = Column(Float)
    glycemie = Column(Float)

    # Timestamp
    date_enregistrement = Column(DateTime, server_default=func.now())

    # Relationships
    consultation = relationship("Consultation", back_populates="signes_vitaux")
    infirmier = relationship("Infirmier", back_populates="signes_vitaux")

    def __repr__(self):
        return f"<SignesVitaux(signes_vitaux_id={self.signes_vitaux_id}, temp={self.temperature}, sat_o2={self.saturation_oxygene})>"