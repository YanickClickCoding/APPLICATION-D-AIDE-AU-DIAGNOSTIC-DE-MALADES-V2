"""
Diagnostic database model
"""
from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import ENUM
from ..database import Base


class Diagnostic(Base):
    """Diagnostic model - corresponds to 'diagnostics' table"""
    
    __tablename__ = "diagnostics"
    
    # Primary Key
    diagnostic_id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False, index=True)
    analyse_ia_id = Column(Integer, ForeignKey("analyses_ia.analyse_id"), index=True)
    medecin_id = Column(Integer, ForeignKey("medecins.medecin_id"), nullable=True, index=True)
    dossier_id = Column(Integer, ForeignKey("dossiers_medicaux.dossier_id"), nullable=False)
    
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
        return f"<Diagnostic(diagnostic_id={self.diagnostic_id}, maladie='{self.nom_maladie}', statut='{self.statut}')>"
