"""
Predictor Module (US-014, US-015, US-016)
Prédictions, score de confiance et explainabilité
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Predictor:
    """
    Classe pour faire des prédictions et expliquer les résultats
    Implémente les US-014, US-015, US-016
    """
    
    def __init__(self, model, label_encoder, feature_names: List[str]):
        self.model = model
        self.label_encoder = label_encoder
        self.feature_names = feature_names
    
    def predict(self, X: pd.DataFrame) -> Dict:
        """
        US-014: Prédiction pour un nouveau patient
        
        Retourne:
        - Diagnostic proposé
        - Score de confiance
        - Diagnostics alternatifs (2ème, 3ème choix)
        - Temps de prédiction
        """
        start_time = datetime.now()
        
        # Vérifier que les features correspondent
        if list(X.columns) != self.feature_names:
            logger.warning("⚠️ Les features ne correspondent pas exactement")
            # Réorganiser les colonnes
            X = X[self.feature_names]
        
        # Prédiction
        y_pred = self.model.predict(X)
        y_pred_proba = self.model.predict_proba(X)
        
        # Temps de prédiction
        prediction_time = (datetime.now() - start_time).total_seconds()
        
        # Diagnostic principal
        main_diagnosis_encoded = y_pred[0]
        main_diagnosis = self.label_encoder.inverse_transform([main_diagnosis_encoded])[0]
        main_confidence = float(y_pred_proba[0][main_diagnosis_encoded])
        
        # Top 3 diagnostics alternatifs
        top_3_indices = np.argsort(y_pred_proba[0])[-3:][::-1]
        alternatives = []
        
        for idx in top_3_indices:
            diagnosis = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(y_pred_proba[0][idx])
            alternatives.append({
                "diagnostic": diagnosis,
                "confiance": confidence
            })
        
        # Niveau de confiance (couleur)
        if main_confidence >= 0.80:
            confidence_level = "high"  # Vert
            confidence_color = "green"
        elif main_confidence >= 0.60:
            confidence_level = "medium"  # Jaune
            confidence_color = "yellow"
        else:
            confidence_level = "low"  # Rouge
            confidence_color = "red"
        
        result = {
            "diagnostic_propose": main_diagnosis,
            "confiance": main_confidence,
            "niveau_confiance": confidence_level,
            "couleur_confiance": confidence_color,
            "diagnostics_alternatifs": alternatives[1:],  # Exclure le principal
            "temps_prediction_secondes": prediction_time,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"🔮 Prédiction effectuée en {prediction_time:.3f}s")
        logger.info(f"   Diagnostic: {main_diagnosis}")
        logger.info(f"   Confiance: {main_confidence*100:.2f}% ({confidence_level})")
        
        return result
    
    def predict_with_alternatives(self, X: pd.DataFrame, top_n: int = 5) -> Dict:
        """
        Prédiction avec plus d'alternatives
        """
        prediction = self.predict(X)
        
        # Obtenir les top N diagnostics
        y_pred_proba = self.model.predict_proba(X)
        top_n_indices = np.argsort(y_pred_proba[0])[-top_n:][::-1]
        
        top_diagnostics = []
        for idx in top_n_indices:
            diagnosis = self.label_encoder.inverse_transform([idx])[0]
            confidence = float(y_pred_proba[0][idx])
            top_diagnostics.append({
                "diagnostic": diagnosis,
                "confiance": confidence,
                "pourcentage": f"{confidence*100:.2f}%"
            })
        
        prediction["top_diagnostics"] = top_diagnostics
        
        return prediction
    
    def calculate_confidence_score(self, X: pd.DataFrame) -> Dict:
        """
        US-015: Calcul détaillé du score de confiance
        
        Explique comment le score est calculé:
        - % des arbres qui votent pour ce diagnostic
        - Nombre d'arbres en accord/désaccord
        """
        y_pred_proba = self.model.predict_proba(X)
        y_pred = self.model.predict(X)
        
        main_diagnosis_idx = y_pred[0]
        main_confidence = y_pred_proba[0][main_diagnosis_idx]
        
        # Nombre d'arbres dans la forêt
        n_estimators = self.model.n_estimators
        
        # Estimation du nombre d'arbres qui votent pour ce diagnostic
        # (approximation basée sur la probabilité)
        trees_agree = int(main_confidence * n_estimators)
        trees_disagree = n_estimators - trees_agree
        
        confidence_details = {
            "score_confiance": float(main_confidence),
            "pourcentage": f"{main_confidence*100:.2f}%",
            "nombre_arbres_total": n_estimators,
            "arbres_en_accord": trees_agree,
            "arbres_en_desaccord": trees_disagree,
            "explication": f"{trees_agree}/{n_estimators} arbres prédisent ce diagnostic"
        }
        
        # Niveau de confiance avec seuils
        if main_confidence >= 0.80:
            confidence_details["niveau"] = "Très fiable"
            confidence_details["couleur"] = "green"
            confidence_details["recommandation"] = "Diagnostic fiable, peut être validé"
        elif main_confidence >= 0.60:
            confidence_details["niveau"] = "À vérifier"
            confidence_details["couleur"] = "yellow"
            confidence_details["recommandation"] = "Vérifier avec examens complémentaires"
        else:
            confidence_details["niveau"] = "Faible confiance"
            confidence_details["couleur"] = "red"
            confidence_details["recommandation"] = "Données insuffisantes, examens nécessaires"
        
        return confidence_details
    
    def explain_prediction(self, X: pd.DataFrame, top_features: int = 5) -> Dict:
        """
        US-016: Explainabilité du diagnostic
        
        Explique POURQUOI le système propose ce diagnostic:
        - Top 5 symptômes/analyses les plus importants
        - Impact de chaque feature sur le diagnostic
        - Règles de décision simples
        """
        # Prédiction
        prediction = self.predict(X)
        
        # Importance des features pour ce modèle
        feature_importances = self.model.feature_importances_
        
        # Trier par importance
        indices = np.argsort(feature_importances)[::-1][:top_features]
        
        # Valeurs du patient pour ces features
        patient_values = X.iloc[0]
        
        important_features = []
        for idx in indices:
            feature_name = self.feature_names[idx]
            importance = float(feature_importances[idx])
            patient_value = float(patient_values[feature_name])
            
            # Déterminer l'impact (simplifié)
            if patient_value > 0.5:  # Valeur normalisée
                impact = "Augmente"
                impact_symbol = "↑"
            else:
                impact = "Diminue"
                impact_symbol = "↓"
            
            important_features.append({
                "feature": feature_name,
                "importance": importance,
                "valeur_patient": patient_value,
                "impact": impact,
                "impact_symbol": impact_symbol,
                "explication": f"{feature_name} = {patient_value:.2f} {impact_symbol} {importance*100:.1f}% d'influence"
            })
        
        # Règles simples (exemples)
        rules = self._generate_simple_rules(X, prediction["diagnostic_propose"])
        
        explanation = {
            "diagnostic": prediction["diagnostic_propose"],
            "confiance": prediction["confiance"],
            "features_importantes": important_features,
            "regles_decision": rules,
            "resume": f"Le diagnostic '{prediction['diagnostic_propose']}' est basé principalement sur: " +
                     ", ".join([f["feature"] for f in important_features[:3]])
        }
        
        logger.info(f"💡 Explication générée pour: {prediction['diagnostic_propose']}")
        
        return explanation
    
    def _generate_simple_rules(self, X: pd.DataFrame, diagnosis: str) -> List[str]:
        """
        Génère des règles de décision simples et compréhensibles
        """
        rules = []
        patient_values = X.iloc[0]
        
        # Exemples de règles (à adapter selon les features)
        # Ces règles sont simplifiées pour la démonstration
        
        # Règle 1: Température
        if 'temperature' in patient_values.index:
            temp = patient_values['temperature']
            if temp > 0.7:  # Normalisé
                rules.append("Température élevée détectée")
        
        # Règle 2: Saturation O2
        if 'saturation_o2' in patient_values.index:
            sat_o2 = patient_values['saturation_o2']
            if sat_o2 < 0.5:
                rules.append("Saturation en oxygène basse")
        
        # Règle 3: Symptômes multiples
        symptom_cols = [col for col in patient_values.index if 'symptom' in col.lower() or 'fievre' in col.lower() or 'toux' in col.lower()]
        active_symptoms = sum([patient_values[col] > 0.5 for col in symptom_cols if col in patient_values.index])
        
        if active_symptoms >= 3:
            rules.append(f"{active_symptoms} symptômes actifs détectés")
        
        # Si aucune règle, ajouter une règle générique
        if not rules:
            rules.append("Combinaison de plusieurs facteurs cliniques")
        
        return rules
    
    def compare_with_previous(
        self, 
        current_X: pd.DataFrame, 
        previous_prediction: Dict
    ) -> Dict:
        """
        US-018: Comparaison avec prédiction précédente
        
        Compare la prédiction actuelle avec une précédente
        """
        # Prédiction actuelle
        current_prediction = self.predict(current_X)
        
        # Comparaison
        diagnosis_changed = current_prediction["diagnostic_propose"] != previous_prediction["diagnostic_propose"]
        confidence_change = current_prediction["confiance"] - previous_prediction["confiance"]
        
        comparison = {
            "prediction_actuelle": current_prediction,
            "prediction_precedente": previous_prediction,
            "diagnostic_change": diagnosis_changed,
            "changement_confiance": float(confidence_change),
            "changement_confiance_pourcent": f"{confidence_change*100:+.2f}%"
        }
        
        # Alerte si changement drastique
        if diagnosis_changed:
            if "Grippe" in previous_prediction["diagnostic_propose"] and "Pneumonie" in current_prediction["diagnostic_propose"]:
                comparison["alerte"] = "⚠️ Changement drastique: Grippe → Pneumonie"
                comparison["recommandation"] = "Examens complémentaires urgents recommandés"
        
        # Explication du changement
        if diagnosis_changed:
            comparison["explication"] = f"Le diagnostic a changé de '{previous_prediction['diagnostic_propose']}' à '{current_prediction['diagnostic_propose']}'"
        else:
            if abs(confidence_change) > 0.1:
                comparison["explication"] = f"Le diagnostic reste '{current_prediction['diagnostic_propose']}' mais la confiance a {'augmenté' if confidence_change > 0 else 'diminué'}"
            else:
                comparison["explication"] = "Diagnostic stable"
        
        return comparison
    
    def batch_predict(self, X: pd.DataFrame) -> List[Dict]:
        """
        Prédictions pour plusieurs patients en batch
        """
        predictions = []
        
        for idx in range(len(X)):
            patient_data = X.iloc[[idx]]
            prediction = self.predict(patient_data)
            prediction["patient_index"] = idx
            predictions.append(prediction)
        
        logger.info(f"📊 {len(predictions)} prédictions effectuées en batch")
        
        return predictions
