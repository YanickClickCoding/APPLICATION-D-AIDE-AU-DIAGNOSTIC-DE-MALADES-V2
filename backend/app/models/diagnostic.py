"""
Diagnostic database model
"""
from sqlalchemy import Column, String, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR, ENUM
from ..database import Base


class Diagnostic(Base):
    """Diagnostic model - corresponds to 'diagnostics' table"""
    
    __tablename__ = "diagnostics"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Foreign Keys
    consultation_id = Column(CHAR(36), ForeignKey("consultations.consultation_id"), nullable=False)
    analyse_ia_id = Column(CHAR(36), ForeignKey("analyses_ia.id"))
    medecin_id = Column(CHAR(36), ForeignKey("medecins.medecin_id"), nullable=True)
    dossier_id = Column(CHAR(36), ForeignKey("dossiers_medicaux.id"), nullable=False)
    
    # Diagnostic Information
    code_icd10 = Column(String(20))  # Code ICD-10
    nom_maladie = Column(String(255), nullable=False)
    description = Column(Text)
    certitude = Column(Float)  # Niveau de certitude (0-1)
    
    # Status
    statut = Column(
        ENUM('PROVISOIRE', 'CONFIRMÉ', 'REJETÉ', 'ARCHIVÉ'),
        default='PROVISOIRE'
    )
    severite = Column(ENUM('LEGER', 'MODERE', 'GRAVE', 'CRITIQUE'))
    
    # Validation
    justification = Column(Text)
    date_validation = Column(Date)
    
    # Relationships
    consultation = relationship("Consultation", back_populates="diagnostics")
    analyse_ia = relationship("AnalyseIA", back_populates="diagnostics")
    medecin = relationship("Medecin", back_populates="diagnostics")
    dossier_medical = relationship("DossierMedical", back_populates="diagnostics")
    traitements = relationship("Traitement", back_populates="diagnostic", cascade="all, delete-orphan")
    suivis = relationship("Suivi", back_populates="diagnostic")
    
    def __repr__(self):
        return f"<Diagnostic(id={self.id}, maladie='{self.nom_maladie}', statut='{self.statut}')>"
