# app/core/config.py
# Add these to your existing config.py

import os
import logging
import sys
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/database_name")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    
    # API Configuration
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "BodyBack Middleware")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
    
    # Server Configuration  
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "true").lower() == "true"
    
    # Security Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not os.getenv("DEBUG_MODE", "true").lower() == "true" else "DEBUG")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s")
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
    
    # CORS Settings
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080")
    ALLOWED_METHODS: str = os.getenv("ALLOWED_METHODS", "GET,POST,PUT,DELETE,OPTIONS")
    ALLOWED_HEADERS: str = os.getenv("ALLOWED_HEADERS", "*")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
    
    # File Upload Settings
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "uploads")
    ALLOWED_FILE_TYPES: str = os.getenv("ALLOWED_FILE_TYPES", "jpg,jpeg,png,gif,pdf")
    
    model_config = {'case_sensitive': True}

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