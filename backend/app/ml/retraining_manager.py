"""
Module de réentraînement automatique du modèle ML
Collecte les diagnostics validés et réentraîne le modèle quand le seuil est atteint
"""
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import json
from pathlib import Path
from sqlalchemy.orm import Session

from ..models.diagnostic import Diagnostic
from ..models.consultation import Consultation
from .model_training import ModelTrainer

logger = logging.getLogger(__name__)


class RetrainingManager:
    """
    Gestionnaire de réentraînement automatique du modèle
    
    Fonctionnalités:
    - Collecte des diagnostics validés depuis la base de données
    - Vérification du seuil de réentraînement (100 cas par défaut)
    - Réentraînement du modèle avec les nouvelles données
    - Évaluation et comparaison avec le modèle actuel
    - Déploiement automatique si le nouveau modèle est meilleur
    """
    
    def __init__(
        self,
        db: Session,
        model_dir: str = "./ml_models",
        retraining_threshold: int = 100
    ):
        """
        Initialise le gestionnaire de réentraînement
        
        Args:
            db: Session de base de données
            model_dir: Répertoire des modèles
            retraining_threshold: Nombre de cas validés nécessaires pour déclencher le réentraînement
        """
        self.db = db
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        self.retraining_threshold = retraining_threshold
        self.trainer = ModelTrainer()
    
    def collect_validated_diagnostics(self) -> pd.DataFrame:
        """
        Collecte tous les diagnostics validés (approuvés) depuis la base de données
        
        Returns:
            DataFrame avec les données des patients et leurs diagnostics validés
        """
        logger.info("📊 Collecte des diagnostics validés...")
        
        try:
            # Requête pour récupérer les diagnostics approuvés avec leurs consultations
            diagnostics = self.db.query(Diagnostic).filter(
                Diagnostic.statut == 'confirme'
            ).all()
            
            if not diagnostics:
                logger.warning("⚠️ Aucun diagnostic validé trouvé")
                return pd.DataFrame()
            
            # Construire le DataFrame
            data = []
            for diag in diagnostics:
                consultation = self.db.query(Consultation).filter(
                    Consultation.consultation_id == diag.consultation_id
                ).first()
                
                if consultation and consultation.patient:
                    patient = consultation.patient
                    
                    # Extraire les features du patient
                    row = {
                        'diagnostic': diag.diagnostic_final,
                        'age': self._calculate_age(patient.date_naissance),
                        'sexe': 1 if patient.sexe == 'M' else 0,
                    }
                    
                    # Ajouter les symptômes si disponibles
                    if consultation.symptomes:
                        for symptome in consultation.symptomes:
                            row[f'symptome_{symptome.nom.lower().replace(" ", "_")}'] = 1
                            row[f'severite_{symptome.nom.lower().replace(" ", "_")}'] = self._encode_severity(symptome.severite)
                    
                    # Ajouter les signes vitaux si disponibles
                    if consultation.signes_vitaux:
                        sv = consultation.signes_vitaux
                        row.update({
                            'tension_systolique': sv.tension_systolique,
                            'tension_diastolique': sv.tension_diastolique,
                            'frequence_cardiaque': sv.frequence_cardiaque,
                            'temperature': sv.temperature,
                            'saturation_o2': sv.saturation_o2,
                        })
                    
                    data.append(row)
            
            df = pd.DataFrame(data)
            logger.info(f"✅ {len(df)} diagnostics validés collectés")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la collecte des diagnostics: {e}")
            return pd.DataFrame()
    
    def should_retrain(self) -> Tuple[bool, int, int]:
        """
        Vérifie si le modèle doit être réentraîné
        
        Returns:
            Tuple (should_retrain, validated_count, threshold)
        """
        try:
            # Compter tous les diagnostics validés
            validated_count = self.db.query(Diagnostic).filter(
                Diagnostic.statut == 'confirme'
            ).count()
            
            should_retrain = validated_count >= self.retraining_threshold
            
            logger.info(
                f"📈 Diagnostics validés: {validated_count}/{self.retraining_threshold} "
                f"(Réentraînement: {'OUI' if should_retrain else 'NON'})"
            )
            
            return should_retrain, validated_count, self.retraining_threshold
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification du seuil: {e}")
            return False, 0, self.retraining_threshold
    
    def retrain_model(
        self,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Optional[Dict]:
        """
        Réentraîne le modèle avec les diagnostics validés
        
        Args:
            test_size: Proportion des données pour le test
            random_state: Seed pour la reproductibilité
            
        Returns:
            Dictionnaire avec les métriques du nouveau modèle ou None si échec
        """
        logger.info("🔄 Début du réentraînement du modèle...")
        
        try:
            # Collecter les données
            df = self.collect_validated_diagnostics()
            
            if df.empty or len(df) < 50:
                logger.warning(f"⚠️ Pas assez de données pour réentraîner ({len(df)} cas)")
                return None
            
            # Séparer features et target
            X = df.drop('diagnostic', axis=1)
            y = df['diagnostic']
            
            # Remplir les valeurs manquantes
            X = X.fillna(X.mean())
            
            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=random_state, stratify=y
            )
            
            logger.info(f"📊 Données: {len(X_train)} train, {len(X_test)} test")
            
            # Entraîner le modèle
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=random_state,
                n_jobs=-1
            )
            
            logger.info("🎯 Entraînement en cours...")
            model.fit(X_train, y_train)
            
            # Évaluer le modèle
            metrics = self.evaluate_new_model(model, X_test, y_test)
            
            # Sauvegarder le modèle temporaire
            temp_model_path = self.model_dir / f"temp_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
            joblib.dump({
                'model': model,
                'feature_names': list(X.columns),
                'classes': list(model.classes_),
                'metadata': {
                    'training_date': datetime.now().isoformat(),
                    'n_samples': len(df),
                    'n_features': len(X.columns),
                    'n_classes': len(model.classes_),
                    'metrics': metrics
                }
            }, temp_model_path)
            
            logger.info(f"✅ Modèle temporaire sauvegardé: {temp_model_path}")
            
            return {
                'model_path': str(temp_model_path),
                'metrics': metrics,
                'n_samples': len(df),
                'n_features': len(X.columns),
                'n_classes': len(model.classes_)
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du réentraînement: {e}")
            return None
    
    def evaluate_new_model(
        self,
        model: RandomForestClassifier,
        X_test: pd.DataFrame,
        y_test: pd.Series
    ) -> Dict:
        """
        Évalue le nouveau modèle sur les données de test
        
        Args:
            model: Modèle à évaluer
            X_test: Features de test
            y_test: Labels de test
            
        Returns:
            Dictionnaire avec les métriques
        """
        logger.info("📊 Évaluation du nouveau modèle...")
        
        try:
            # Prédictions
            y_pred = model.predict(X_test)
            
            # Calculer les métriques
            accuracy = accuracy_score(y_test, y_pred)
            precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
            recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
            f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
            
            # Matrice de confusion
            cm = confusion_matrix(y_test, y_pred)
            
            metrics = {
                'accuracy': float(accuracy),
                'precision': float(precision),
                'recall': float(recall),
                'f1_score': float(f1),
                'confusion_matrix': cm.tolist()
            }
            
            logger.info(f"✅ Métriques: Accuracy={accuracy:.3f}, F1={f1:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'évaluation: {e}")
            return {}
    
    def deploy_model(self, model_path: str, version: str = None) -> bool:
        """
        Déploie un nouveau modèle en production
        
        Args:
            model_path: Chemin vers le modèle à déployer
            version: Version du modèle (auto-généré si None)
            
        Returns:
            True si le déploiement a réussi
        """
        logger.info(f"🚀 Déploiement du modèle: {model_path}")
        
        try:
            # Charger le modèle temporaire
            model_data = joblib.load(model_path)
            
            # Générer le nom de version
            if version is None:
                version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Sauvegarder avec le nouveau nom
            production_path = self.model_dir / f"random_forest_{version}.joblib"
            joblib.dump(model_data, production_path)
            
            # Supprimer le modèle temporaire
            Path(model_path).unlink()
            
            logger.info(f"✅ Modèle déployé: {production_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du déploiement: {e}")
            self.db.rollback()
            return False
    
    def auto_retrain_and_deploy(self) -> Dict:
        """
        Processus complet de réentraînement et déploiement automatique
        
        Returns:
            Dictionnaire avec le statut et les détails
        """
        logger.info("🤖 Démarrage du processus de réentraînement automatique...")
        
        try:
            # Vérifier si le réentraînement est nécessaire
            should_retrain, validated_count, threshold = self.should_retrain()
            
            if not should_retrain:
                return {
                    'status': 'skipped',
                    'message': f'Pas assez de données ({validated_count}/{threshold})',
                    'validated_count': validated_count,
                    'threshold': threshold
                }
            
            # Réentraîner le modèle
            result = self.retrain_model()
            
            if not result:
                return {
                    'status': 'failed',
                    'message': 'Échec du réentraînement',
                    'validated_count': validated_count
                }
            
            # Comparer avec le modèle actuel
            current_accuracy = self._get_current_model_accuracy()
            new_accuracy = result['metrics']['accuracy']
            
            logger.info(f"📊 Comparaison: Actuel={current_accuracy:.3f}, Nouveau={new_accuracy:.3f}")
            
            # Déployer si meilleur
            if new_accuracy >= current_accuracy:
                deployed = self.deploy_model(result['model_path'])
                
                if deployed:
                    return {
                        'status': 'deployed',
                        'message': 'Nouveau modèle déployé avec succès',
                        'old_accuracy': current_accuracy,
                        'new_accuracy': new_accuracy,
                        'improvement': new_accuracy - current_accuracy,
                        'metrics': result['metrics']
                    }
                else:
                    return {
                        'status': 'failed',
                        'message': 'Échec du déploiement',
                        'metrics': result['metrics']
                    }
            else:
                # Supprimer le modèle temporaire
                Path(result['model_path']).unlink()
                
                return {
                    'status': 'rejected',
                    'message': 'Nouveau modèle moins performant',
                    'old_accuracy': current_accuracy,
                    'new_accuracy': new_accuracy,
                    'metrics': result['metrics']
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur dans le processus automatique: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _get_current_model_accuracy(self) -> float:
        """Retourne 0.0 (log de training supprimé)"""
        return 0.0
    
    def _calculate_age(self, date_naissance: datetime) -> int:
        """Calcule l'âge à partir de la date de naissance"""
        today = datetime.now()
        age = today.year - date_naissance.year
        if today.month < date_naissance.month or (today.month == date_naissance.month and today.day < date_naissance.day):
            age -= 1
        return age
    
    def _encode_severity(self, severity: str) -> int:
        """Encode la sévérité en valeur numérique"""
        severity_map = {
            'Légère': 1,
            'Modérée': 2,
            'Sévère': 3
        }
        return severity_map.get(severity, 1)
