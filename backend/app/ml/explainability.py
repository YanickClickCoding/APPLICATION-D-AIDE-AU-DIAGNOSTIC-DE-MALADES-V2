"""
Model Explainability Module
Explique les prédictions du modèle ML
Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
import logging

logger = logging.getLogger(__name__)


class ModelExplainer:
    """
    Classe pour expliquer les prédictions du modèle ML
    Implémente les Requirements 4.1 à 4.5
    """
    
    def __init__(self, model: Any, feature_names: List[str], class_names: Optional[List[str]] = None):
        """
        Initialise l'explainer
        
        Args:
            model: Modèle ML entraîné (RandomForest ou DecisionTree)
            feature_names: Noms des features
            class_names: Noms des classes (optionnel)
        """
        self.model = model
        self.feature_names = feature_names
        self.class_names = class_names or []
        
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Récupère l'importance des features du modèle
        
        Returns:
            Dictionnaire {feature_name: importance}
        """
        if hasattr(self.model, 'feature_importances_'):
            importances = self.model.feature_importances_
            return dict(zip(self.feature_names, importances))
        else:
            logger.warning("Le modèle ne supporte pas feature_importances_")
            return {}
    
    def get_top_features(self, n: int = 5) -> List[Tuple[str, float]]:
        """
        Récupère les N features les plus importantes
        
        Args:
            n: Nombre de features à retourner
            
        Returns:
            Liste de tuples (feature_name, importance) triée par importance décroissante
        """
        importance_dict = self.get_feature_importance()
        
        # Trier par importance décroissante
        sorted_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        # Retourner les top N
        top_n = sorted_features[:n]
        
        logger.info(f"Top {n} features: {[f[0] for f in top_n]}")
        
        return top_n
    
    def explain_prediction(self, X_instance: np.ndarray, 
                          prediction: Any,
                          prediction_proba: Optional[np.ndarray] = None) -> Dict:
        """
        Explique une prédiction individuelle
        
        Args:
            X_instance: Instance à expliquer (array 1D ou 2D)
            prediction: Prédiction du modèle
            prediction_proba: Probabilités de prédiction (optionnel)
            
        Returns:
            Dictionnaire contenant l'explication
        """
        # S'assurer que X_instance est 2D
        if X_instance.ndim == 1:
            X_instance = X_instance.reshape(1, -1)
        
        # Récupérer l'importance globale des features
        feature_importance = self.get_feature_importance()
        
        # Calculer l'impact de chaque feature pour cette instance
        feature_impacts = {}
        for i, feature_name in enumerate(self.feature_names):
            if i < X_instance.shape[1]:
                feature_value = X_instance[0, i]
                importance = feature_importance.get(feature_name, 0.0)
                
                # Impact = valeur * importance
                impact = float(feature_value * importance)
                feature_impacts[feature_name] = {
                    "value": float(feature_value),
                    "importance": float(importance),
                    "impact": impact
                }
        
        # Trier par impact absolu
        sorted_impacts = sorted(
            feature_impacts.items(),
            key=lambda x: abs(x[1]["impact"]),
            reverse=True
        )
        
        # Top features pour cette prédiction
        top_features_for_prediction = sorted_impacts[:5]
        
        explanation = {
            "prediction": str(prediction),
            "confidence": float(np.max(prediction_proba)) if prediction_proba is not None else None,
            "top_features": [
                {
                    "feature": feature,
                    "value": data["value"],
                    "importance": data["importance"],
                    "impact": data["impact"]
                }
                for feature, data in top_features_for_prediction
            ],
            "all_feature_impacts": feature_impacts
        }
        
        logger.info(f"Explication générée pour prédiction: {prediction}")
        
        return explanation
    
    def generate_text_explanation(self, explanation: Dict) -> str:
        """
        Génère une explication textuelle à partir d'un dictionnaire d'explication
        
        Args:
            explanation: Dictionnaire d'explication (retourné par explain_prediction)
            
        Returns:
            Explication textuelle formatée
        """
        lines = []
        
        # En-tête
        lines.append("=" * 70)
        lines.append("EXPLICATION DE LA PRÉDICTION")
        lines.append("=" * 70)
        
        # Prédiction
        prediction = explanation.get("prediction", "N/A")
        confidence = explanation.get("confidence")
        
        lines.append(f"\nDiagnostic prédit: {prediction}")
        if confidence is not None:
            lines.append(f"Confiance: {confidence * 100:.1f}%")
        
        # Top features
        lines.append("\n" + "-" * 70)
        lines.append("FACTEURS PRINCIPAUX DE LA DÉCISION")
        lines.append("-" * 70)
        
        top_features = explanation.get("top_features", [])
        
        if top_features:
            lines.append("\nLes 5 caractéristiques les plus influentes:")
            for i, feature_data in enumerate(top_features, 1):
                feature = feature_data["feature"]
                value = feature_data["value"]
                importance = feature_data["importance"]
                impact = feature_data["impact"]
                
                lines.append(f"\n{i}. {feature}")
                lines.append(f"   Valeur: {value:.2f}")
                lines.append(f"   Importance globale: {importance:.4f}")
                lines.append(f"   Impact sur cette prédiction: {impact:.4f}")
        else:
            lines.append("\nAucune information sur les features disponible.")
        
        # Interprétation
        lines.append("\n" + "-" * 70)
        lines.append("INTERPRÉTATION")
        lines.append("-" * 70)
        
        if top_features:
            most_important = top_features[0]
            lines.append(f"\nLa caractéristique la plus déterminante est '{most_important['feature']}'")
            lines.append(f"avec une valeur de {most_important['value']:.2f}.")
            
            if confidence is not None:
                if confidence > 0.8:
                    lines.append(f"\nLe modèle est très confiant ({confidence * 100:.1f}%) dans cette prédiction.")
                elif confidence > 0.6:
                    lines.append(f"\nLe modèle est modérément confiant ({confidence * 100:.1f}%) dans cette prédiction.")
                else:
                    lines.append(f"\nLe modèle a une confiance faible ({confidence * 100:.1f}%) dans cette prédiction.")
                    lines.append("Une validation médicale est fortement recommandée.")
        
        lines.append("\n" + "=" * 70)
        
        return "\n".join(lines)
    
    def find_similar_cases(self, X_instance: np.ndarray, 
                          X_train: np.ndarray,
                          y_train: np.ndarray,
                          n_similar: int = 5,
                          metric: str = 'euclidean') -> List[Dict]:
        """
        Trouve les cas similaires dans les données d'entraînement
        
        Args:
            X_instance: Instance à comparer
            X_train: Données d'entraînement
            y_train: Labels d'entraînement
            n_similar: Nombre de cas similaires à retourner
            metric: Métrique de distance ('euclidean' ou 'manhattan')
            
        Returns:
            Liste de dictionnaires contenant les cas similaires
        """
        # S'assurer que X_instance est 2D
        if X_instance.ndim == 1:
            X_instance = X_instance.reshape(1, -1)
        
        # Calculer les distances
        if metric == 'euclidean':
            distances = np.sqrt(np.sum((X_train - X_instance) ** 2, axis=1))
        elif metric == 'manhattan':
            distances = np.sum(np.abs(X_train - X_instance), axis=1)
        else:
            raise ValueError(f"Métrique inconnue: {metric}")
        
        # Trouver les indices des cas les plus similaires
        similar_indices = np.argsort(distances)[:n_similar]
        
        # Construire la liste des cas similaires
        similar_cases = []
        for idx in similar_indices:
            case = {
                "index": int(idx),
                "distance": float(distances[idx]),
                "label": str(y_train[idx]) if y_train is not None else None,
                "features": X_train[idx].tolist() if X_train.ndim > 1 else [float(X_train[idx])]
            }
            similar_cases.append(case)
        
        logger.info(f"Trouvé {len(similar_cases)} cas similaires (métrique: {metric})")
        
        return similar_cases
    
    def get_decision_path(self, X_instance: np.ndarray) -> Optional[List[str]]:
        """
        Récupère le chemin de décision dans l'arbre pour une instance
        
        Args:
            X_instance: Instance à expliquer
            
        Returns:
            Liste de conditions (règles) suivies dans l'arbre
        """
        # S'assurer que X_instance est 2D
        if X_instance.ndim == 1:
            X_instance = X_instance.reshape(1, -1)
        
        # Vérifier si le modèle est un arbre de décision
        if isinstance(self.model, DecisionTreeClassifier):
            tree = self.model
        elif isinstance(self.model, RandomForestClassifier):
            # Utiliser le premier arbre de la forêt
            tree = self.model.estimators_[0]
        else:
            logger.warning("Le modèle ne supporte pas l'extraction du chemin de décision")
            return None
        
        # Récupérer le chemin de décision
        decision_path = tree.decision_path(X_instance)
        node_indicator = decision_path.toarray()[0]
        
        # Récupérer les nœuds visités
        node_indices = np.where(node_indicator == 1)[0]
        
        # Construire les règles
        rules = []
        tree_ = tree.tree_
        
        for node_id in node_indices:
            # Si c'est une feuille, on s'arrête
            if tree_.feature[node_id] == -2:
                # Classe prédite
                class_idx = np.argmax(tree_.value[node_id])
                if self.class_names and class_idx < len(self.class_names):
                    class_name = self.class_names[class_idx]
                else:
                    class_name = f"Class_{class_idx}"
                rules.append(f"=> Prédiction: {class_name}")
                break
            
            # Récupérer la feature et le seuil
            feature_idx = tree_.feature[node_id]
            threshold = tree_.threshold[node_id]
            feature_name = self.feature_names[feature_idx] if feature_idx < len(self.feature_names) else f"Feature_{feature_idx}"
            
            # Valeur de la feature pour cette instance
            feature_value = X_instance[0, feature_idx]
            
            # Déterminer la direction
            if feature_value <= threshold:
                direction = "<="
            else:
                direction = ">"
            
            rule = f"{feature_name} {direction} {threshold:.2f} (valeur: {feature_value:.2f})"
            rules.append(rule)
        
        logger.info(f"Chemin de décision: {len(rules)} étapes")
        
        return rules
    
    def explain_with_decision_path(self, X_instance: np.ndarray,
                                   prediction: Any,
                                   prediction_proba: Optional[np.ndarray] = None) -> Dict:
        """
        Explication complète incluant le chemin de décision
        
        Args:
            X_instance: Instance à expliquer
            prediction: Prédiction du modèle
            prediction_proba: Probabilités de prédiction
            
        Returns:
            Dictionnaire d'explication complet
        """
        # Explication de base
        explanation = self.explain_prediction(X_instance, prediction, prediction_proba)
        
        # Ajouter le chemin de décision
        decision_path = self.get_decision_path(X_instance)
        if decision_path:
            explanation["decision_path"] = decision_path
        
        return explanation
    
    def compare_predictions(self, X_instance1: np.ndarray,
                           X_instance2: np.ndarray,
                           prediction1: Any,
                           prediction2: Any) -> Dict:
        """
        Compare deux prédictions et explique les différences
        
        Args:
            X_instance1: Première instance
            X_instance2: Deuxième instance
            prediction1: Prédiction pour instance 1
            prediction2: Prédiction pour instance 2
            
        Returns:
            Dictionnaire de comparaison
        """
        # S'assurer que les instances sont 2D
        if X_instance1.ndim == 1:
            X_instance1 = X_instance1.reshape(1, -1)
        if X_instance2.ndim == 1:
            X_instance2 = X_instance2.reshape(1, -1)
        
        # Calculer les différences de features
        feature_diffs = {}
        for i, feature_name in enumerate(self.feature_names):
            if i < X_instance1.shape[1] and i < X_instance2.shape[1]:
                value1 = X_instance1[0, i]
                value2 = X_instance2[0, i]
                diff = value2 - value1
                
                feature_diffs[feature_name] = {
                    "value1": float(value1),
                    "value2": float(value2),
                    "difference": float(diff),
                    "percent_change": float((diff / (value1 + 1e-10)) * 100)
                }
        
        # Trier par différence absolue
        sorted_diffs = sorted(
            feature_diffs.items(),
            key=lambda x: abs(x[1]["difference"]),
            reverse=True
        )
        
        comparison = {
            "prediction1": str(prediction1),
            "prediction2": str(prediction2),
            "predictions_differ": prediction1 != prediction2,
            "top_differences": [
                {
                    "feature": feature,
                    **data
                }
                for feature, data in sorted_diffs[:5]
            ],
            "all_differences": feature_diffs
        }
        
        logger.info(f"Comparaison: {prediction1} vs {prediction2}")
        
        return comparison


def demo_explainer():
    """
    Fonction de démonstration de l'explainer
    """
    from sklearn.datasets import load_iris
    from sklearn.ensemble import RandomForestClassifier
    
    # Charger des données de test
    iris = load_iris()
    X, y = iris.data, iris.target
    
    # Entraîner un modèle
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # Créer l'explainer
    explainer = ModelExplainer(
        model=model,
        feature_names=iris.feature_names,
        class_names=iris.target_names.tolist()
    )
    
    # Expliquer une prédiction
    X_test = X[0:1]
    prediction = model.predict(X_test)[0]
    prediction_proba = model.predict_proba(X_test)[0]
    
    explanation = explainer.explain_prediction(X_test, prediction, prediction_proba)
    
    print("Explication:")
    print(explainer.generate_text_explanation(explanation))
    
    # Trouver des cas similaires
    similar = explainer.find_similar_cases(X_test, X, y, n_similar=3)
    print("\nCas similaires:")
    for i, case in enumerate(similar, 1):
        print(f"{i}. Distance: {case['distance']:.2f}, Label: {case['label']}")


if __name__ == "__main__":
    demo_explainer()
