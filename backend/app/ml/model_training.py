"""
Model Training Module (US-012, US-013)
Entraînement et évaluation du modèle Random Forest
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, 
    classification_report, 
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score
)
from sklearn.preprocessing import LabelEncoder
import joblib
import json
import logging
from datetime import datetime
from typing import Dict, Tuple, Optional
import os

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Classe pour l'entraînement du modèle de diagnostic
    Implémente les US-012 et US-013
    """
    
    def __init__(self, model_path: str = "./ml_models/"):
        self.model: Optional[RandomForestClassifier] = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.model_path = model_path
        self.training_history = {}
        self.normalization_params: Dict = {}
        self.dataset_means: Dict = {}

        # Créer le dossier si nécessaire
        os.makedirs(model_path, exist_ok=True)
    
    def train(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        n_estimators: int = 100,
        max_depth: int = 20,
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict:
        """
        US-012: Entraînement du modèle initial
        
        Args:
            X: Features (données d'entrée)
            y: Target (diagnostics)
            n_estimators: Nombre d'arbres dans la forêt
            max_depth: Profondeur maximale des arbres
            test_size: Proportion du jeu de test (0.2 = 20%)
            random_state: Seed pour reproductibilité
        
        Returns:
            Dict avec les métriques d'entraînement
        """
        start_time = datetime.now()
        logger.info(f"🚀 Début de l'entraînement du modèle...")
        logger.info(f"   Données: {X.shape[0]} cas, {X.shape[1]} features")
        logger.info(f"   Maladies: {len(y.unique())} classes différentes")
        
        # Vérifier le minimum de données
        if len(X) < 500:
            logger.warning(f"⚠️ Seulement {len(X)} cas (minimum recommandé: 500)")
        
        # Encoder les labels (diagnostics)
        y_encoded = self.label_encoder.fit_transform(y)
        
        # Diviser les données (80% train, 20% test)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, 
            test_size=test_size, 
            random_state=random_state,
            stratify=y_encoded  # Garder la même distribution
        )
        
        logger.info(f"   Train: {len(X_train)} cas | Test: {len(X_test)} cas")
        
        # Créer le modèle Random Forest avec entropie (US-012)
        #
        # class_weight='balanced' : compense les effectifs inégaux par classe
        # (6 à 105 cas selon la maladie) pour ne pas écraser les maladies à faible
        # volume. Le modèle est entraîné uniquement sur les features symptômes
        # (les colonnes Lab_/Vital_ bruitées du dataset sont exclues en amont, dans
        # train_new_model), ce qui permet à une maladie aux symptômes distinctifs
        # de ressortir avec une confiance élevée (90 %+).
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            criterion='entropy',  # Utilisation de l'entropie comme demandé
            class_weight='balanced',
            random_state=random_state,
            n_jobs=-1,  # Utiliser tous les CPU
            verbose=0
        )
        
        # Entraîner le modèle
        logger.info(f"   Entraînement avec {n_estimators} arbres...")
        self.model.fit(X_train, y_train)
        
        # Calculer le temps d'entraînement
        training_duration = (datetime.now() - start_time).total_seconds()
        
        # Évaluer sur le jeu de test
        y_pred = self.model.predict(X_test)
        accuracy  = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall    = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1        = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        logger.info(f"Modele entraine avec succes!")
        logger.info(f"   Accuracy  : {accuracy * 100:.2f}%")
        logger.info(f"   Precision : {precision * 100:.2f}%")
        logger.info(f"   Recall    : {recall * 100:.2f}%")
        logger.info(f"   F1-Score  : {f1 * 100:.2f}%")
        logger.info(f"   Duree     : {training_duration:.2f} secondes")

        # Sauvegarder les feature names
        self.feature_names = X.columns.tolist()

        # Historique d'entraînement
        self.training_history = {
            "date": datetime.now().isoformat(),
            "n_samples": len(X),
            "n_features": len(self.feature_names),
            "n_classes": len(self.label_encoder.classes_),
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "test_size": test_size,
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "training_duration_seconds": training_duration
        }
        
        return self.training_history
    
    def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        US-013: Évaluation complète du modèle
        
        Retourne:
        - Précision globale (accuracy)
        - Précision par diagnostic
        - Sensibilité (recall)
        - Spécificité
        - F1-score
        - Matrice de confusion
        """
        if self.model is None:
            raise ValueError("Modèle non entraîné. Appelez train() d'abord.")
        
        logger.info("📊 Évaluation du modèle...")
        
        # Encoder les labels
        y_test_encoded = self.label_encoder.transform(y_test)
        
        # Prédictions
        y_pred = self.model.predict(X_test)
        y_pred_proba = self.model.predict_proba(X_test)
        
        # Métriques globales
        accuracy = accuracy_score(y_test_encoded, y_pred)
        precision = precision_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        f1 = f1_score(y_test_encoded, y_pred, average='weighted', zero_division=0)
        
        # Matrice de confusion
        conf_matrix = confusion_matrix(y_test_encoded, y_pred)
        
        # Rapport de classification (par classe)
        class_report = classification_report(
            y_test_encoded, 
            y_pred, 
            target_names=self.label_encoder.classes_,
            output_dict=True,
            zero_division=0
        )
        
        # Vérifier si le modèle est acceptable (>80%)
        if accuracy < 0.80:
            logger.warning(f"⚠️ Précision faible: {accuracy*100:.2f}% (seuil: 80%)")
            logger.warning("   Le modèle devrait être amélioré avant utilisation.")
        else:
            logger.info(f"✅ Modèle acceptable: {accuracy*100:.2f}%")
        
        evaluation_results = {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1),
            "confusion_matrix": conf_matrix.tolist(),
            "classification_report": class_report,
            "acceptable": accuracy >= 0.80
        }
        
        logger.info(f"   Accuracy:  {accuracy*100:.2f}%")
        logger.info(f"   Precision: {precision*100:.2f}%")
        logger.info(f"   Recall:    {recall*100:.2f}%")
        logger.info(f"   F1-Score:  {f1*100:.2f}%")
        
        return evaluation_results
    
    def cross_validate(self, X: pd.DataFrame, y: pd.Series, cv: int = 5) -> Dict:
        """
        Validation croisée pour évaluer la robustesse du modèle
        """
        if self.model is None:
            raise ValueError("Modèle non entraîné. Appelez train() d'abord.")
        
        logger.info(f"🔄 Validation croisée ({cv}-fold)...")
        
        y_encoded = self.label_encoder.transform(y)
        
        scores = cross_val_score(
            self.model, X, y_encoded, 
            cv=cv, 
            scoring='accuracy',
            n_jobs=-1
        )
        
        cv_results = {
            "cv_scores": scores.tolist(),
            "mean_score": float(scores.mean()),
            "std_score": float(scores.std()),
            "min_score": float(scores.min()),
            "max_score": float(scores.max())
        }
        
        logger.info(f"   Score moyen: {scores.mean()*100:.2f}% (±{scores.std()*100:.2f}%)")
        
        return cv_results
    
    def get_feature_importance(self, top_n: int = 15) -> Dict:
        """
        Retourne l'importance des features (symptômes/analyses)
        Utile pour US-016 (Explainabilité)
        """
        if self.model is None:
            raise ValueError("Modèle non entraîné.")
        
        importances = self.model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        feature_importance = {
            "features": [self.feature_names[i] for i in indices],
            "importances": [float(importances[i]) for i in indices]
        }
        
        logger.info(f"📈 Top {top_n} features les plus importantes:")
        for i, (feat, imp) in enumerate(zip(feature_importance["features"], feature_importance["importances"]), 1):
            logger.info(f"   {i}. {feat}: {imp:.4f}")
        
        return feature_importance
    
    def save_model(self, version: str = "1.0") -> str:
        """
        Sauvegarde le modèle entraîné
        
        Sauvegarde:
        - Le modèle Random Forest
        - Le label encoder
        - Les feature names
        - L'historique d'entraînement
        """
        if self.model is None:
            raise ValueError("Aucun modèle à sauvegarder.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_filename = f"random_forest_v{version}_{timestamp}.joblib"
        model_filepath = os.path.join(self.model_path, model_filename)
        
        # Sauvegarder le modèle et les métadonnées
        model_data = {
            "model": self.model,
            "label_encoder": self.label_encoder,
            "feature_names": self.feature_names,
            "training_history": self.training_history,
            "normalization_params": self.normalization_params,
            "dataset_means": self.dataset_means,
            "version": version,
            "saved_at": datetime.now().isoformat()
        }
        
        joblib.dump(model_data, model_filepath)
        
        # Sauvegarder aussi les métadonnées en JSON
        metadata_filepath = model_filepath.replace(".joblib", "_metadata.json")
        with open(metadata_filepath, 'w', encoding='utf-8') as f:
            json.dump({
                "version": version,
                "training_history": self.training_history,
                "feature_names": self.feature_names,
                "classes": self.label_encoder.classes_.tolist(),
                "saved_at": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Modèle sauvegardé: {model_filepath}")
        logger.info(f"💾 Métadonnées sauvegardées: {metadata_filepath}")
        
        return model_filepath
    
    def load_model(self, filepath: str) -> None:
        """
        Charge un modèle précédemment entraîné
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Modèle introuvable: {filepath}")
        
        logger.info(f"📂 Chargement du modèle: {filepath}")
        
        model_data = joblib.load(filepath)
        
        self.model = model_data["model"]
        self.label_encoder = model_data["label_encoder"]
        self.feature_names = model_data["feature_names"]
        self.training_history = model_data.get("training_history", {})
        self.normalization_params = model_data.get("normalization_params", {})
        self.dataset_means = model_data.get("dataset_means", {})
        
        logger.info(f"✅ Modèle chargé avec succès!")
        logger.info(f"   Version: {model_data.get('version', 'unknown')}")
        logger.info(f"   Classes: {len(self.label_encoder.classes_)}")
        logger.info(f"   Features: {len(self.feature_names)}")
    
    def compare_models(self, other_model_path: str, X_test: pd.DataFrame, y_test: pd.Series) -> Dict:
        """
        Compare le modèle actuel avec un autre modèle
        Utile pour US-028 (Réentraînement)
        """
        # Sauvegarder le modèle actuel temporairement
        current_model = self.model
        current_encoder = self.label_encoder
        
        # Évaluer le modèle actuel
        current_eval = self.evaluate(X_test, y_test)
        
        # Charger l'autre modèle
        self.load_model(other_model_path)
        other_eval = self.evaluate(X_test, y_test)
        
        # Restaurer le modèle actuel
        self.model = current_model
        self.label_encoder = current_encoder
        
        comparison = {
            "current_model": {
                "accuracy": current_eval["accuracy"],
                "f1_score": current_eval["f1_score"]
            },
            "other_model": {
                "accuracy": other_eval["accuracy"],
                "f1_score": other_eval["f1_score"]
            },
            "improvement": {
                "accuracy": current_eval["accuracy"] - other_eval["accuracy"],
                "f1_score": current_eval["f1_score"] - other_eval["f1_score"]
            },
            "current_is_better": current_eval["accuracy"] > other_eval["accuracy"]
        }
        
        logger.info("🔄 Comparaison des modèles:")
        logger.info(f"   Modèle actuel:  {current_eval['accuracy']*100:.2f}%")
        logger.info(f"   Autre modèle:   {other_eval['accuracy']*100:.2f}%")
        logger.info(f"   Amélioration:   {comparison['improvement']['accuracy']*100:+.2f}%")
        
        return comparison
