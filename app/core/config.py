# app/core/config.py
# Add these to your existing config.py

import os
import logging
import sys
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Existing settings...
    
    # API Configuration
    PROJECT_NAME: str = "BodyBack Middleware"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Server Configuration  
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not os.getenv("DEBUG_MODE", "true").lower() == "true" else "DEBUG")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    LOG_FILE: str = os.getenv("LOG_FILE", "")  # Empty = console only
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # SendPulse Configuration
    SENDPULSE_USER_ID: str = os.getenv("SENDPULSE_USER_ID", "")
    SENDPULSE_SECRET: str = os.getenv("SENDPULSE_SECRET", "")
    SENDPULSE_BOT_ID: str = os.getenv("SENDPULSE_BOT_ID", "")
    
    # Sync Configuration
    SYNC_BATCH_SIZE: int = int(os.getenv("SYNC_BATCH_SIZE", "5"))
    SYNC_LOCK_TIMEOUT: int = int(os.getenv("SYNC_LOCK_TIMEOUT", "600"))
    
    class Config:
        case_sensitive = True

settings = Settings()

def setup_logging():
    """Configure logging for the entire application"""
    
    # Create formatter
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if specified)
    if settings.LOG_FILE:
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Suppress noisy third-party loggers in production
    if not settings.DEBUG_MODE:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
    
    # Log configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured - Level: {settings.LOG_LEVEL}")
    if settings.LOG_FILE:
        logger.info(f"Logging to file: {settings.LOG_FILE}")