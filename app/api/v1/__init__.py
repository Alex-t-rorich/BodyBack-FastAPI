# app/api/v1/__init__.py
"""
API v1 endpoints
"""

from .auth import router as auth_router
from .users import router as users_router
from .profiles import router as profiles_router
from .trainers import router as trainers_router
from .customers import router as customers_router
from .qr_codes import router as qr_codes_router
from .sessions import router as sessions_router

__all__ = [
    "auth_router",
    "users_router", 
    "profiles_router",
    "trainers_router",
    "customers_router",
    "qr_codes_router",
    "sessions_router"
]