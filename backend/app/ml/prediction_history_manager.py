"""
Prediction History Manager
Gestion de l'historique des prédictions ML
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5
"""
from sqlalchemy.orm import Session
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from app.models.prediction_history import PredictionHistory

logger = logging.getLogger(__name__)


class PredictionHistoryManager:
    """
    Gestionnaire pour l'historique des prédictions ML
    Implémente les Requirements 5.1 à 5.5
    """
    
    def __init__(self, db: Session):
        """
        Initialise le gestionnaire
        
        Args:
            db: Session de base de données SQLAlchemy
        """
        self.db = db
    
    def save_prediction(self, 
                       patient_id: int,
                       predicted_disease: str,
                       confidence: float,
                       prediction_probabilities: Optional[Dict[str, float]] = None,
                       feature_values: Optional[Dict[str, Any]] = None,
                       top_features: Optional[List[Dict]] = None,
                       consultation_id: Optional[int] = None,
                       model_version: Optional[str] = None,
                       model_accuracy: Optional[float] = None) -> PredictionHistory:
        """
        Enregistre une nouvelle prédiction dans l'historique
        
        Args:
            patient_id: ID du patient
            predicted_disease: Maladie prédite
            confidence: Score de confiance (0-1)
            prediction_probabilities: Probabilités pour toutes les classes
            feature_values: Valeurs des features utilisées
            top_features: Top features importantes
            consultation_id: ID de la consultation (optionnel)
            model_version: Version du modèle
            model_accuracy: Précision du modèle
            
        Returns:
            Objet PredictionHistory créé
        """
        # Déterminer le niveau de confiance
        if confidence >= 0.8:
            confidence_level = "HIGH"
        elif confidence >= 0.6:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        # Créer l'entrée d'historique
        prediction_entry = PredictionHistory(
            patient_id=patient_id,
            consultation_id=consultation_id,
            predicted_disease=predicted_disease,
            confidence=confidence,
            confidence_level=confidence_level,
            prediction_probabilities=prediction_probabilities,
            feature_values=feature_values,
            top_features=top_features,
            model_version=model_version,
            model_accuracy=model_accuracy,
            created_at=datetime.utcnow()
        )
        
        # Sauvegarder dans la base de données
        self.db.add(prediction_entry)
        self.db.commit()
        self.db.refresh(prediction_entry)
        
        logger.info(f"Prédiction sauvegardée: patient_id={patient_id}, disease={predicted_disease}, confidence={confidence:.2f}")
        
        return prediction_entry
    
    def get_patient_history(self, 
                           patient_id: int,
                           limit: Optional[int] = None,
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> List[PredictionHistory]:
        """
        Récupère l'historique des prédictions pour un patient
        
        Args:
            patient_id: ID du patient
            limit: Nombre maximum de prédictions à retourner
            start_date: Date de début (optionnel)
            end_date: Date de fin (optionnel)
            
        Returns:
            Liste des prédictions triées par date décroissante
        """
        query = self.db.query(PredictionHistory).filter(
            PredictionHistory.patient_id == patient_id
        )
        
        # Filtrer par date si spécifié
        if start_date:
            query = query.filter(PredictionHistory.created_at >= start_date)
        if end_date:
            query = query.filter(PredictionHistory.created_at <= end_date)
        
        # Trier par date décroissante (plus récent en premier)
        query = query.order_by(PredictionHistory.created_at.desc())
        
        # Limiter le nombre de résultats
        if limit:
            query = query.limit(limit)
        
        predictions = query.all()
        
        logger.info(f"Historique récupéré: patient_id={patient_id}, count={len(predictions)}")
        
        return predictions
    
    def get_latest_prediction(self, patient_id: int) -> Optional[PredictionHistory]:
        """
        Récupère la dernière prédiction pour un patient
        
        Args:
            patient_id: ID du patient
            
        Returns:
            Dernière prédiction ou None
        """
        prediction = self.db.query(PredictionHistory).filter(
            PredictionHistory.patient_id == patient_id
        ).order_by(PredictionHistory.created_at.desc()).first()
        
        return prediction
    
    def compare_predictions(self, 
                           prediction_id1: int,
                           prediction_id2: int) -> Dict:
        """
        Compare deux prédictions
        
        Args:
            prediction_id1: ID de la première prédiction
            prediction_id2: ID de la deuxième prédiction
            
        Returns:
            Dictionnaire de comparaison
        """
        # Récupérer les deux prédictions
        pred1 = self.db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id1
        ).first()
        
        pred2 = self.db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id2
        ).first()
        
        if not pred1 or not pred2:
            raise ValueError("Une ou plusieurs prédictions introuvables")
        
        # Calculer les différences
        comparison = {
            "prediction1": {
                "id": pred1.id,
                "date": pred1.created_at.isoformat(),
                "disease": pred1.predicted_disease,
                "confidence": pred1.confidence,
                "confidence_level": pred1.confidence_level
            },
            "prediction2": {
                "id": pred2.id,
                "date": pred2.created_at.isoformat(),
                "disease": pred2.predicted_disease,
                "confidence": pred2.confidence,
                "confidence_level": pred2.confidence_level
            },
            "differences": {
                "disease_changed": pred1.predicted_disease != pred2.predicted_disease,
                "confidence_change": pred2.confidence - pred1.confidence,
                "time_difference_hours": (pred2.created_at - pred1.created_at).total_seconds() / 3600
            }
        }
        
        # Comparer les features si disponibles
        if pred1.feature_values and pred2.feature_values:
            feature_changes = {}
            for feature, value1 in pred1.feature_values.items():
                if feature in pred2.feature_values:
                    value2 = pred2.feature_values[feature]
                    if value1 != value2:
                        feature_changes[feature] = {
                            "old_value": value1,
                            "new_value": value2,
                            "change": value2 - value1 if isinstance(value1, (int, float)) and isinstance(value2, (int, float)) else None
                        }
            
            comparison["feature_changes"] = feature_changes
        
        logger.info(f"Comparaison: pred1={prediction_id1}, pred2={prediction_id2}")
        
        return comparison
    
    def compare_with_previous(self, patient_id: int, 
                             current_prediction: Dict) -> Optional[Dict]:
        """
        Compare une prédiction actuelle avec la précédente pour un patient
        
        Args:
            patient_id: ID du patient
            current_prediction: Dictionnaire de la prédiction actuelle
            
        Returns:
            Dictionnaire de comparaison ou None si pas de prédiction précédente
        """
        # Récupérer la dernière prédiction
        previous = self.get_latest_prediction(patient_id)
        
        if not previous:
            logger.info(f"Pas de prédiction précédente pour patient_id={patient_id}")
            return None
        
        # Comparer
        comparison = {
            "previous": {
                "id": previous.id,
                "date": previous.created_at.isoformat(),
                "disease": previous.predicted_disease,
                "confidence": previous.confidence
            },
            "current": {
                "disease": current_prediction.get("predicted_disease"),
                "confidence": current_prediction.get("confidence")
            },
            "changes": {
                "disease_changed": previous.predicted_disease != current_prediction.get("predicted_disease"),
                "confidence_change": current_prediction.get("confidence", 0) - previous.confidence
            }
        }
        
        return comparison
    
    def detect_significant_changes(self, 
                                   patient_id: int,
                                   lookback_days: int = 7,
                                   confidence_threshold: float = 0.2,
                                   disease_change: bool = True) -> List[Dict]:
        """
        Détecte les changements significatifs dans l'historique des prédictions
        
        Args:
            patient_id: ID du patient
            lookback_days: Nombre de jours à analyser
            confidence_threshold: Seuil de changement de confiance significatif
            disease_change: Détecter les changements de diagnostic
            
        Returns:
            Liste des changements significatifs détectés
        """
        # Récupérer l'historique récent
        start_date = datetime.utcnow() - timedelta(days=lookback_days)
        history = self.get_patient_history(
            patient_id=patient_id,
            start_date=start_date
        )
        
        if len(history) < 2:
            logger.info(f"Pas assez de prédictions pour détecter des changements: patient_id={patient_id}")
            return []
        
        significant_changes = []
        
        # Comparer chaque prédiction avec la précédente
        for i in range(len(history) - 1):
            current = history[i]
            previous = history[i + 1]
            
            # Changement de diagnostic
            if disease_change and current.predicted_disease != previous.predicted_disease:
                significant_changes.append({
                    "type": "disease_change",
                    "date": current.created_at.isoformat(),
                    "from": previous.predicted_disease,
                    "to": current.predicted_disease,
                    "confidence_from": previous.confidence,
                    "confidence_to": current.confidence,
                    "severity": "HIGH"
                })
            
            # Changement significatif de confiance
            confidence_change = abs(current.confidence - previous.confidence)
            if confidence_change >= confidence_threshold:
                significant_changes.append({
                    "type": "confidence_change",
                    "date": current.created_at.isoformat(),
                    "disease": current.predicted_disease,
                    "confidence_from": previous.confidence,
                    "confidence_to": current.confidence,
                    "change": current.confidence - previous.confidence,
                    "severity": "MEDIUM" if confidence_change >= 0.3 else "LOW"
                })
        
        logger.info(f"Changements significatifs détectés: patient_id={patient_id}, count={len(significant_changes)}")
        
        return significant_changes
    
    def get_prediction_statistics(self, patient_id: int) -> Dict:
        """
        Calcule des statistiques sur l'historique des prédictions d'un patient
        
        Args:
            patient_id: ID du patient
            
        Returns:
            Dictionnaire de statistiques
        """
        history = self.get_patient_history(patient_id)
        
        if not history:
            return {
                "total_predictions": 0,
                "diseases": {},
                "average_confidence": 0.0,
                "confidence_trend": None
            }
        
        # Compter les diagnostics
        disease_counts = {}
        confidences = []
        
        for pred in history:
            disease_counts[pred.predicted_disease] = disease_counts.get(pred.predicted_disease, 0) + 1
            confidences.append(pred.confidence)
        
        # Tendance de confiance (dernières 5 prédictions)
        recent_confidences = confidences[:5]
        if len(recent_confidences) >= 2:
            confidence_trend = "increasing" if recent_confidences[0] > recent_confidences[-1] else "decreasing"
        else:
            confidence_trend = "stable"
        
        statistics = {
            "total_predictions": len(history),
            "diseases": disease_counts,
            "average_confidence": sum(confidences) / len(confidences),
            "min_confidence": min(confidences),
            "max_confidence": max(confidences),
            "confidence_trend": confidence_trend,
            "most_common_disease": max(disease_counts, key=disease_counts.get) if disease_counts else None
        }
        
        logger.info(f"Statistiques calculées: patient_id={patient_id}")
        
        return statistics
    
    def update_validation(self,
                         prediction_id: int,
                         is_validated: int,
                         validated_by: int,
                         validation_notes: Optional[str] = None,
                         actual_disease: Optional[str] = None) -> PredictionHistory:
        """
        Met à jour le statut de validation d'une prédiction
        
        Args:
            prediction_id: ID de la prédiction
            is_validated: Statut (1=approuvé, -1=rejeté, 0=en attente)
            validated_by: ID du médecin validateur
            validation_notes: Notes de validation
            actual_disease: Diagnostic réel si différent
            
        Returns:
            Prédiction mise à jour
        """
        prediction = self.db.query(PredictionHistory).filter(
            PredictionHistory.id == prediction_id
        ).first()
        
        if not prediction:
            raise ValueError(f"Prédiction {prediction_id} introuvable")
        
        prediction.is_validated = is_validated
        prediction.validated_by = validated_by
        prediction.validated_at = datetime.utcnow()
        prediction.validation_notes = validation_notes
        
        if actual_disease:
            prediction.actual_disease = actual_disease
        
        self.db.commit()
        self.db.refresh(prediction)
        
        logger.info(f"Validation mise à jour: prediction_id={prediction_id}, status={is_validated}")
        
        return prediction
    
    def get_validation_statistics(self) -> Dict:
        """
        Calcule des statistiques globales sur les validations
        
        Returns:
            Dictionnaire de statistiques
        """
        total = self.db.query(PredictionHistory).count()
        approved = self.db.query(PredictionHistory).filter(
            PredictionHistory.is_validated == 1
        ).count()
        rejected = self.db.query(PredictionHistory).filter(
            PredictionHistory.is_validated == -1
        ).count()
        pending = self.db.query(PredictionHistory).filter(
            PredictionHistory.is_validated == 0
        ).count()
        
        statistics = {
            "total_predictions": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
            "approval_rate": (approved / total * 100) if total > 0 else 0,
            "rejection_rate": (rejected / total * 100) if total > 0 else 0
        }
        
        logger.info(f"Statistiques de validation: {statistics}")
        
        return statistics


def demo_prediction_history_manager():
    """
    Fonction de démonstration du gestionnaire d'historique
    """
    from app.database import SessionLocal
    
    db = SessionLocal()
    manager = PredictionHistoryManager(db)
    
    # Sauvegarder une prédiction
    prediction = manager.save_prediction(
        patient_id=1,
        predicted_disease="Grippe",
        confidence=0.85,
        prediction_probabilities={"Grippe": 0.85, "COVID-19": 0.10, "Rhume": 0.05},
        model_version="v1.0"
    )
    
    print(f"Prédiction sauvegardée: {prediction.id}")
    
    # Récupérer l'historique
    history = manager.get_patient_history(patient_id=1, limit=10)
    print(f"Historique: {len(history)} prédictions")
    
    # Statistiques
    stats = manager.get_prediction_statistics(patient_id=1)
    print(f"Statistiques: {stats}")
    
    db.close()


if __name__ == "__main__":
    demo_prediction_history_manager()
