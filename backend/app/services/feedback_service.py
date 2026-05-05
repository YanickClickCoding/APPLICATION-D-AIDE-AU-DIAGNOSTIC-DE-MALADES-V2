"""
Service de gestion du feedback des médecins
Collecte et analyse les retours sur les prédictions IA
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models.feedback import DoctorFeedback
from ..models.diagnostic import Diagnostic
from ..models.analyse_ia import AnalyseIA
from ..models.consultation import Consultation

logger = logging.getLogger(__name__)


class FeedbackService:
    """
    Service de gestion du feedback médecin
    
    Fonctionnalités:
    - Enregistrement du feedback
    - Calcul du score moyen de qualité
    - Identification des prédictions de basse qualité
    - Alertes qualité
    """
    
    def __init__(self, db: Session):
        """
        Initialise le service de feedback
        
        Args:
            db: Session de base de données
        """
        self.db = db
    
    def save_feedback(
        self,
        consultation_id: int,
        medecin_id: int,
        quality_score: int,
        comments: Optional[str] = None,
        helpful: bool = True,
        suggestions: Optional[str] = None
    ) -> Optional[DoctorFeedback]:
        """
        Enregistre un feedback médecin
        
        Args:
            consultation_id: ID de la consultation
            medecin_id: ID du médecin
            quality_score: Score de qualité (1-5)
            comments: Commentaires
            helpful: La prédiction était-elle utile?
            suggestions: Suggestions d'amélioration
            
        Returns:
            Objet DoctorFeedback créé ou None si erreur
        """
        logger.info(f"💬 Enregistrement du feedback pour consultation {consultation_id}")
        
        try:
            # Valider le score
            if not 1 <= quality_score <= 5:
                logger.error(f"❌ Score invalide: {quality_score} (doit être entre 1 et 5)")
                return None
            
            # Vérifier si un feedback existe déjà
            existing = self.db.query(DoctorFeedback).filter(
                DoctorFeedback.consultation_id == consultation_id,
                DoctorFeedback.medecin_id == medecin_id
            ).first()
            
            if existing:
                # Mettre à jour le feedback existant
                existing.quality_score = quality_score
                existing.comments = comments
                existing.helpful = helpful
                existing.suggestions = suggestions
                existing.feedback_date = datetime.now()
                
                self.db.commit()
                self.db.refresh(existing)
                
                logger.info(f"✅ Feedback mis à jour: {existing.feedback_id}")
                return existing
            else:
                # Créer un nouveau feedback
                feedback = DoctorFeedback(
                    consultation_id=consultation_id,
                    medecin_id=medecin_id,
                    quality_score=quality_score,
                    comments=comments,
                    helpful=helpful,
                    suggestions=suggestions,
                    feedback_date=datetime.now()
                )
                
                self.db.add(feedback)
                self.db.commit()
                self.db.refresh(feedback)
                
                logger.info(f"✅ Feedback créé: {feedback.feedback_id}")
                return feedback
                
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement du feedback: {e}")
            self.db.rollback()
            return None
    
    def calculate_average_quality(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        Calcule le score moyen de qualité
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Dictionnaire avec les statistiques
        """
        logger.info("📊 Calcul du score moyen de qualité...")
        
        try:
            # Définir la période par défaut (30 derniers jours)
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=30)
            
            # Requête pour les statistiques
            query = self.db.query(
                func.avg(DoctorFeedback.quality_score).label('avg_score'),
                func.count(DoctorFeedback.feedback_id).label('total_feedback'),
                func.sum(func.case((DoctorFeedback.helpful == True, 1), else_=0)).label('helpful_count')
            ).filter(
                DoctorFeedback.feedback_date >= start_date,
                DoctorFeedback.feedback_date <= end_date
            )
            
            result = query.first()
            
            if not result or result.total_feedback == 0:
                logger.warning("⚠️ Aucun feedback trouvé pour la période")
                return {
                    'average_score': 0.0,
                    'total_feedback': 0,
                    'helpful_percentage': 0.0,
                    'period': {
                        'start': start_date.isoformat(),
                        'end': end_date.isoformat()
                    }
                }
            
            avg_score = float(result.avg_score) if result.avg_score else 0.0
            total = result.total_feedback
            helpful = result.helpful_count or 0
            helpful_pct = (helpful / total * 100) if total > 0 else 0.0
            
            # Distribution des scores
            distribution = self._get_score_distribution(start_date, end_date)
            
            stats = {
                'average_score': round(avg_score, 2),
                'total_feedback': total,
                'helpful_count': helpful,
                'helpful_percentage': round(helpful_pct, 1),
                'score_distribution': distribution,
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                }
            }
            
            logger.info(f"✅ Score moyen: {avg_score:.2f}/5 ({total} feedbacks)")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul: {e}")
            return {
                'error': str(e),
                'average_score': 0.0,
                'total_feedback': 0
            }
    
    def get_low_quality_predictions(
        self,
        threshold: int = 2,
        limit: int = 20
    ) -> List[Dict]:
        """
        Récupère les prédictions avec un score de qualité bas
        
        Args:
            threshold: Seuil de score (inclus)
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des prédictions de basse qualité
        """
        logger.info(f"⚠️ Recherche des prédictions avec score ≤ {threshold}...")
        
        try:
            # Requête pour les feedbacks de basse qualité
            query = self.db.query(
                DoctorFeedback,
                Consultation,
                Diagnostic,
                AnalyseIA
            ).join(
                Consultation,
                DoctorFeedback.consultation_id == Consultation.consultation_id
            ).join(
                Diagnostic,
                Consultation.consultation_id == Diagnostic.consultation_id
            ).join(
                AnalyseIA,
                Diagnostic.analyse_ia_id == AnalyseIA.analyse_ia_id
            ).filter(
                DoctorFeedback.quality_score <= threshold
            ).order_by(
                DoctorFeedback.feedback_date.desc()
            ).limit(limit)
            
            results = query.all()
            
            low_quality = []
            for feedback, consultation, diagnostic, analyse_ia in results:
                low_quality.append({
                    'feedback_id': feedback.feedback_id,
                    'consultation_id': consultation.consultation_id,
                    'patient_id': consultation.patient_id,
                    'quality_score': feedback.quality_score,
                    'comments': feedback.comments,
                    'predicted_disease': analyse_ia.diagnostic_suggere,
                    'actual_disease': diagnostic.diagnostic_final,
                    'confidence': analyse_ia.confiance,
                    'feedback_date': feedback.feedback_date.isoformat(),
                    'helpful': feedback.helpful
                })
            
            logger.info(f"✅ {len(low_quality)} prédictions de basse qualité trouvées")
            
            return low_quality
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
            return []
    
    def get_feedback_by_medecin(
        self,
        medecin_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """
        Récupère les feedbacks d'un médecin spécifique
        
        Args:
            medecin_id: ID du médecin
            limit: Nombre maximum de résultats
            
        Returns:
            Liste des feedbacks
        """
        logger.info(f"👨‍⚕️ Récupération des feedbacks du médecin {medecin_id}...")
        
        try:
            feedbacks = self.db.query(DoctorFeedback).filter(
                DoctorFeedback.medecin_id == medecin_id
            ).order_by(
                DoctorFeedback.feedback_date.desc()
            ).limit(limit).all()
            
            feedback_list = [
                {
                    'feedback_id': f.feedback_id,
                    'consultation_id': f.consultation_id,
                    'quality_score': f.quality_score,
                    'comments': f.comments,
                    'helpful': f.helpful,
                    'suggestions': f.suggestions,
                    'feedback_date': f.feedback_date.isoformat()
                }
                for f in feedbacks
            ]
            
            logger.info(f"✅ {len(feedback_list)} feedbacks récupérés")
            
            return feedback_list
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération: {e}")
            return []
    
    def generate_quality_alert(self) -> Optional[Dict]:
        """
        Génère une alerte si la qualité est trop basse
        
        Returns:
            Dictionnaire avec l'alerte ou None si pas d'alerte
        """
        logger.info("🚨 Vérification des alertes qualité...")
        
        try:
            # Calculer le score moyen des 7 derniers jours
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            stats = self.calculate_average_quality(start_date, end_date)
            
            avg_score = stats.get('average_score', 0.0)
            total_feedback = stats.get('total_feedback', 0)
            
            # Seuils d'alerte
            CRITICAL_THRESHOLD = 2.5
            WARNING_THRESHOLD = 3.5
            MIN_FEEDBACK = 5
            
            if total_feedback < MIN_FEEDBACK:
                logger.info(f"ℹ️ Pas assez de feedbacks ({total_feedback}) pour générer une alerte")
                return None
            
            if avg_score <= CRITICAL_THRESHOLD:
                alert = {
                    'level': 'critical',
                    'message': f'Score de qualité critique: {avg_score:.2f}/5',
                    'average_score': avg_score,
                    'total_feedback': total_feedback,
                    'recommendation': 'Réentraînement urgent du modèle recommandé',
                    'generated_at': datetime.now().isoformat()
                }
                logger.warning(f"🚨 ALERTE CRITIQUE: Score {avg_score:.2f}/5")
                return alert
                
            elif avg_score <= WARNING_THRESHOLD:
                alert = {
                    'level': 'warning',
                    'message': f'Score de qualité bas: {avg_score:.2f}/5',
                    'average_score': avg_score,
                    'total_feedback': total_feedback,
                    'recommendation': 'Surveiller et envisager un réentraînement',
                    'generated_at': datetime.now().isoformat()
                }
                logger.warning(f"⚠️ ALERTE: Score {avg_score:.2f}/5")
                return alert
            
            logger.info(f"✅ Qualité satisfaisante: {avg_score:.2f}/5")
            return None
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la génération de l'alerte: {e}")
            return None
    
    def _get_score_distribution(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calcule la distribution des scores
        
        Args:
            start_date: Date de début
            end_date: Date de fin
            
        Returns:
            Distribution des scores
        """
        try:
            distribution = {}
            
            for score in range(1, 6):
                count = self.db.query(func.count(DoctorFeedback.feedback_id)).filter(
                    DoctorFeedback.quality_score == score,
                    DoctorFeedback.feedback_date >= start_date,
                    DoctorFeedback.feedback_date <= end_date
                ).scalar() or 0
                
                distribution[str(score)] = count
            
            return distribution
            
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul de la distribution: {e}")
            return {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0}
