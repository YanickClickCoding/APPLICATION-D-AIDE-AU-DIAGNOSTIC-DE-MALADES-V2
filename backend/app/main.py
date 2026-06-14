"""
FastAPI Main Application
Medical Diagnostic AI System
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
import traceback

from .config import settings
from .database import engine, Base
from .utils.logger import setup_logging
from .ml.model_manager import model_manager
from .routers import (
    auth_router,
    patients_router,
    consultations_router,
    ml_router,
    ml_public_router,
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

    # Générer le cache des symptômes au démarrage (depuis CSV + règles custom + modèle)
    try:
        from .routers.admin import _save_symptomes_cache
        _save_symptomes_cache()
        logger.info("✅ Cache symptômes généré au démarrage")
    except Exception as e:
        logger.warning(f"⚠️ Cache symptômes non généré au démarrage : {e}")

    # Synchroniser en arrière-plan les données géographiques OMS (carte du monde).
    # Non bloquant : le backend démarre tout de suite, la MAJ se fait en fond.
    try:
        from .services.who_data_sync import start_background_sync
        start_background_sync()
    except Exception as e:
        logger.warning(f"⚠️ Sync OMS non lancée au démarrage : {e}")

    logger.info("✅ Application prête!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Arrêt de l'application...")


# Créer l'application FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Système de diagnostic médical assisté par IA utilisant Random Forest",
    lifespan=lifespan,
    redirect_slashes=False  # Désactiver la redirection automatique du trailing slash
)

# ── Middleware : log chaque requête HTTP + capture erreurs 500 ────────────────
@app.middleware("http")
async def http_logging_middleware(request: Request, call_next):
    start = time.time()
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start) * 1000
        level = logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(level,
            f"{request.method} {request.url.path} → {response.status_code} "
            f"({duration_ms:.0f}ms)"
        )
        return response
    except Exception as exc:
        duration_ms = (time.time() - start) * 1000
        logger.error(
            f"{request.method} {request.url.path} → 500 EXCEPTION ({duration_ms:.0f}ms)\n"
            + traceback.format_exc()
        )
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erreur interne: {str(exc)}"}
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
app.include_router(ml_public_router, prefix="/api")
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
