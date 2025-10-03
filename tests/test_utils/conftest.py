# Conftest for utility tests with database setup
import asyncio

import pytest
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings

# Create test database engine
test_engine = create_async_engine(
    settings.database_url.replace("fastapi_vibe_coding", "fastapi_vibe_coding_test"),
    echo=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database for utility tests."""

    async def create_tables():
        async with test_engine.begin() as conn:
            # Import all models to ensure they're registered
            from src.apps.articles.models import Article
            from src.apps.sensitive_fields.models import SensitiveField
            from src.apps.users.models import User

            # Create all tables
            from sqlalchemy import text
            await conn.run_sync(
                lambda sync_conn: sync_conn.execute(
                    text("CREATE SCHEMA IF NOT EXISTS public")
                )
            )
            await conn.run_sync(
                lambda sync_conn: sync_conn.execute(
                    text("DROP SCHEMA IF EXISTS public CASCADE")
                )
            )
            await conn.run_sync(
                lambda sync_conn: sync_conn.execute(text("CREATE SCHEMA public"))
            )

            # Create tables
            from src.db.session import Base

            await conn.run_sync(Base.metadata.create_all)

    # Run the async setup
    asyncio.run(create_tables())

    yield

    # Cleanup - simplified to avoid async loop issues
    try:
        asyncio.run(test_engine.dispose())
    except Exception:
        pass  # Ignore cleanup errors
