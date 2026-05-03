"""
Infirmier database model
"""
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import DateTime
from ..database import Base


class Infirmier(Base):
    """Infirmier model - corresponds to 'infirmiers' table"""
    
    __tablename__ = "infirmiers"
    
    # Primary Key
    infirmier_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Infirmier Info
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    telephone = Column(String(20), nullable=False)
    email = Column(String(200))
    disponible = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    signes_vitaux = relationship("SignesVitaux", back_populates="infirmier")
    
    def __repr__(self):
        return f"<Infirmier(id={self.infirmier_id}, nom='{self.nom}', prenoms='{self.prenoms}')>"
