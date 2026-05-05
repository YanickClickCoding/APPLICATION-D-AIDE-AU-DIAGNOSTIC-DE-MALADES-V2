"""
Module d'analyse des erreurs du modèle ML
Identifie les patterns d'erreurs et génère des rapports détaillés
"""
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.diagnostic import Diagnostic
from ..models.analyse_ia import AnalyseIA

logger = logging.getLogger(__name__)


class ErrorAnalyzer:
    """
    Analyseur d'erreurs du modèle ML
    
    Fonctionnalités:
    - Analyse des erreurs de prédiction
    - Identification des patterns d'erreurs
    - Calcul du taux d'erreur par diagnostic
    - Génération de rapports détaillés
    """
    
    def __init__(self, db: Session):
        """
        Initialise l'analyseur d'erreurs
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def analyze_errors(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Analyse complète des erreurs du modèle
        
        Args:
            start_date: Date de début de l'analyse
            end_date: Date de fin de l'analyse
            
        Returns:
            Dictionnaire avec les métriques d'erreur
        """
        logger.info("📊 Analyse des erreurs du modèle...")
        
        try:
            # Définir la période par défaut (30 derniers jours)
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
            
            # Récupérer les diagnostics avec prédictions IA
            query = self.db.query(Diagnostic, AnalyseIA).join(
                AnalyseIA,
                Diagnostic.analyse_ia_id == AnalyseIA.analyse_ia_id
            ).filter(
                Diagnostic.date_diagnostic >= start_date,
                Diagnostic.date_diagnostic <= end_date,
                Diagnostic.statut.in_(['confirme', 'rejete'])
            )
            
            results = query.all()
            
            if not results:
                logger.warning("⚠️ Aucune donnée trouvée pour l'analyse")
                return {
                    'total_predictions': 0,
                    'errors': 0,
                    'error_rate': 0.0,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            
            # Construire les listes de prédictions et vérités
            y_true = []
            y_pred = []
            errors = []
            
            for diagnostic, analyse_ia in results:
                predicted = analyse_ia.diagnostic_suggere
                actual = diagnostic.diagnostic_final
                
                y_pred.append(predicted)
                y_true.append(actual)
                
                # Identifier les erreurs
                if predicted != actual:
                    errors.append({
                        'diagnostic_id': diagnostic.diagnostic_id,
                        'predicted': predicted,
                        'actual': actual,
                        'confidence': analyse_ia.confiance,
                        'date': diagnostic.date_diagnostic.isoformat()
                    })
            
            # Calculer les métriques
            total = len(y_true)
            n_errors = len(errors)
            error_rate = n_errors / total if total > 0 else 0.0
            
            # Matrice de confusion
            cm = confusion_matrix(y_true, y_pred)
            
            # Rapport de classification
            try:
                class_report = classification_report(
                    y_true,
                    y_pred,
                    output_dict=True,
                    zero_division=0
                )
            except Exception as e:
                logger.warning(f"⚠️ Impossible de générer le rapport de classification: {e}")
                class_report = {}
            
            metrics = {
                'total_predictions': total,
                'correct_predictions': total - n_errors,
                'errors': n_errors,
                'error_rate': float(error_rate),
                'accuracy': float(1 - error_rate),
                'confusion_matrix': cm.tolist(),
                'classification_report': class_report,
                'error_details': errors[:10],  # Top 10 erreurs
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            logger.info(
                f"✅ Analyse terminée: {n_errors}/{total} erreurs "
                f"(Taux d'erreur: {error_rate:.2%})"
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'analyse: {e}")
            return {
                'error': str(e),
                'total_predictions': 0,
                'errors': 0,
                'error_rate': 0.0
            }
    
    def identify_error_patterns(
        self,
        min_occurrences: int = 3
    ) -> List[Dict]:
        """
        Identifie les patterns d'erreurs récurrents
        
        Args:
            min_occurrences: Nombre minimum d'occurrences pour considérer un pattern
            
        Returns:
            Liste des patterns identifiés
        """
        logger.info("🔍 Identification des patterns d'erreurs...")
        
        try:
            # Récupérer les erreurs (prédictions rejetées)
            query = self.db.query(
                AnalyseIA.diagnostic_suggere.label('predicted'),
                Diagnostic.diagnostic_final.label('actual'),
                func.count().label('count'),
                func.avg(AnalyseIA.confiance).label('avg_confidence')
            ).join(
                Diagnostic,
                AnalyseIA.analyse_ia_id == Diagnostic.analyse_ia_id
            ).filter(
                Diagnostic.statut == 'rejete'
            ).group_by(
                AnalyseIA.diagnostic_suggere,
                Diagnostic.diagnostic_final
            ).having(
                func.count() >= min_occurrences
            ).order_by(
                func.count().desc()
            )
            
            results = query.all()
            
            patterns = []
            for row in results:
                patterns.append({
                    'predicted_disease': row.predicted,
                    'actual_disease': row.actual,
                    'occurrences': row.count,
                    'avg_confidence': float(row.avg_confidence),
                    'pattern_type': self._classify_error_pattern(row.predicted, row.actual)
                })
            
            logger.info(f"✅ {len(patterns)} patterns identifiés")
            
            return patterns
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'identification des patterns: {e}")
            return []
    
    def calculate_error_rate_by_diagnosis(self) -> List[Dict]:
        """
        Calcule le taux d'erreur pour chaque diagnostic
        
        Returns:
            Liste des diagnostics avec leurs taux d'erreur
        """
        logger.info("📈 Calcul du taux d'erreur par diagnostic...")
        
        try:
            # Récupérer les statistiques par diagnostic
            query = self.db.query(
                AnalyseIA.diagnostic_suggere.label('diagnosis'),
                func.count().label('total'),
                func.sum(
                    func.case(
                        (Diagnostic.statut == 'confirme', 1),
                        else_=0
                    )
                ).label('correct'),
                func.sum(
                    func.case(
                        (Diagnostic.statut == 'rejete', 1),
                        else_=0
                    )
                ).label('errors')
            ).join(
                Diagnostic,
                AnalyseIA.analyse_ia_id == Diagnostic.analyse_ia_id
            ).filter(
                Diagnostic.statut.in_(['confirme', 'rejete'])
            ).group_by(
                AnalyseIA.diagnostic_suggere
            ).order_by(
                func.count().desc()
            )
            
            results = query.all()
            
            diagnosis_stats = []
            for row in results:
                total = row.total
                correct = row.correct or 0
                errors = row.errors or 0
                error_rate = errors / total if total > 0 else 0.0
                accuracy = correct / total if total > 0 else 0.0
                
                diagnosis_stats.append({
                    'diagnosis': row.diagnosis,
                    'total_predictions': total,
                    'correct': correct,
                    'errors': errors,
                    'error_rate': float(error_rate),
                    'accuracy': float(accuracy)
                })
            
            logger.info(f"✅ Statistiques calculées pour {len(diagnosis_stats)} diagnostics")
            
            return diagnosis_stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul: {e}")
            return []
    
    def get_high_error_diagnoses(
        self,
        threshold: float = 0.3,
        min_samples: int = 5
    ) -> List[Dict]:
        """
        Identifie les diagnostics avec un taux d'erreur élevé
        
        Args:
            threshold: Seuil de taux d'erreur (0.3 = 30%)
            min_samples: Nombre minimum d'échantillons
            
        Returns:
            Liste des diagnostics problématiques
        """
        logger.info(f"⚠️ Recherche des diagnostics avec taux d'erreur > {threshold:.0%}...")
        
        try:
            all_stats = self.calculate_error_rate_by_diagnosis()
            
            high_error = [
                stat for stat in all_stats
                if stat['error_rate'] >= threshold and stat['total_predictions'] >= min_samples
            ]
            
            # Trier par taux d'erreur décroissant
            high_error.sort(key=lambda x: x['error_rate'], reverse=True)
            
            logger.info(f"✅ {len(high_error)} diagnostics problématiques identifiés")
            
            return high_error
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
            return []
    
    def generate_error_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Génère un rapport complet d'analyse des erreurs
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Rapport complet avec toutes les analyses
        """
        logger.info("📄 Génération du rapport d'erreurs...")
        
        try:
            # Analyse globale
            global_metrics = self.analyze_errors(start_date, end_date)
            
            # Patterns d'erreurs
            error_patterns = self.identify_error_patterns()
            
            # Taux d'erreur par diagnostic
            diagnosis_stats = self.calculate_error_rate_by_diagnosis()
            
            # Diagnostics problématiques
            high_error_diagnoses = self.get_high_error_diagnoses()
            
            # Recommandations
            recommendations = self._generate_recommendations(
                global_metrics,
                error_patterns,
                high_error_diagnoses
            )
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'period': global_metrics.get('period', {}),
                'summary': {
                    'total_predictions': global_metrics.get('total_predictions', 0),
                    'errors': global_metrics.get('errors', 0),
                    'error_rate': global_metrics.get('error_rate', 0.0),
                    'accuracy': global_metrics.get('accuracy', 0.0)
                },
                'error_patterns': error_patterns[:10],  # Top 10
                'diagnosis_statistics': diagnosis_stats[:20],  # Top 20
                'high_error_diagnoses': high_error_diagnoses,
                'recommendations': recommendations
            }
            
            logger.info("✅ Rapport généré avec succès")
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération du rapport: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def _classify_error_pattern(self, predicted: str, actual: str) -> str:
        """
        Classifie le type de pattern d'erreur
        
        Args:
            predicted: Diagnostic prédit
            actual: Diagnostic réel
            
        Returns:
            Type de pattern
        """
        # Logique simple de classification
        if predicted.lower() in actual.lower() or actual.lower() in predicted.lower():
            return 'similar_diseases'
        elif any(word in predicted.lower() for word in ['infection', 'inflammation']) and \
             any(word in actual.lower() for word in ['infection', 'inflammation']):
            return 'same_category'
        else:
            return 'different_category'
    
    def _generate_recommendations(
        self,
        global_metrics: Dict,
        error_patterns: List[Dict],
        high_error_diagnoses: List[Dict]
    ) -> List[str]:
        """
        Génère des recommandations basées sur l'analyse
        
        Args:
            global_metrics: Métriques globales
            error_patterns: Patterns d'erreurs
            high_error_diagnoses: Diagnostics problématiques
            
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Recommandations basées sur le taux d'erreur global
        error_rate = global_metrics.get('error_rate', 0.0)
        
        if error_rate > 0.3:
            recommendations.append(
                "⚠️ Taux d'erreur élevé (>30%). Envisager un réentraînement du modèle avec plus de données."
            )
        elif error_rate > 0.2:
            recommendations.append(
                "⚠️ Taux d'erreur modéré (>20%). Surveiller l'évolution et collecter plus de cas validés."
            )
        
        # Recommandations basées sur les patterns
        if len(error_patterns) > 5:
            recommendations.append(
                f"🔍 {len(error_patterns)} patterns d'erreurs récurrents détectés. "
                "Analyser les features discriminantes pour ces cas."
            )
        
        # Recommandations basées sur les diagnostics problématiques
        if high_error_diagnoses:
            problematic = [d['diagnosis'] for d in high_error_diagnoses[:3]]
            recommendations.append(
                f"⚠️ Diagnostics problématiques: {', '.join(problematic)}. "
                "Collecter plus d'exemples pour ces maladies."
            )
        
        # Recommandation générale
        if not recommendations:
            recommendations.append(
                "✅ Performance satisfaisante. Continuer la surveillance et la collecte de données."
            )
        
        return recommendations
