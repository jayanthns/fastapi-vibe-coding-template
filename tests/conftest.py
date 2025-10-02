"""
Shared test fixtures and configuration.
"""

import os
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.db.session import Base, get_db
from src.main import app


# Test database configuration - using PostgreSQL test database
# Read credentials from environment variables
def get_test_database_url():
    """Get test database URL from environment variables."""
    import os
    from urllib.parse import quote_plus

    # Get database credentials from environment
    db_host = os.getenv("DATABASE_HOST", "localhost")
    db_port = os.getenv("DATABASE_PORT", "5432")
    db_user = os.getenv("DATABASE_USERNAME", "postgres")
    db_password = os.getenv("DATABASE_PASSWORD", "postgres")
    db_name = os.getenv("DATABASE_NAME", "fastapi_vibe_coding")

    # Create test database name
    test_db_name = f"{db_name}_test"

    # URL encode password to handle special characters
    encoded_password = quote_plus(db_password)

    return f"postgresql+asyncpg://{db_user}:{encoded_password}@{db_host}:{db_port}/{test_db_name}"


TEST_DATABASE_URL = get_test_database_url()


# Override the database URL for tests
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database before running tests."""
    # Set test database URL
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL

    # Create test database engine
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    import asyncio

    async def create_tables():
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    # Run in the current event loop if available, otherwise create new one
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, create a task
            asyncio.create_task(create_tables())
        else:
            asyncio.run(create_tables())
    except RuntimeError:
        asyncio.run(create_tables())

    yield

    # Cleanup after tests - simplified to avoid event loop issues
    try:
        # Just dispose the engine, let the database handle cleanup
        test_engine.sync_engine.dispose()
    except Exception:
        pass  # Ignore cleanup errors


@pytest.fixture
def client():
    """Create test client for database ping endpoints."""
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
    with patch("app.core.logging.get_logger") as mock:
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
