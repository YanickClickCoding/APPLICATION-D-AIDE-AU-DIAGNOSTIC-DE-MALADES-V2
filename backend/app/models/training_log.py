"""
Model Training Log Model
Historique des entraînements du modèle ML
Requirement: 7.6
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from datetime import datetime
from app.database import Base


class ModelTrainingLog(Base):
    """
    Modèle pour l'historique des entraînements du modèle ML
    Enregistre chaque session d'entraînement avec ses métriques
    """
    __tablename__ = "model_training_logs"
    
    # Clé primaire
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Version du modèle
    version = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # RandomForest, DecisionTree, etc.
    
    # Métriques de performance
    accuracy = Column(Float, nullable=False)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Matrice de confusion (JSON)
    confusion_matrix = Column(JSON, nullable=True)
    
    # Détails de l'entraînement
    training_samples = Column(Integer, nullable=True)
    test_samples = Column(Integer, nullable=True)
    n_features = Column(Integer, nullable=True)
    n_classes = Column(Integer, nullable=True)
    
    # Hyperparamètres (JSON)
    hyperparameters = Column(JSON, nullable=True)
    
    # Importance des features (JSON)
    feature_importance = Column(JSON, nullable=True)
    
    # Temps d'entraînement
    training_duration_seconds = Column(Float, nullable=True)
    
    # Statut du déploiement
    is_deployed = Column(Integer, default=0)  # 0=non, 1=oui
    deployed_at = Column(DateTime, nullable=True)
    
    # Chemin du fichier modèle
    model_filepath = Column(String(500), nullable=True)
    
    # Notes et commentaires
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __repr__(self):
        return f"<ModelTrainingLog(id={self.id}, version={self.version}, accuracy={self.accuracy:.4f})>"
    
    def to_dict(self):
        """Convertit l'objet en dictionnaire"""
        return {
            "id": self.id,
            "version": self.version,
            "model_type": self.model_type,
            "accuracy": self.accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "confusion_matrix": self.confusion_matrix,
            "training_samples": self.training_samples,
            "test_samples": self.test_samples,
            "n_features": self.n_features,
            "n_classes": self.n_classes,
            "hyperparameters": self.hyperparameters,
            "feature_importance": self.feature_importance,
            "training_duration_seconds": self.training_duration_seconds,
            "is_deployed": self.is_deployed,
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "model_filepath": self.model_filepath,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
