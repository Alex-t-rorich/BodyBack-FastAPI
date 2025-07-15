# main.py
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings, setup_logging
from app.core.database import create_tables
from app.routes.routes import router

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting up {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Create database tables
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Application shutdown complete")

# FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="FastAPI application with PostgreSQL database and organized routing",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Include all routes from the main router
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host=settings.HOST, 
        port=settings.PORT, 
        reload=settings.DEBUG_MODE,
        log_config=None  # Use our custom logging config
    )