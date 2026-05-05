"""
Chart Generator Module
Génération de graphiques avec Matplotlib et Seaborn
Requirements: 9.1-9.9
"""
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

from . import save_figure

logger = logging.getLogger(__name__)


class ChartGenerator:
    """
    Générateur de graphiques pour le système médical
    Implémente les Requirements 9.1 à 9.9
    """
    
    def __init__(self):
        """Initialise le générateur de graphiques"""
        pass
    
    def plot_patient_timeline(self, 
                             patient_data: pd.DataFrame,
                             patient_id: int,
                             save: bool = True) -> Optional[str]:
        """
        Génère une timeline des symptômes et analyses d'un patient
        
        Args:
            patient_data: DataFrame avec colonnes [date, symptom, value]
            patient_id: ID du patient
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if not patient_data.empty and 'date' in patient_data.columns:
            # Convertir les dates
            patient_data['date'] = pd.to_datetime(patient_data['date'])
            
            # Tracer les lignes pour chaque symptôme/analyse
            for column in patient_data.columns:
                if column != 'date':
                    ax.plot(patient_data['date'], patient_data[column], 
                           marker='o', label=column, linewidth=2)
            
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Valeur', fontsize=12)
            ax.set_title(f'Timeline Patient #{patient_id}', fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"patient_timeline_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Timeline patient sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_diagnosis_distribution(self,
                                   diagnosis_counts: Dict[str, int],
                                   save: bool = True) -> Optional[str]:
        """
        Génère un graphique en barres de la distribution des diagnostics
        
        Args:
            diagnosis_counts: Dictionnaire {diagnostic: count}
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if diagnosis_counts:
            # Trier par count décroissant
            sorted_data = sorted(diagnosis_counts.items(), key=lambda x: x[1], reverse=True)
            diagnoses = [item[0] for item in sorted_data[:15]]  # Top 15
            counts = [item[1] for item in sorted_data[:15]]
            
            # Créer le graphique en barres
            bars = ax.bar(range(len(diagnoses)), counts, color='steelblue', alpha=0.8)
            
            # Ajouter les valeurs sur les barres
            for i, (bar, count) in enumerate(zip(bars, counts)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       str(count), ha='center', va='bottom', fontsize=10)
            
            ax.set_xlabel('Diagnostic', fontsize=12)
            ax.set_ylabel('Nombre de cas', fontsize=12)
            ax.set_title('Distribution des Diagnostics', fontsize=14, fontweight='bold')
            ax.set_xticks(range(len(diagnoses)))
            ax.set_xticklabels(diagnoses, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"diagnosis_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Distribution diagnostics sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_correlation_heatmap(self,
                                correlation_matrix: pd.DataFrame,
                                save: bool = True) -> Optional[str]:
        """
        Génère une heatmap de corrélation des symptômes
        
        Args:
            correlation_matrix: Matrice de corrélation
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(12, 10))
        
        if not correlation_matrix.empty:
            # Créer la heatmap avec Seaborn
            sns.heatmap(correlation_matrix, 
                       annot=True, 
                       fmt='.2f',
                       cmap='coolwarm',
                       center=0,
                       square=True,
                       linewidths=0.5,
                       cbar_kws={"shrink": 0.8},
                       ax=ax)
            
            ax.set_title('Heatmap de Corrélation des Symptômes', 
                        fontsize=14, fontweight='bold', pad=20)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"correlation_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Heatmap corrélation sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_model_performance(self,
                              performance_history: List[Dict],
                              save: bool = True) -> Optional[str]:
        """
        Génère une courbe de performance du modèle dans le temps
        
        Args:
            performance_history: Liste de {date, accuracy, precision, recall}
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if performance_history:
            df = pd.DataFrame(performance_history)
            df['date'] = pd.to_datetime(df['date'])
            
            # Tracer les métriques
            ax.plot(df['date'], df['accuracy'], marker='o', label='Accuracy', linewidth=2)
            if 'precision' in df.columns:
                ax.plot(df['date'], df['precision'], marker='s', label='Precision', linewidth=2)
            if 'recall' in df.columns:
                ax.plot(df['date'], df['recall'], marker='^', label='Recall', linewidth=2)
            
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Score', fontsize=12)
            ax.set_title('Performance du Modèle ML', fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_ylim([0, 1])
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"model_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Performance modèle sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_confusion_matrix(self,
                             confusion_matrix: np.ndarray,
                             class_names: List[str],
                             save: bool = True) -> Optional[str]:
        """
        Génère une matrice de confusion colorée
        
        Args:
            confusion_matrix: Matrice de confusion numpy
            class_names: Noms des classes
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if confusion_matrix is not None and len(confusion_matrix) > 0:
            # Créer la heatmap
            sns.heatmap(confusion_matrix,
                       annot=True,
                       fmt='d',
                       cmap='Blues',
                       xticklabels=class_names,
                       yticklabels=class_names,
                       cbar_kws={"shrink": 0.8},
                       ax=ax)
            
            ax.set_xlabel('Prédiction', fontsize=12)
            ax.set_ylabel('Réalité', fontsize=12)
            ax.set_title('Matrice de Confusion', fontsize=14, fontweight='bold')
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"confusion_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Matrice confusion sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_age_distribution_by_diagnosis(self,
                                          data: pd.DataFrame,
                                          save: bool = True) -> Optional[str]:
        """
        Génère des boxplots de distribution d'âge par diagnostic
        
        Args:
            data: DataFrame avec colonnes [diagnosis, age]
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(14, 6))
        
        if not data.empty and 'diagnosis' in data.columns and 'age' in data.columns:
            # Créer le boxplot avec Seaborn
            sns.boxplot(data=data, x='diagnosis', y='age', palette='Set2', ax=ax)
            
            ax.set_xlabel('Diagnostic', fontsize=12)
            ax.set_ylabel('Âge', fontsize=12)
            ax.set_title('Distribution d\'Âge par Diagnostic', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"age_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Distribution âge sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_feature_importance(self,
                               feature_importance: Dict[str, float],
                               top_n: int = 20,
                               save: bool = True) -> Optional[str]:
        """
        Génère un graphique en barres horizontales de l'importance des features
        
        Args:
            feature_importance: Dictionnaire {feature: importance}
            top_n: Nombre de features à afficher
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        if feature_importance:
            # Trier et prendre les top N
            sorted_features = sorted(feature_importance.items(), 
                                   key=lambda x: x[1], 
                                   reverse=True)[:top_n]
            features = [item[0] for item in sorted_features]
            importances = [item[1] for item in sorted_features]
            
            # Créer le graphique en barres horizontales
            y_pos = np.arange(len(features))
            bars = ax.barh(y_pos, importances, color='teal', alpha=0.8)
            
            # Ajouter les valeurs
            for i, (bar, imp) in enumerate(zip(bars, importances)):
                ax.text(bar.get_width() + 0.001, bar.get_y() + bar.get_height()/2,
                       f'{imp:.4f}', va='center', fontsize=9)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(features)
            ax.set_xlabel('Importance', fontsize=12)
            ax.set_title(f'Top {top_n} Features Importantes', fontsize=14, fontweight='bold')
            ax.grid(axis='x', alpha=0.3)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"feature_importance_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Importance features sauvegardée: {filepath}")
            return filepath
        
        return None
    
    def plot_confidence_evolution(self,
                                 confidence_data: List[Dict],
                                 save: bool = True) -> Optional[str]:
        """
        Génère une courbe d'évolution de la confiance du modèle
        
        Args:
            confidence_data: Liste de {date, confidence, confidence_level}
            save: Sauvegarder le graphique
            
        Returns:
            Chemin du fichier si save=True
        """
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if confidence_data:
            df = pd.DataFrame(confidence_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Tracer la courbe de confiance
            ax.plot(df['date'], df['confidence'], 
                   marker='o', linewidth=2, color='darkblue', label='Confiance')
            
            # Ajouter des zones colorées pour les niveaux
            ax.axhspan(0.8, 1.0, alpha=0.2, color='green', label='Confiance Haute')
            ax.axhspan(0.6, 0.8, alpha=0.2, color='orange', label='Confiance Moyenne')
            ax.axhspan(0.0, 0.6, alpha=0.2, color='red', label='Confiance Basse')
            
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Score de Confiance', fontsize=12)
            ax.set_title('Évolution de la Confiance du Modèle', fontsize=14, fontweight='bold')
            ax.legend(loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_ylim([0, 1])
            plt.xticks(rotation=45)
        else:
            ax.text(0.5, 0.5, 'Aucune donnée disponible', 
                   ha='center', va='center', fontsize=14)
        
        plt.tight_layout()
        
        if save:
            filepath = save_figure(fig, f"confidence_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            logger.info(f"Évolution confiance sauvegardée: {filepath}")
            return filepath
        
        return None


def demo_chart_generator():
    """
    Fonction de démonstration du générateur de graphiques
    """
    generator = ChartGenerator()
    
    # Test distribution diagnostics
    diagnosis_counts = {
        "Grippe": 45,
        "COVID-19": 32,
        "Pneumonie": 28,
        "Bronchite": 15,
        "Asthme": 12
    }
    generator.plot_diagnosis_distribution(diagnosis_counts)
    
    # Test feature importance
    feature_importance = {
        f"feature_{i}": np.random.random() for i in range(20)
    }
    generator.plot_feature_importance(feature_importance, top_n=10)
    
    print("Graphiques de démonstration générés!")


if __name__ == "__main__":
    demo_chart_generator()
