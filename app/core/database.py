# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import all models to ensure they're registered with Base
from app.models import Base, User, Customer, Trainer, Role, Profile, SessionVolume, SessionTracking, QRCode
from .config import settings

# Database configuration with connection pool settings
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_timeout=settings.DB_POOL_TIMEOUT,
    pool_recycle=settings.DB_POOL_RECYCLE,
    echo=settings.DEBUG_MODE  # Log SQL queries in debug mode
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)