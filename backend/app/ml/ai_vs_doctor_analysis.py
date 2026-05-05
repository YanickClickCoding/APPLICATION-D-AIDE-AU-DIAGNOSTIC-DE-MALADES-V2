"""
Module de comparaison entre les prédictions IA et les diagnostics des médecins
Analyse les accords, désaccords et patterns
"""
import logging
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.diagnostic import Diagnostic
from ..models.analyse_ia import AnalyseIA
from ..models.consultation import Consultation
from ..models.user import User

logger = logging.getLogger(__name__)


class AIvsDoctorAnalyzer:
    """
    Analyseur de comparaison IA vs Médecin
    
    Fonctionnalités:
    - Calcul du taux d'accord
    - Identification des cas où l'IA était correcte mais rejetée
    - Identification des cas où l'IA était incorrecte mais approuvée
    - Génération de matrice de comparaison
    - Rapport détaillé
    """
    
    def __init__(self, db: Session):
        """
        Initialise l'analyseur
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def calculate_agreement_rate(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Calcule le taux d'accord entre l'IA et les médecins
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec les statistiques d'accord
        """
        logger.info("🤝 Calcul du taux d'accord IA vs Médecin...")
        
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
                logger.warning("⚠️ Aucune donnée trouvée")
                return {
                    'total_cases': 0,
                    'agreement_rate': 0.0,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            
            # Analyser les accords/désaccords
            total = len(results)
            agreements = 0
            disagreements = 0
            
            for diagnostic, analyse_ia in results:
                if diagnostic.statut == 'confirme':
                    # Médecin a approuvé la prédiction IA
                    agreements += 1
                else:
                    # Médecin a rejeté la prédiction IA
                    disagreements += 1
            
            agreement_rate = (agreements / total * 100) if total > 0 else 0.0
            
            stats = {
                'total_cases': total,
                'agreements': agreements,
                'disagreements': disagreements,
                'agreement_rate': round(agreement_rate, 2),
                'disagreement_rate': round(100 - agreement_rate, 2),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            logger.info(
                f"✅ Taux d'accord: {agreement_rate:.1f}% "
                f"({agreements}/{total} cas)"
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul: {e}")
            return {
                'error': str(e),
                'total_cases': 0,
                'agreement_rate': 0.0
            }
    
    def identify_ai_correct_but_rejected(
        self,
        limit: int = 20
    ) -> List[Dict]:
        """
        Identifie les cas où l'IA avait raison mais a été rejetée
        (Nécessite une validation externe ou un suivi patient)
        
        Args:
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des cas identifiés
        """
        logger.info("🔍 Recherche des cas IA correcte mais rejetée...")
        
        try:
            # Cette analyse nécessiterait un suivi patient pour confirmer
            # Pour l'instant, on identifie les cas rejetés avec haute confiance
            
            query = self.db.query(
                Diagnostic,
                AnalyseIA,
                Consultation
            ).join(
                AnalyseIA,
                Diagnostic.analyse_ia_id == AnalyseIA.analyse_ia_id
            ).join(
                Consultation,
                Diagnostic.consultation_id == Consultation.consultation_id
            ).filter(
                Diagnostic.statut == 'rejete',
                AnalyseIA.confiance >= 0.8  # Haute confiance
            ).order_by(
                AnalyseIA.confiance.desc()
            ).limit(limit)
            
            results = query.all()
            
            cases = []
            for diagnostic, analyse_ia, consultation in results:
                cases.append({
                    'diagnostic_id': diagnostic.diagnostic_id,
                    'consultation_id': consultation.consultation_id,
                    'patient_id': consultation.patient_id,
                    'ai_prediction': analyse_ia.diagnostic_suggere,
                    'doctor_diagnosis': diagnostic.diagnostic_final,
                    'ai_confidence': round(analyse_ia.confiance * 100, 1),
                    'date': diagnostic.date_diagnostic.isoformat(),
                    'notes': diagnostic.notes_medecin,
                    'reason': 'Haute confiance IA mais rejeté par médecin'
                })
            
            logger.info(f"✅ {len(cases)} cas identifiés")
            
            return cases
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'identification: {e}")
            return []
    
    def identify_ai_incorrect_but_approved(
        self,
        limit: int = 20
    ) -> List[Dict]:
        """
        Identifie les cas où l'IA s'est trompée mais a été approuvée
        (Nécessite une validation externe ou un suivi patient)
        
        Args:
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des cas identifiés
        """
        logger.info("🔍 Recherche des cas IA incorrecte mais approuvée...")
        
        try:
            # Cette analyse nécessiterait un suivi patient pour confirmer
            # Pour l'instant, on identifie les cas approuvés avec basse confiance
            
            query = self.db.query(
                Diagnostic,
                AnalyseIA,
                Consultation
            ).join(
                AnalyseIA,
                Diagnostic.analyse_ia_id == AnalyseIA.analyse_ia_id
            ).join(
                Consultation,
                Diagnostic.consultation_id == Consultation.consultation_id
            ).filter(
                Diagnostic.statut == 'confirme',
                AnalyseIA.confiance < 0.6  # Basse confiance
            ).order_by(
                AnalyseIA.confiance.asc()
            ).limit(limit)
            
            results = query.all()
            
            cases = []
            for diagnostic, analyse_ia, consultation in results:
                cases.append({
                    'diagnostic_id': diagnostic.diagnostic_id,
                    'consultation_id': consultation.consultation_id,
                    'patient_id': consultation.patient_id,
                    'ai_prediction': analyse_ia.diagnostic_suggere,
                    'doctor_diagnosis': diagnostic.diagnostic_final,
                    'ai_confidence': round(analyse_ia.confiance * 100, 1),
                    'date': diagnostic.date_diagnostic.isoformat(),
                    'notes': diagnostic.notes_medecin,
                    'reason': 'Basse confiance IA mais approuvé par médecin'
                })
            
            logger.info(f"✅ {len(cases)} cas identifiés")
            
            return cases
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'identification: {e}")
            return []
    
    def generate_comparison_matrix(self) -> Dict:
        """
        Génère une matrice de comparaison IA vs Médecin
        
        Returns:
            Matrice avec les statistiques croisées
        """
        logger.info("📊 Génération de la matrice de comparaison...")
        
        try:
            # Récupérer tous les diagnostics avec IA
            query = self.db.query(Diagnostic, AnalyseIA).join(
                AnalyseIA,
                Diagnostic.analyse_ia_id == AnalyseIA.analyse_ia_id
            ).filter(
                Diagnostic.statut.in_(['confirme', 'rejete'])
            )
            
            results = query.all()
            
            if not results:
                logger.warning("⚠️ Aucune donnée trouvée")
                return {
                    'matrix': {},
                    'total_cases': 0
                }
            
            # Construire la matrice
            matrix = {
                'high_confidence_approved': 0,
                'high_confidence_rejected': 0,
                'medium_confidence_approved': 0,
                'medium_confidence_rejected': 0,
                'low_confidence_approved': 0,
                'low_confidence_rejected': 0
            }
            
            for diagnostic, analyse_ia in results:
                confidence = analyse_ia.confiance
                approved = diagnostic.statut == 'confirme'
                
                if confidence >= 0.8:
                    level = 'high'
                elif confidence >= 0.6:
                    level = 'medium'
                else:
                    level = 'low'
                
                status = 'approved' if approved else 'rejected'
                key = f'{level}_confidence_{status}'
                matrix[key] += 1
            
            total = len(results)
            
            # Calculer les pourcentages
            matrix_pct = {
                key: {
                    'count': value,
                    'percentage': round((value / total * 100) if total > 0 else 0, 1)
                }
                for key, value in matrix.items()
            }
            
            result = {
                'matrix': matrix_pct,
                'total_cases': total,
                'summary': {
                    'high_confidence': {
                        'total': matrix['high_confidence_approved'] + matrix['high_confidence_rejected'],
                        'approval_rate': round(
                            (matrix['high_confidence_approved'] / 
                             (matrix['high_confidence_approved'] + matrix['high_confidence_rejected']) * 100)
                            if (matrix['high_confidence_approved'] + matrix['high_confidence_rejected']) > 0 else 0,
                            1
                        )
                    },
                    'medium_confidence': {
                        'total': matrix['medium_confidence_approved'] + matrix['medium_confidence_rejected'],
                        'approval_rate': round(
                            (matrix['medium_confidence_approved'] / 
                             (matrix['medium_confidence_approved'] + matrix['medium_confidence_rejected']) * 100)
                            if (matrix['medium_confidence_approved'] + matrix['medium_confidence_rejected']) > 0 else 0,
                            1
                        )
                    },
                    'low_confidence': {
                        'total': matrix['low_confidence_approved'] + matrix['low_confidence_rejected'],
                        'approval_rate': round(
                            (matrix['low_confidence_approved'] / 
                             (matrix['low_confidence_approved'] + matrix['low_confidence_rejected']) * 100)
                            if (matrix['low_confidence_approved'] + matrix['low_confidence_rejected']) > 0 else 0,
                            1
                        )
                    }
                }
            }
            
            logger.info("✅ Matrice générée avec succès")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération: {e}")
            return {
                'error': str(e),
                'matrix': {},
                'total_cases': 0
            }
    
    def generate_comparison_report(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Génère un rapport complet de comparaison IA vs Médecin
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Rapport complet
        """
        logger.info("📄 Génération du rapport de comparaison...")
        
        try:
            # Taux d'accord
            agreement_stats = self.calculate_agreement_rate(start_date, end_date)
            
            # Matrice de comparaison
            comparison_matrix = self.generate_comparison_matrix()
            
            # Cas spécifiques
            ai_correct_rejected = self.identify_ai_correct_but_rejected(limit=10)
            ai_incorrect_approved = self.identify_ai_incorrect_but_approved(limit=10)
            
            # Statistiques par médecin
            doctor_stats = self._get_doctor_statistics()
            
            # Recommandations
            recommendations = self._generate_recommendations(
                agreement_stats,
                comparison_matrix,
                ai_correct_rejected,
                ai_incorrect_approved
            )
            
            report = {
                'generated_at': datetime.now().isoformat(),
                'period': agreement_stats.get('period', {}),
                'agreement_statistics': agreement_stats,
                'comparison_matrix': comparison_matrix,
                'special_cases': {
                    'ai_correct_but_rejected': ai_correct_rejected,
                    'ai_incorrect_but_approved': ai_incorrect_approved
                },
                'doctor_statistics': doctor_stats,
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
    
    def _get_doctor_statistics(self) -> List[Dict]:
        """
        Calcule les statistiques par médecin
        
        Returns:
            Liste des statistiques par médecin
        """
        try:
            query = self.db.query(
                User.utilisateur_id,
                User.nom,
                User.prenoms,
                func.count(Diagnostic.diagnostic_id).label('total_diagnostics'),
                func.sum(
                    func.case(
                        (Diagnostic.statut == 'confirme', 1),
                        else_=0
                    )
                ).label('approved'),
                func.sum(
                    func.case(
                        (Diagnostic.statut == 'rejete', 1),
                        else_=0
                    )
                ).label('rejected')
            ).join(
                Consultation,
                User.utilisateur_id == Consultation.medecin_id
            ).join(
                Diagnostic,
                Consultation.consultation_id == Diagnostic.consultation_id
            ).filter(
                User.role == 'medecin',
                Diagnostic.analyse_ia_id.isnot(None)
            ).group_by(
                User.utilisateur_id,
                User.nom,
                User.prenoms
            ).order_by(
                func.count(Diagnostic.diagnostic_id).desc()
            ).limit(10)
            
            results = query.all()
            
            stats = []
            for row in results:
                total = row.total_diagnostics
                approved = row.approved or 0
                rejected = row.rejected or 0
                approval_rate = (approved / total * 100) if total > 0 else 0.0
                
                stats.append({
                    'medecin_id': row.utilisateur_id,
                    'nom': row.nom,
                    'prenoms': row.prenoms,
                    'total_diagnostics': total,
                    'approved': approved,
                    'rejected': rejected,
                    'approval_rate': round(approval_rate, 1)
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul des statistiques: {e}")
            return []
    
    def _generate_recommendations(
        self,
        agreement_stats: Dict,
        comparison_matrix: Dict,
        ai_correct_rejected: List,
        ai_incorrect_approved: List
    ) -> List[str]:
        """
        Génère des recommandations basées sur l'analyse
        
        Returns:
            Liste de recommandations
        """
        recommendations = []
        
        # Recommandations basées sur le taux d'accord
        agreement_rate = agreement_stats.get('agreement_rate', 0.0)
        
        if agreement_rate >= 80:
            recommendations.append(
                "✅ Excellent taux d'accord (≥80%). L'IA est bien calibrée avec les médecins."
            )
        elif agreement_rate >= 60:
            recommendations.append(
                "⚠️ Taux d'accord modéré (60-80%). Analyser les cas de désaccord pour améliorer le modèle."
            )
        else:
            recommendations.append(
                "🚨 Taux d'accord faible (<60%). Réentraînement urgent recommandé."
            )
        
        # Recommandations basées sur les cas spéciaux
        if len(ai_correct_rejected) > 5:
            recommendations.append(
                f"🔍 {len(ai_correct_rejected)} cas de haute confiance rejetés. "
                "Former les médecins sur l'interprétation des prédictions IA."
            )
        
        if len(ai_incorrect_approved) > 5:
            recommendations.append(
                f"⚠️ {len(ai_incorrect_approved)} cas de basse confiance approuvés. "
                "Sensibiliser les médecins à vérifier les prédictions de faible confiance."
            )
        
        return recommendations
