from fastapi import APIRouter

# Import routers from Django-style apps
from src.apps.articles.router import router as articles_router
from src.apps.pings.cache_router import router as cache_router
from src.apps.pings.database_router import router as database_router
from src.apps.sensitive_fields.router import router as sensitive_fields_router
from src.apps.users.router import router as users_router

api_router = APIRouter()

# Include app routers
api_router.include_router(articles_router, prefix="/v1/articles", tags=["articles"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(
    sensitive_fields_router, prefix="/v1/sensitive-fields", tags=["sensitive-fields"]
)

# Include ping routers with separate prefixes
api_router.include_router(cache_router, prefix="/v1/pings/cache", tags=["cache-pings"])
api_router.include_router(
    database_router, prefix="/v1/pings/db", tags=["database-pings"]
)
