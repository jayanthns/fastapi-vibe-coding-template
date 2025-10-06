from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from src.urls import api_router
from src.core.cache import cache
from src.core.config import settings
from src.core.logging import setup_logging
from src.db.session import engine
from src.middleware.trace import TraceIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Setup logging configuration
    setup_logging()


    # Initialize cache service with fallback support
    try:
        ping_result = await cache.ping()
        cache_type = cache.service_type
        is_fallback = getattr(cache, 'is_fallback_active', False)

        if ping_result:
            if is_fallback:
                print(f"✅ {cache_type.title()} cache (fallback) connection established successfully")
                print("   Redis unavailable, using memory cache fallback")
            else:
                print(f"✅ {cache_type.title()} cache connection established successfully")
        else:
            print("⚠️  Cache connection failed - both Redis and memory cache unavailable")
            print("   Cache features will be disabled")
    except Exception as e:
        print(f"⚠️  Cache connection failed: {e}")
        print("   Cache features will be disabled")

    # Ensure engine is created during startup for early DB feedback
    async with engine.begin() as conn:  # noqa: F841
        pass
    yield

    # Cleanup
    if cache.is_redis:
        await cache.close_async_client()


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
    from src.middleware.trace import get_request_logger, get_trace_id

    logger = get_request_logger(request)
    logger.info("Health check requested")

    return {
        "status": "ok",
        "trace_id": get_trace_id(request),
        "timestamp": "2024-01-01T10:00:00Z",
    }


app.include_router(api_router, prefix="/api")
