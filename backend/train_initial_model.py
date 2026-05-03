"""
Script d'entraînement initial du modèle
US-012: Entraînement du modèle initial

Usage:
    python train_initial_model.py
"""
import sys
import os
from pathlib import Path

# Ajouter le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.model_manager import model_manager
from app.utils.logger import setup_logging
import logging

# Configuration du logging
setup_logging(log_level="INFO")
logger = logging.getLogger(__name__)


def main():
    """
    Entraîne le modèle initial sur le dataset
    """
    logger.info("=" * 80)
    logger.info("🚀 ENTRAÎNEMENT DU MODÈLE INITIAL")
    logger.info("=" * 80)
    
    # Chemin du dataset
    dataset_path = "../les ressources dataset/dataset_medical_robust_10000_cas.csv"
    
    if not os.path.exists(dataset_path):
        logger.error(f"❌ Dataset introuvable: {dataset_path}")
        logger.error("   Vérifiez que le fichier existe")
        return
    
    logger.info(f"📂 Dataset: {dataset_path}")
    
    # Entraîner le modèle
    logger.info("")
    logger.info("🤖 Début de l'entraînement...")
    logger.info("-" * 80)
    
    results = model_manager.train_new_model(
        dataset_path=dataset_path,
        n_estimators=200,  # Plus d'arbres pour mieux apprendre
        max_depth=30,      # Plus de profondeur
        save=True
    )
    
    logger.info("-" * 80)
    
    if results["success"]:
        logger.info("")
        logger.info("✅ ENTRAÎNEMENT RÉUSSI!")
        logger.info("")
        logger.info("📊 RÉSULTATS:")
        logger.info(f"   Précision: {results['evaluation']['accuracy']*100:.2f}%")
        logger.info(f"   Precision: {results['evaluation']['precision']*100:.2f}%")
        logger.info(f"   Recall: {results['evaluation']['recall']*100:.2f}%")
        logger.info(f"   F1-Score: {results['evaluation']['f1_score']*100:.2f}%")
        logger.info("")
        logger.info(f"   Nombre de cas: {results['training']['n_samples']}")
        logger.info(f"   Nombre de features: {results['training']['n_features']}")
        logger.info(f"   Nombre de classes: {results['training']['n_classes']}")
        logger.info(f"   Durée: {results['training']['training_duration_seconds']:.2f}s")
        logger.info("")
        
        if "model_path" in results["training"]:
            logger.info(f"💾 Modèle sauvegardé: {results['training']['model_path']}")
        
        logger.info("")
        logger.info("🎯 PROCHAINES ÉTAPES:")
        logger.info("   1. Démarrer l'API: python -m app.main")
        logger.info("   2. Tester les prédictions via l'API")
        logger.info("   3. Intégrer avec le frontend React")
        
    else:
        logger.error("")
        logger.error("❌ ENTRAÎNEMENT ÉCHOUÉ!")
        logger.error(f"   Erreur: {results.get('error', 'Inconnue')}")
    
    logger.info("")
    logger.info("=" * 80)


if __name__ == "__main__":
    main()
