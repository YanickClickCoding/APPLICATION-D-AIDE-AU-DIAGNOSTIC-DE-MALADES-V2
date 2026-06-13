"""
API routers
"""
from .auth import router as auth_router
from .patients import router as patients_router
from .consultations import router as consultations_router
from .ml_prediction import router as ml_router, public_router as ml_public_router
from .analytics import router as analytics_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "patients_router",
    "consultations_router",
    "ml_router",
    "ml_public_router",
    "analytics_router",
    "admin_router",
]
