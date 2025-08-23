import logging
from fastapi import APIRouter

# Import standalone route modules
from .health import router as health_router
from .root import router as root_router

# Import API routes
from app.api.v1 import auth_router, users_router, profiles_router, trainers_router

# TODO: Import other API routes when created
# from .api.customers import router as customers_router
# from .api.sync import router as sync_router

logger = logging.getLogger(__name__)

# Main application router
router = APIRouter()

# Include standalone routes (no prefix)
router.include_router(root_router, tags=["root"])
router.include_router(health_router, tags=["health"])

# Include API routes with prefixes
router.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
router.include_router(users_router, prefix="/api/v1/users", tags=["users"])
router.include_router(profiles_router, prefix="/api/v1/profiles", tags=["profiles"])
router.include_router(trainers_router, prefix="/api/v1/trainers", tags=["trainers"])

# TODO: Include other API routes with prefixes when created
# router.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
# router.include_router(sync_router, prefix="/api/v1/sync", tags=["sync"])

logger.info("Main router configured with all routes")