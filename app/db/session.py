from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


# Create engine without echo to avoid duplicate SQL logging
engine = create_async_engine(settings.database_url, echo=False, future=True)  # type: ignore
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_db_with_trace_id(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session with trace_id-aware logging (only in development environment).

    Usage:
        @router.get("/")
        async def endpoint(request: Request, db=Depends(get_db_with_trace_id)):
            # Database operations will be logged with trace_id (development only)
            pass
    """
    from app.middleware.trace import get_trace_id
    from app.core.sqlalchemy_logging import setup_sqlalchemy_logging

    trace_id = get_trace_id(request)

    # Setup SQLAlchemy logging with trace_id (only in development)
    setup_sqlalchemy_logging(trace_id)

    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        # Clean up logging handlers (only if they were set up)
        from app.core.config import settings
        from app.core.sqlalchemy_logging import clear_sqlalchemy_logging

        # Only clear if we're in development (where logging was set up)
        if settings.environment == "development":
            clear_sqlalchemy_logging()
