import logging
from fastapi import APIRouter

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/")
async def root():
    # Root endpoint that provides basic application information.
    # Shows welcome message, version, and available endpoints.
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "debug_mode": settings.DEBUG_MODE,
        "environment": "development" if settings.DEBUG_MODE else "production",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "api_v1": settings.API_V1_STR
        },
        "status": "running"
    }

@router.get("/info")
async def app_info():
    # Detailed application information endpoint.
    # Provides more comprehensive details about the application.
    return {
        "project_name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "description": "FastAPI application with PostgreSQL database",
        "debug_mode": settings.DEBUG_MODE,
        "api_version": settings.API_V1_STR,
        "host": settings.HOST,
        "port": settings.PORT
    }