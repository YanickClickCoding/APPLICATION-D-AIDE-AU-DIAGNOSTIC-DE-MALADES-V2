"""
AnalyseIA database model - Stocke les prédictions de l'IA
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base


class AnalyseIA(Base):
    """AnalyseIA model - corresponds to 'analyses_ia' table"""
    
    __tablename__ = "analyses_ia"
    
    # Primary Key
    analyse_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Foreign Key
    consultation_id = Column(Integer, ForeignKey("consultations.consultation_id"), nullable=False)
    
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
        return f"<AnalyseIA(analyse_id={self.analyse_id}, modele='{self.modele_ia}', confiance={self.scoring_confiance})>"
