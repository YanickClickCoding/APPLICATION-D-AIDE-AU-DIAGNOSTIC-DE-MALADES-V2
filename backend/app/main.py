"""
FastAPI Main Application
Medical Diagnostic AI System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import engine, Base
from .utils.logger import setup_logging
from .ml.model_manager import model_manager
from .routers import (
    auth_router,
    patients_router,
    consultations_router,
    ml_router,
    analytics_router,
    admin_router,
)

# Configuration du logging
setup_logging(
    log_level=settings.LOG_LEVEL,
    log_file=settings.LOG_FILE
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle events: startup and shutdown
    """
    # Startup
    logger.info("🚀 Démarrage de l'application...")
    logger.info(f"   Environnement: {settings.ENVIRONMENT}")
    logger.info(f"   Version: {settings.APP_VERSION}")
    
    # Créer les tables si elles n'existent pas
    # Note: En production, utiliser Alembic pour les migrations
    # Base.metadata.create_all(bind=engine)
    
    # Charger le modèle ML
    logger.info("📦 Chargement du modèle ML...")
    model_loaded = model_manager.load_latest_model(settings.MODEL_PATH)
    
    if model_loaded:
        logger.info("✅ Modèle ML chargé avec succès")
        model_info = model_manager.get_model_info()
        logger.info(f"   Version: {model_info['version']}")
        logger.info(f"   Classes: {model_info['n_classes']}")
        logger.info(f"   Features: {model_info['n_features']}")
    else:
        logger.warning("⚠️ Aucun modèle ML chargé")
        logger.warning("   Entraînez un modèle avec le script d'entraînement")
    
    logger.info("✅ Application prête!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de l'application...")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système de diagnostic médical assisté par IA utilisant Random Forest",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrer les routers avec le préfixe /api
app.include_router(auth_router, prefix="/api")
app.include_router(patients_router, prefix="/api")
app.include_router(consultations_router, prefix="/api")
app.include_router(ml_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(admin_router, prefix="/api")


@app.get("/")
def root():
    """
    Root endpoint
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "model_loaded": model_manager.model_loaded
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "model_loaded": model_manager.model_loaded,
        "database": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
