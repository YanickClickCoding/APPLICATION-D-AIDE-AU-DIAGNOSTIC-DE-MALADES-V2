"""
Service de dashboard pour les KPIs et statistiques globales
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..models.patient import Patient
from ..models.consultation import Consultation
from ..models.diagnostic import Diagnostic
from ..models.analyse_ia import AnalyseIA
from ..models.user import User
from ..models.training_log import ModelTrainingLog

logger = logging.getLogger(__name__)


class DashboardService:
    """
    Service pour générer les données du dashboard
    
    Fonctionnalités:
    - KPIs globaux (patients, consultations, diagnostics)
    - Tendances temporelles
    - Top diagnostics
    - Performance du modèle
    - Statistiques du personnel
    """
    
    def __init__(self, db: Session):
        """
        Initialise le service de dashboard
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def get_global_kpis(self) -> Dict:
        """
        Récupère les KPIs globaux du système
        
        Returns:
            Dictionnaire avec les KPIs
        """
        logger.info("📊 Calcul des KPIs globaux...")
        
        try:
            # Date du début du mois
            today = datetime.now()
            first_day_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Total patients
            total_patients = self.db.query(func.count(Patient.patient_id)).scalar() or 0
            
            # Patients ce mois
            patients_ce_mois = self.db.query(func.count(Patient.patient_id)).filter(
                Patient.date_creation >= first_day_of_month
            ).scalar() or 0
            
            # Total consultations
            total_consultations = self.db.query(func.count(Consultation.consultation_id)).scalar() or 0
            
            # Consultations ce mois
            consultations_ce_mois = self.db.query(func.count(Consultation.consultation_id)).filter(
                Consultation.date_consultation >= first_day_of_month
            ).scalar() or 0
            
            # Total diagnostics
            total_diagnostics = self.db.query(func.count(Diagnostic.diagnostic_id)).scalar() or 0
            
            # Diagnostics ce mois
            diagnostics_ce_mois = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.date_diagnostic >= first_day_of_month
            ).scalar() or 0
            
            # Taux d'approbation IA
            total_with_ia = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None)
            ).scalar() or 0
            
            approved = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None),
                Diagnostic.statut == 'confirme'
            ).scalar() or 0
            
            taux_approbation = (approved / total_with_ia * 100) if total_with_ia > 0 else 0.0
            
            # Confiance moyenne
            avg_confidence = self.db.query(func.avg(AnalyseIA.confiance)).scalar() or 0.0
            
            # Personnel actif
            medecins_actifs = self.db.query(func.count(User.utilisateur_id)).filter(
                User.role == 'medecin',
                User.actif == True
            ).scalar() or 0
            
            infirmiers_actifs = self.db.query(func.count(User.utilisateur_id)).filter(
                User.role == 'infirmier',
                User.actif == True
            ).scalar() or 0
            
            kpis = {
                'patients': {
                    'total': total_patients,
                    'ce_mois': patients_ce_mois,
                    'variation': self._calculate_variation(total_patients, patients_ce_mois)
                },
                'consultations': {
                    'total': total_consultations,
                    'ce_mois': consultations_ce_mois,
                    'variation': self._calculate_variation(total_consultations, consultations_ce_mois)
                },
                'diagnostics': {
                    'total': total_diagnostics,
                    'ce_mois': diagnostics_ce_mois,
                    'variation': self._calculate_variation(total_diagnostics, diagnostics_ce_mois)
                },
                'ia_performance': {
                    'taux_approbation': round(taux_approbation, 1),
                    'confiance_moyenne': round(avg_confidence * 100, 1),
                    'total_predictions': total_with_ia
                },
                'personnel': {
                    'medecins_actifs': medecins_actifs,
                    'infirmiers_actifs': infirmiers_actifs,
                    'total_actif': medecins_actifs + infirmiers_actifs
                },
                'generated_at': datetime.now().isoformat()
            }
            
            logger.info("✅ KPIs calculés avec succès")
            
            return kpis
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul des KPIs: {e}")
            return {
                'error': str(e),
                'generated_at': datetime.now().isoformat()
            }
    
    def get_trends(
        self,
        days: int = 30,
        metric: str = 'consultations'
    ) -> List[Dict]:
        """
        Récupère les tendances temporelles
        
        Args:
            days: Nombre de jours à analyser
            metric: Métrique à analyser ('consultations', 'diagnostics', 'patients')
            
        Returns:
            Liste des points de données pour le graphique
        """
        logger.info(f"📈 Calcul des tendances ({metric}, {days} jours)...")
        
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            if metric == 'consultations':
                query = self.db.query(
                    func.date(Consultation.date_consultation).label('date'),
                    func.count(Consultation.consultation_id).label('count')
                ).filter(
                    Consultation.date_consultation >= start_date
                ).group_by(
                    func.date(Consultation.date_consultation)
                ).order_by('date')
                
            elif metric == 'diagnostics':
                query = self.db.query(
                    func.date(Diagnostic.date_diagnostic).label('date'),
                    func.count(Diagnostic.diagnostic_id).label('count')
                ).filter(
                    Diagnostic.date_diagnostic >= start_date
                ).group_by(
                    func.date(Diagnostic.date_diagnostic)
                ).order_by('date')
                
            elif metric == 'patients':
                query = self.db.query(
                    func.date(Patient.date_creation).label('date'),
                    func.count(Patient.patient_id).label('count')
                ).filter(
                    Patient.date_creation >= start_date
                ).group_by(
                    func.date(Patient.date_creation)
                ).order_by('date')
            else:
                logger.warning(f"⚠️ Métrique inconnue: {metric}")
                return []
            
            results = query.all()
            
            trends = [
                {
                    'date': row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                    'count': row.count
                }
                for row in results
            ]
            
            logger.info(f"✅ {len(trends)} points de données récupérés")
            
            return trends
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul des tendances: {e}")
            return []
    
    def get_top_diagnostics(self, limit: int = 10) -> List[Dict]:
        """
        Récupère les diagnostics les plus fréquents
        
        Args:
            limit: Nombre de diagnostics à retourner
            
        Returns:
            Liste des diagnostics avec leur fréquence
        """
        logger.info(f"🏆 Récupération du top {limit} diagnostics...")
        
        try:
            query = self.db.query(
                Diagnostic.diagnostic_final.label('diagnostic'),
                func.count(Diagnostic.diagnostic_id).label('count')
            ).filter(
                Diagnostic.diagnostic_final.isnot(None),
                Diagnostic.diagnostic_final != ''
            ).group_by(
                Diagnostic.diagnostic_final
            ).order_by(
                func.count(Diagnostic.diagnostic_id).desc()
            ).limit(limit)
            
            results = query.all()
            
            # Calculer le total pour les pourcentages
            total = sum(row.count for row in results)
            
            top_diagnostics = [
                {
                    'diagnostic': row.diagnostic,
                    'count': row.count,
                    'percentage': round((row.count / total * 100) if total > 0 else 0, 1)
                }
                for row in results
            ]
            
            logger.info(f"✅ {len(top_diagnostics)} diagnostics récupérés")
            
            return top_diagnostics
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération: {e}")
            return []
    
    def get_model_performance_metrics(self) -> Dict:
        """
        Récupère les métriques de performance du modèle
        
        Returns:
            Dictionnaire avec les métriques
        """
        logger.info("🎯 Récupération des métriques du modèle...")
        
        try:
            # Dernière version déployée
            last_model = self.db.query(ModelTrainingLog).filter(
                ModelTrainingLog.deployed == True
            ).order_by(
                ModelTrainingLog.training_date.desc()
            ).first()
            
            if not last_model:
                logger.warning("⚠️ Aucun modèle déployé trouvé")
                return {
                    'model_deployed': False,
                    'message': 'Aucun modèle déployé'
                }
            
            # Statistiques des prédictions
            total_predictions = self.db.query(func.count(AnalyseIA.analyse_ia_id)).scalar() or 0
            
            # Diagnostics avec IA
            with_ia = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None)
            ).scalar() or 0
            
            approved = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None),
                Diagnostic.statut == 'confirme'
            ).scalar() or 0
            
            rejected = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None),
                Diagnostic.statut == 'rejete'
            ).scalar() or 0
            
            pending = self.db.query(func.count(Diagnostic.diagnostic_id)).filter(
                Diagnostic.analyse_ia_id.isnot(None),
                Diagnostic.statut == 'en_attente'
            ).scalar() or 0
            
            # Distribution de confiance
            confidence_dist = self._get_confidence_distribution()
            
            metrics = {
                'model_deployed': True,
                'current_model': {
                    'version': last_model.version,
                    'accuracy': round(last_model.accuracy * 100, 1),
                    'precision': round(last_model.precision * 100, 1),
                    'recall': round(last_model.recall * 100, 1),
                    'f1_score': round(last_model.f1_score * 100, 1),
                    'training_date': last_model.training_date.isoformat(),
                    'n_samples': last_model.n_samples,
                    'n_classes': last_model.n_classes
                },
                'predictions': {
                    'total': total_predictions,
                    'with_diagnostic': with_ia,
                    'approved': approved,
                    'rejected': rejected,
                    'pending': pending,
                    'approval_rate': round((approved / with_ia * 100) if with_ia > 0 else 0, 1)
                },
                'confidence_distribution': confidence_dist
            }
            
            logger.info("✅ Métriques récupérées avec succès")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des métriques: {e}")
            return {
                'error': str(e),
                'model_deployed': False
            }
    
    def get_recent_activity(self, limit: int = 10) -> Dict:
        """
        Récupère l'activité récente du système
        
        Args:
            limit: Nombre d'éléments à retourner
            
        Returns:
            Dictionnaire avec les activités récentes
        """
        logger.info(f"📋 Récupération de l'activité récente (limit={limit})...")
        
        try:
            # Consultations récentes
            recent_consultations = self.db.query(Consultation).order_by(
                Consultation.date_consultation.desc()
            ).limit(limit).all()
            
            # Diagnostics récents
            recent_diagnostics = self.db.query(Diagnostic).order_by(
                Diagnostic.date_diagnostic.desc()
            ).limit(limit).all()
            
            # Nouveaux patients
            recent_patients = self.db.query(Patient).order_by(
                Patient.date_creation.desc()
            ).limit(limit).all()
            
            activity = {
                'consultations': [
                    {
                        'id': c.consultation_id,
                        'patient_id': c.patient_id,
                        'medecin_id': c.medecin_id,
                        'date': c.date_consultation.isoformat(),
                        'motif': c.motif,
                        'statut': c.statut
                    }
                    for c in recent_consultations
                ],
                'diagnostics': [
                    {
                        'id': d.diagnostic_id,
                        'consultation_id': d.consultation_id,
                        'diagnostic': d.diagnostic_final,
                        'date': d.date_diagnostic.isoformat(),
                        'statut': d.statut
                    }
                    for d in recent_diagnostics
                ],
                'patients': [
                    {
                        'id': p.patient_id,
                        'nom': p.nom,
                        'prenom': p.prenom,
                        'date_creation': p.date_creation.isoformat()
                    }
                    for p in recent_patients
                ]
            }
            
            logger.info("✅ Activité récente récupérée")
            
            return activity
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération de l'activité: {e}")
            return {
                'error': str(e),
                'consultations': [],
                'diagnostics': [],
                'patients': []
            }
    
    def _calculate_variation(self, total: int, current_period: int) -> float:
        """
        Calcule la variation en pourcentage
        
        Args:
            total: Total global
            current_period: Valeur de la période actuelle
            
        Returns:
            Variation en pourcentage
        """
        if total == 0:
            return 0.0
        
        previous_period = total - current_period
        if previous_period == 0:
            return 100.0 if current_period > 0 else 0.0
        
        variation = ((current_period - previous_period) / previous_period) * 100
        return round(variation, 1)
    
    def _get_confidence_distribution(self) -> Dict:
        """
        Calcule la distribution des niveaux de confiance
        
        Returns:
            Dictionnaire avec la distribution
        """
        try:
            # Compter par niveau de confiance
            low = self.db.query(func.count(AnalyseIA.analyse_ia_id)).filter(
                AnalyseIA.confiance < 0.6
            ).scalar() or 0
            
            medium = self.db.query(func.count(AnalyseIA.analyse_ia_id)).filter(
                and_(AnalyseIA.confiance >= 0.6, AnalyseIA.confiance < 0.8)
            ).scalar() or 0
            
            high = self.db.query(func.count(AnalyseIA.analyse_ia_id)).filter(
                AnalyseIA.confiance >= 0.8
            ).scalar() or 0
            
            total = low + medium + high
            
            return {
                'low': {
                    'count': low,
                    'percentage': round((low / total * 100) if total > 0 else 0, 1)
                },
                'medium': {
                    'count': medium,
                    'percentage': round((medium / total * 100) if total > 0 else 0, 1)
                },
                'high': {
                    'count': high,
                    'percentage': round((high / total * 100) if total > 0 else 0, 1)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul de la distribution: {e}")
            return {'low': {'count': 0, 'percentage': 0}, 'medium': {'count': 0, 'percentage': 0}, 'high': {'count': 0, 'percentage': 0}}
