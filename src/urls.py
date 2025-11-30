from fastapi import APIRouter

# Import routers from apps
from src.apps.animals.router import router as animals_router
from src.apps.audit.router import router as audit_router
from src.apps.background_jobs.router import router as background_jobs_router
from src.apps.files.router import router as files_router
from src.apps.pings.router import router as pings_router
from src.apps.users.router import router as users_router

api_router = APIRouter()

# Include app routers
api_router.include_router(animals_router, prefix="/v1/animals", tags=["animals"])
api_router.include_router(audit_router, prefix="/v1/audit", tags=["audit"])
api_router.include_router(files_router, prefix="/v1/files", tags=["files"])
api_router.include_router(pings_router, prefix="/v1/pings", tags=["pings"])
api_router.include_router(users_router, prefix="/v1/users", tags=["users"])
api_router.include_router(background_jobs_router, prefix="/v1/jobs", tags=["jobs"])
