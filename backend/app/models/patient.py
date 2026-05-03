"""
Patient database model - Adapté au schéma MySQL existant
"""
from sqlalchemy import Column, String, Date, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..database import Base


class Patient(Base):
    """Patient model - corresponds to 'patients' table"""
    
    __tablename__ = "patients"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Personal Information
    nom = Column(String(100), nullable=False)
    prenoms = Column(String(150), nullable=False)
    date_naissance = Column(Date, nullable=False)
    sexe = Column(Enum('M', 'F'), nullable=False)
    groupe_sanguin = Column(Enum('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'))
    
    # Contact Information
    telephone = Column(String(20))
    email = Column(String(200))
    adresse = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    dossier_medical = relationship("DossierMedical", back_populates="patient", uselist=False)
    ordonnances = relationship("Ordonnance", back_populates="patient")
    suivis = relationship("Suivi", back_populates="patient")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, nom='{self.nom}', prenoms='{self.prenoms}')>"
