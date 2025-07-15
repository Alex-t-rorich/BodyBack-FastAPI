import logging
from fastapi import APIRouter

# Import standalone route modules
from .health import router as health_router
from .root import router as root_router

# TODO: Import API routes when created
# from .api.customers import router as customers_router
# from .api.sync import router as sync_router

logger = logging.getLogger(__name__)

# Main application router
router = APIRouter()

# Include standalone routes (no prefix)
router.include_router(root_router, tags=["root"])
router.include_router(health_router, tags=["health"])

# TODO: Include API routes with prefixes when created
# router.include_router(customers_router, prefix="/api/v1/customers", tags=["customers"])
# router.include_router(sync_router, prefix="/api/v1/sync", tags=["sync"])

logger.info("Main router configured with all routes")