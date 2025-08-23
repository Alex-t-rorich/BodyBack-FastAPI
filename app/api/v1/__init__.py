# app/api/v1/__init__.py
"""
API v1 endpoints
"""

from .auth import router as auth_router
from .users import router as users_router
from .profiles import router as profiles_router

__all__ = [
    "auth_router",
    "users_router", 
    "profiles_router"
]