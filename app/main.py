from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.urls import api_router
from app.core.background_tasks import background_task_manager
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.cache import unified_cache_service
from app.db.session import engine
from app.middleware.trace import TraceIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Setup logging configuration
    setup_logging()

    # Start background task manager
    await background_task_manager.start()

    # Initialize cache service
    try:
        await unified_cache_service.ping()
        cache_type = unified_cache_service.service_type
        print(f"✅ {cache_type.title()} cache connection established successfully")
    except Exception as e:
        print(f"⚠️  Cache connection failed: {e}")
        print("   Cache features will be disabled")

    # Ensure engine is created during startup for early DB feedback
    async with engine.begin() as conn:  # noqa: F841
        pass
    yield

    # Cleanup
    await background_task_manager.stop()
    if unified_cache_service.is_redis:
        await unified_cache_service._get_service().close_async_client()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Add trace ID middleware (should be first to capture all requests)
app.add_middleware(TraceIDMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
async def health_check(request: Request):
    from app.middleware.trace import get_request_logger, get_trace_id

    logger = get_request_logger(request)
    logger.info("Health check requested")

    return {
        "status": "ok",
        "trace_id": get_trace_id(request),
        "timestamp": "2024-01-01T10:00:00Z",
    }


app.include_router(api_router, prefix="/api")
