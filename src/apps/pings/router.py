"""
Pings app router - combines cache and database health checks.
"""

from fastapi import APIRouter

from src.apps.pings.cache_router import router as cache_router
from src.apps.pings.database_router import router as database_router

router = APIRouter()

# Include cache ping routes
router.include_router(cache_router, tags=["cache-health"])

# Include database ping routes
router.include_router(database_router, tags=["database-health"])
