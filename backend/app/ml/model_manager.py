"""
Model Manager Module - Singleton pour gérer le cycle de vie du modèle
Gère le chargement, l'entraînement et les prédictions
"""
import os
import logging
from typing import Optional, Dict
from datetime import datetime
import pandas as pd
import numpy as np

from .data_preprocessing import DataPreprocessor
from .model_training import ModelTrainer
from .predictor import Predictor

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Singleton pour gérer le modèle ML
    Assure qu'un seul modèle est chargé en mémoire
    """
    
    _instance: Optional['ModelManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.preprocessor = DataPreprocessor()
        self.trainer = ModelTrainer()
        self.predictor: Optional[Predictor] = None
        self.model_loaded = False
        self.model_version = None
        self.model_metadata = {}
        self._initialized = True
        
        logger.info("🤖 ModelManager initialisé")
    
    def load_latest_model(self, model_path: str = "./ml_models/") -> bool:
        """
        Charge le dernier modèle entraîné
        """
        try:
            if not os.path.exists(model_path):
                logger.warning(f"⚠️ Dossier modèles introuvable: {model_path}")
                return False
            
            # Trouver le dernier modèle
            model_files = [f for f in os.listdir(model_path) if f.endswith('.joblib')]
            
            if not model_files:
                logger.warning("⚠️ Aucun modèle trouvé")
                return False
            
            # Trier par date (le plus récent en premier)
            model_files.sort(reverse=True)
            latest_model = os.path.join(model_path, model_files[0])
            
            # Charger le modèle
            self.trainer.load_model(latest_model)
            
            # Créer le predictor
            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names
            )
            
            self.model_loaded = True
            self.model_version = model_files[0]
            self.model_metadata = self.trainer.training_history
            
            logger.info(f"✅ Modèle chargé: {self.model_version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement modèle: {e}")
            return False
    
    def train_new_model(
        self,
        dataset_path: str,
        n_estimators: int = 100,
        max_depth: int = 20,
        save: bool = True
    ) -> Dict:
        """
        Entraîne un nouveau modèle sur le dataset
        """
        try:
            logger.info(f"🚀 Début entraînement nouveau modèle...")
            logger.info(f"   Dataset: {dataset_path}")
            
            # 1. Charger les données
            df = self.preprocessor.load_dataset(dataset_path)
            
            # 2. Nettoyage
            df, cleaning_log = self.preprocessor.clean_data(df)
            
            # 3. Créer features
            df = self.preprocessor.create_features(df)
            
            # 4. Normalisation (colonnes numériques)
            # Identifier les colonnes numériques à normaliser (exclure ID et target)
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            # Retirer la target si elle est numérique
            if 'Maladie_Diagnostic' in numeric_cols:
                numeric_cols.remove('Maladie_Diagnostic')
            
            # Normaliser seulement les colonnes Vital_ et Lab_
            cols_to_normalize = [col for col in numeric_cols if col.startswith('Vital_') or col.startswith('Lab_')]
            
            if cols_to_normalize:
                df, norm_params = self.preprocessor.normalize_data(df, cols_to_normalize)
            
            # 5. Supprimer les colonnes non-numériques (sauf la target)
            # Garder seulement: target + colonnes numériques
            cols_to_keep = ['Maladie_Diagnostic'] + df.select_dtypes(include=[np.number]).columns.tolist()
            df = df[cols_to_keep]
            
            # Supprimer les colonnes inutiles (ID, dates, etc.)
            cols_to_drop = ['ID'] if 'ID' in df.columns else []
            if cols_to_drop:
                df = df.drop(columns=cols_to_drop)
            
            # 6. Préparer X et y
            X, y = self.preprocessor.prepare_xy(df, target_column='Maladie_Diagnostic')
            
            # 7. Entraîner
            training_results = self.trainer.train(
                X, y,
                n_estimators=n_estimators,
                max_depth=max_depth
            )
            
            # 8. Évaluer
            from sklearn.model_selection import train_test_split
            y_encoded = self.trainer.label_encoder.transform(y)
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y_encoded
            )
            evaluation_results = self.trainer.evaluate(X_test, y_test)
            
            # 9. Sauvegarder si demandé
            if save:
                model_path = self.trainer.save_model(version="1.0")
                training_results["model_path"] = model_path
            
            # 10. Charger le nouveau modèle
            self.predictor = Predictor(
                model=self.trainer.model,
                label_encoder=self.trainer.label_encoder,
                feature_names=self.trainer.feature_names
            )
            
            self.model_loaded = True
            self.model_metadata = training_results
            
            logger.info("✅ Entraînement terminé avec succès!")
            
            return {
                "training": training_results,
                "evaluation": evaluation_results,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur entraînement: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict(self, patient_data: Dict) -> Dict:
        """
        Fait une prédiction pour un patient
        """
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé. Appelez load_latest_model() d'abord.")
        
        try:
            # Convertir en DataFrame
            df = pd.DataFrame([patient_data])
            
            # S'assurer que toutes les features sont présentes
            for feature in self.trainer.feature_names:
                if feature not in df.columns:
                    df[feature] = 0  # Valeur par défaut
            
            # Réorganiser les colonnes
            df = df[self.trainer.feature_names]
            
            # Prédiction
            result = self.predictor.predict(df)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur prédiction: {e}")
            raise
    
    def explain_prediction(self, patient_data: Dict) -> Dict:
        """
        Explique une prédiction
        """
        if not self.model_loaded or self.predictor is None:
            raise ValueError("Modèle non chargé.")
        
        try:
            df = pd.DataFrame([patient_data])
            
            for feature in self.trainer.feature_names:
                if feature not in df.columns:
                    df[feature] = 0
            
            df = df[self.trainer.feature_names]
            
            explanation = self.predictor.explain_prediction(df)
            
            return explanation
            
        except Exception as e:
            logger.error(f"❌ Erreur explication: {e}")
            raise
    
    def get_model_info(self) -> Dict:
        """
        Retourne les informations sur le modèle chargé
        """
        return {
            "loaded": self.model_loaded,
            "version": self.model_version,
            "metadata": self.model_metadata,
            "n_features": len(self.trainer.feature_names) if self.trainer.feature_names else 0,
            "n_classes": len(self.trainer.label_encoder.classes_) if self.trainer.label_encoder else 0,
            "classes": self.trainer.label_encoder.classes_.tolist() if self.trainer.label_encoder else []
        }
    
    def retrain_with_new_data(self, new_data_path: str) -> Dict:
        """
        Réentraîne le modèle avec de nouvelles données
        US-028: Réentraînement
        """
        logger.info("🔄 Réentraînement avec nouvelles données...")
        
        # Entraîner nouveau modèle
        results = self.train_new_model(new_data_path, save=True)
        
        if results["success"]:
            # Comparer avec ancien modèle si disponible
            logger.info("✅ Réentraînement réussi!")
        
        return results


# Instance globale
model_manager = ModelManager()
