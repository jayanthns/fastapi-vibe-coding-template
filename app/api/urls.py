"""
Centralized URL configuration for the API - Django-style organization.
This file acts as the main URL dispatcher, similar to Django's urls.py.
"""

from fastapi import APIRouter

from app.api.v1 import articles, background_jobs, pings

# Create the main API router
api_router = APIRouter()

# Include versioned API routes
api_router.include_router(articles.router, prefix="/v1/articles", tags=["articles"])
api_router.include_router(
    background_jobs.router, prefix="/v1", tags=["background-jobs"]
)
api_router.include_router(pings.router, prefix="/v1/pings", tags=["cache-health"])

# You can add more versioned routes here as your API grows
# Example:
# api_router.include_router(
#     users.router,
#     prefix="/v1/users",
#     tags=["users"]
# )

# For future API versions (v2, v3, etc.):
# api_router.include_router(
#     articles_v2.router,
#     prefix="/v2/articles",
#     tags=["articles-v2"]
# )
