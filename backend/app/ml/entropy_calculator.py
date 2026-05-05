"""
Entropy Calculator Module
Calcul de l'entropie, gain d'information et importance des features
Requirements: 3.1, 3.2, 3.3, 3.5
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from sklearn.tree import DecisionTreeClassifier, _tree
import logging

logger = logging.getLogger(__name__)


class EntropyCalculator:
    """
    Classe pour calculer l'entropie et le gain d'information des features
    Implémente les Requirements 3.1 à 3.5
    """
    
    def __init__(self):
        self.feature_importance: Dict[str, float] = {}
        self.information_gains: Dict[str, float] = {}
        
    def calculate_entropy(self, y: pd.Series) -> float:
        """
        Calcule l'entropie d'une variable cible
        
        Formule: H(S) = -Σ p(x) * log2(p(x))
        
        Args:
            y: Série contenant les labels de classe
            
        Returns:
            Entropie (valeur entre 0 et log2(n_classes))
        """
        if len(y) == 0:
            return 0.0
        
        # Calculer les probabilités de chaque classe
        value_counts = y.value_counts()
        probabilities = value_counts / len(y)
        
        # Calculer l'entropie
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))
        
        return float(entropy)
    
    def calculate_conditional_entropy(self, X_feature: pd.Series, y: pd.Series) -> float:
        """
        Calcule l'entropie conditionnelle H(Y|X)
        
        Args:
            X_feature: Feature pour laquelle calculer l'entropie conditionnelle
            y: Variable cible
            
        Returns:
            Entropie conditionnelle
        """
        conditional_entropy = 0.0
        
        # Pour chaque valeur unique de la feature
        for value in X_feature.unique():
            # Filtrer les données pour cette valeur
            mask = X_feature == value
            y_subset = y[mask]
            
            # Probabilité de cette valeur
            p_value = len(y_subset) / len(y)
            
            # Entropie de ce sous-ensemble
            entropy_subset = self.calculate_entropy(y_subset)
            
            # Ajouter à l'entropie conditionnelle pondérée
            conditional_entropy += p_value * entropy_subset
        
        return conditional_entropy
    
    def calculate_information_gain(self, X_feature: pd.Series, y: pd.Series) -> float:
        """
        Calcule le gain d'information pour une feature
        
        Formule: IG(Y, X) = H(Y) - H(Y|X)
        
        Args:
            X_feature: Feature pour laquelle calculer le gain
            y: Variable cible
            
        Returns:
            Gain d'information
        """
        # Entropie avant le split
        entropy_before = self.calculate_entropy(y)
        
        # Entropie après le split (conditionnelle)
        entropy_after = self.calculate_conditional_entropy(X_feature, y)
        
        # Gain d'information
        information_gain = entropy_before - entropy_after
        
        return float(information_gain)
    
    def calculate_all_information_gains(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Calcule le gain d'information pour toutes les features
        
        Args:
            X: DataFrame des features
            y: Variable cible
            
        Returns:
            Dictionnaire {feature_name: information_gain}
        """
        information_gains = {}
        
        for column in X.columns:
            try:
                ig = self.calculate_information_gain(X[column], y)
                information_gains[column] = ig
            except Exception as e:
                logger.warning(f"Erreur calcul IG pour {column}: {e}")
                information_gains[column] = 0.0
        
        self.information_gains = information_gains
        logger.info(f"Gains d'information calculés pour {len(information_gains)} features")
        
        return information_gains
    
    def rank_features_by_importance(self, X: pd.DataFrame, y: pd.Series, 
                                    method: str = 'information_gain') -> List[Tuple[str, float]]:
        """
        Classe les features par ordre d'importance
        
        Args:
            X: DataFrame des features
            y: Variable cible
            method: Méthode de calcul ('information_gain' ou 'tree_importance')
            
        Returns:
            Liste de tuples (feature_name, importance) triée par importance décroissante
        """
        if method == 'information_gain':
            # Calculer les gains d'information
            importance_dict = self.calculate_all_information_gains(X, y)
        
        elif method == 'tree_importance':
            # Utiliser l'importance des features d'un arbre de décision
            tree = DecisionTreeClassifier(criterion='entropy', random_state=42)
            tree.fit(X, y)
            importance_dict = dict(zip(X.columns, tree.feature_importances_))
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
        
        # Trier par importance décroissante
        ranked_features = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        self.feature_importance = dict(ranked_features)
        
        logger.info(f"Features classées par {method}")
        logger.info(f"Top 5: {ranked_features[:5]}")
        
        return ranked_features
    
    def extract_decision_rules(self, tree: DecisionTreeClassifier, 
                               feature_names: List[str],
                               class_names: Optional[List[str]] = None,
                               max_depth: int = 3) -> List[str]:
        """
        Extrait les règles de décision d'un arbre de décision
        
        Args:
            tree: Arbre de décision entraîné
            feature_names: Noms des features
            class_names: Noms des classes (optionnel)
            max_depth: Profondeur maximale des règles à extraire
            
        Returns:
            Liste de règles de décision sous forme de strings
        """
        tree_ = tree.tree_
        feature_name = [
            feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
            for i in tree_.feature
        ]
        
        rules = []
        
        def recurse(node, depth, conditions):
            """Fonction récursive pour parcourir l'arbre"""
            if depth > max_depth:
                return
            
            # Si c'est une feuille
            if tree_.feature[node] == _tree.TREE_UNDEFINED:
                # Classe prédite
                class_idx = np.argmax(tree_.value[node])
                if class_names:
                    class_name = class_names[class_idx]
                else:
                    class_name = f"Class_{class_idx}"
                
                # Construire la règle
                rule = " AND ".join(conditions) + f" => {class_name}"
                rules.append(rule)
                return
            
            # Nœud de décision
            feature = feature_name[node]
            threshold = tree_.threshold[node]
            
            # Branche gauche (<=)
            left_conditions = conditions + [f"{feature} <= {threshold:.2f}"]
            recurse(tree_.children_left[node], depth + 1, left_conditions)
            
            # Branche droite (>)
            right_conditions = conditions + [f"{feature} > {threshold:.2f}"]
            recurse(tree_.children_right[node], depth + 1, right_conditions)
        
        # Démarrer la récursion depuis la racine
        recurse(0, 0, [])
        
        logger.info(f"Extraction de {len(rules)} règles de décision (max_depth={max_depth})")
        
        return rules
    
    def get_feature_splits(self, tree: DecisionTreeClassifier, 
                          feature_names: List[str]) -> Dict[str, List[float]]:
        """
        Récupère les seuils de split pour chaque feature dans l'arbre
        
        Args:
            tree: Arbre de décision entraîné
            feature_names: Noms des features
            
        Returns:
            Dictionnaire {feature_name: [thresholds]}
        """
        tree_ = tree.tree_
        splits = {name: [] for name in feature_names}
        
        for node in range(tree_.node_count):
            if tree_.feature[node] != _tree.TREE_UNDEFINED:
                feature_idx = tree_.feature[node]
                feature_name = feature_names[feature_idx]
                threshold = tree_.threshold[node]
                splits[feature_name].append(threshold)
        
        # Trier les seuils
        for feature in splits:
            splits[feature] = sorted(splits[feature])
        
        return splits
    
    def analyze_feature_importance_with_entropy(self, X: pd.DataFrame, y: pd.Series) -> Dict:
        """
        Analyse complète de l'importance des features avec entropie
        
        Returns:
            Dictionnaire contenant:
            - entropy_before: Entropie initiale
            - information_gains: Gains d'information par feature
            - ranked_features: Features classées par importance
            - top_features: Top 10 features
        """
        # Entropie initiale
        entropy_before = self.calculate_entropy(y)
        
        # Gains d'information
        information_gains = self.calculate_all_information_gains(X, y)
        
        # Classement
        ranked_features = self.rank_features_by_importance(X, y, method='information_gain')
        
        # Top features
        top_features = ranked_features[:10]
        
        analysis = {
            "entropy_before": float(entropy_before),
            "information_gains": information_gains,
            "ranked_features": ranked_features,
            "top_features": top_features,
            "n_features": len(X.columns)
        }
        
        logger.info(f"Analyse complète: entropie={entropy_before:.4f}, {len(X.columns)} features")
        
        return analysis
    
    def get_entropy_report(self, X: pd.DataFrame, y: pd.Series) -> str:
        """
        Génère un rapport textuel sur l'entropie et l'importance des features
        
        Returns:
            Rapport formaté en string
        """
        analysis = self.analyze_feature_importance_with_entropy(X, y)
        
        report = []
        report.append("=" * 60)
        report.append("RAPPORT D'ANALYSE D'ENTROPIE ET GAIN D'INFORMATION")
        report.append("=" * 60)
        report.append(f"\nEntropie initiale: {analysis['entropy_before']:.4f}")
        report.append(f"Nombre de features: {analysis['n_features']}")
        report.append(f"Nombre de classes: {len(y.unique())}")
        report.append("\n" + "-" * 60)
        report.append("TOP 10 FEATURES PAR GAIN D'INFORMATION")
        report.append("-" * 60)
        
        for i, (feature, gain) in enumerate(analysis['top_features'], 1):
            report.append(f"{i:2d}. {feature:40s} | IG = {gain:.6f}")
        
        report.append("=" * 60)
        
        return "\n".join(report)


def demo_entropy_calculator():
    """
    Fonction de démonstration du calculateur d'entropie
    """
    # Créer des données de test
    np.random.seed(42)
    n_samples = 100
    
    X = pd.DataFrame({
        'feature1': np.random.randn(n_samples),
        'feature2': np.random.randn(n_samples),
        'feature3': np.random.choice([0, 1, 2], n_samples)
    })
    
    y = pd.Series(np.random.choice(['A', 'B', 'C'], n_samples))
    
    # Calculer l'entropie
    calc = EntropyCalculator()
    
    print("Entropie de y:", calc.calculate_entropy(y))
    print("\nGains d'information:")
    for feature in X.columns:
        ig = calc.calculate_information_gain(X[feature], y)
        print(f"  {feature}: {ig:.4f}")
    
    print("\nRapport complet:")
    print(calc.get_entropy_report(X, y))


if __name__ == "__main__":
    demo_entropy_calculator()
