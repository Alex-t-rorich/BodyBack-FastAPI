import logging
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check():
    # Comprehensive health check endpoint.
    # Tests database connection and returns application status.
    health_status = {
        "status": "healthy",
        "checks": {}
    }
    
    # Test database connection
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
        logger.debug("Health check: Database connection OK")
        
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = {
            "status": "unhealthy", 
            "message": f"Database connection failed: {str(e)}"
        }
        logger.error(f"Health check: Database connection failed - {e}")
    
    # Add more health checks here as needed
    # health_status["checks"]["redis"] = {...}
    # health_status["checks"]["external_api"] = {...}
    
    # Return appropriate HTTP status
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/simple")
async def simple_health_check():
    # Simple health check that just returns OK.
    # Useful for basic uptime monitoring.
    return {"status": "ok", "message": "Service is running"}