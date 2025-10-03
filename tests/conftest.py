"""
Comprehensive test fixtures and configuration for all test types.
This single conftest.py handles both API tests and utility tests.
"""

import asyncio
import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.main import app

# Test database configuration
TEST_DATABASE_URL = settings.database_url.replace(
    "fastapi_vibe_coding", "postgres_test"
)
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database for all tests that need database access."""

    async def create_tables():
        async with test_engine.begin() as conn:
            # Import all models to ensure they're registered
            # Create all tables
            from sqlalchemy import text

            from src.apps.articles.models import Article
            from src.apps.sensitive_fields.models import SensitiveField
            from src.apps.users.models import User

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


@pytest.fixture
def client():
    """Create test client for API endpoints."""
    return TestClient(app)


@pytest.fixture
def mock_request():
    """Mock FastAPI Request object."""
    request = AsyncMock()
    request.state.trace_id = "test-trace-id-123"
    request.state.start_time = 1234567890.0
    return request


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("src.core.logging.get_logger") as mock:
        mock_logger = AsyncMock()
        mock.return_value = mock_logger
        yield mock_logger


@pytest.fixture
def mock_trace_id():
    """Mock trace ID for testing."""
    return "test-trace-id-456"


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # This fixture runs automatically before each test
    # You can add any global test setup here
    pass


@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        "title": "Test Article",
        "content": "This is a test article content for testing purposes.",
    }


@pytest.fixture
def sample_job_parameters():
    """Sample job parameters for testing."""
    return {
        "article_id": 123,
        "processing_time": 1,
        "recipient": "test@example.com",
        "subject": "Test Email",
        "report_type": "test_report",
        "date_range": "2024-01",
    }


@pytest.fixture
def test_engine_fixture():
    """Provide test database engine for utility tests."""
    return test_engine
