"""
Pings app router - combines all ping and health check endpoints.
"""

from fastapi import APIRouter

from src.apps.pings.cache_router import router as cache_router
from src.apps.pings.database_router import router as database_router
from src.apps.pings.external_router import router as external_router
from src.apps.pings.system_router import router as system_router

router = APIRouter()

# Include system ping routes (basic ping/pong)
router.include_router(system_router, prefix="/system", tags=["system-health"])

# Include cache ping routes
router.include_router(cache_router, prefix="/cache", tags=["cache-health"])

# Include database ping routes
router.include_router(database_router, prefix="/db", tags=["database-health"])

# Include external endpoint ping routes
router.include_router(external_router, prefix="/external", tags=["external-pings"])
