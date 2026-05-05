"""
Prediction History Manager
Gestion de l'historique des prédictions
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.prediction_history import PredictionHistory
import logging

logger = logging.getLogger(__name__)


class PredictionHistoryManager:
    """
    Gestionnaire de l'historique des prédictions
    
    Fonctionnalités:
    - Enregistrement des prédictions
    - Récupération de l'historique
    - Comparaison de prédiction