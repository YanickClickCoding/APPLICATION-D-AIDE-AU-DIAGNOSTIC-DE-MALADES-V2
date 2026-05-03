"""
AnalyseIA database model - Stocke les prédictions de l'IA
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from ..database import Base


class AnalyseIA(Base):
    """AnalyseIA model - corresponds to 'analyses_ia' table"""
    
    __tablename__ = "analyses_ia"
    
    # Primary Key (UUID)
    id = Column(CHAR(36), primary_key=True, index=True)
    
    # Foreign Key
    consultation_id = Column(CHAR(36), ForeignKey("consultations.consultation_id"), nullable=False)
    
    # AI Model Info
    modele_ia = Column(String(100))  # Nom du modèle (ex: "RandomForest_v1.0")
    probabilite = Column(Float)  # Probabilité du diagnostic principal
    diagnostics_suggeres = Column(JSON)  # Liste des diagnostics avec probabilités
    scoring_confiance = Column(Float)  # Score de confiance global (0-1)
    
    # Input/Output Data
    donnees_entree = Column(JSON)  # Données utilisées pour la prédiction
    temps_traitement = Column(Integer)  # Temps de traitement en ms
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    consultation = relationship("Consultation", back_populates="analyses_ia")
    diagnostics = relationship("Diagnostic", back_populates="analyse_ia")
    
    def __repr__(self):
        return f"<AnalyseIA(id={self.id}, modele='{self.modele_ia}', confiance={self.scoring_confiance})>"
