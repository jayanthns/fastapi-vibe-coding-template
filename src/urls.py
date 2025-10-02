from fastapi import APIRouter

# Import routers from Django-style apps
from src.apps.articles.router import router as articles_router
from src.apps.users.router import router as users_router
from src.apps.sensitive_fields.router import router as sensitive_fields_router
from src.apps.background_jobs.router import router as background_jobs_router
from src.apps.pings.router import router as pings_router

api_router = APIRouter()

# Include app routers
api_router.include_router(articles_router, prefix="/v1/articles", tags=["articles"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(sensitive_fields_router, prefix="/v1/sensitive-fields", tags=["sensitive-fields"])
api_router.include_router(background_jobs_router, prefix="/v1/jobs", tags=["background-jobs"])
api_router.include_router(pings_router, prefix="/v1/pings", tags=["pings"])
