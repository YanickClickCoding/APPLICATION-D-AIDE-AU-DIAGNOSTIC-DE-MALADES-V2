"""
API routers
"""
from .patients import router as patients_router
from .consultations import router as consultations_router
from .ml_prediction import router as ml_router
from .analytics import router as analytics_router

__all__ = [
    "patients_router",
    "consultations_router",
    "ml_router",
    "analytics_router"
]
