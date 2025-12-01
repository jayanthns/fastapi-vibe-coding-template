"""
Pytest configuration and fixtures for the FastAPI application.
"""

import asyncio
from pathlib import Path
from uuid import uuid4

# ============================================================================
# GLOBAL DRAMATIQ CONFIGURATION (Must run before test collection)
# ============================================================================
import dramatiq
import pytest
from dramatiq.brokers.stub import StubBroker
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

# Import all models to ensure they are registered with SQLAlchemy
# Import all models to ensure they are registered with SQLAlchemy
from src.apps.animals.models import Animal  # noqa: F401
from src.apps.audit.models import AuditLog  # noqa: F401
from src.apps.background_jobs.middleware import JobTrackingMiddleware
from src.apps.users.models import User  # noqa: F401
from src.db.session import Base

# Configure Dramatiq to use StubBroker globally for all tests
# This ensures that when tasks are imported during test collection,
# they register with this StubBroker instead of a real RedisBroker.
dramatiq_broker = StubBroker()
dramatiq_broker.add_middleware(JobTrackingMiddleware())
dramatiq.set_broker(dramatiq_broker)

# ============================================================================
# CENTRALIZED TEST ORDER MANAGEMENT
# ============================================================================


def pytest_collection_modifyitems(config, items):
    """
    Centralized test order management.
    This function runs after test collection and before test execution.
    """
    from tests.test_config import get_test_order

    # Apply order markers to test items based on centralized configuration
    for item in items:
        file_path = str(item.fspath)
        order = get_test_order(file_path)
        item.add_marker(pytest.mark.order(order))


def pytest_runtest_logstart(nodeid, location):
    """
    Print module labels when each test module starts.
    This provides clear visual separation between different test modules.
    """
    # Extract file path from nodeid (format: path/to/file.py::class::test)
    file_path = nodeid.split("::")[0]
    test_file = Path(file_path)

    # Define module labels based on file patterns
    module_labels = {
        "test_database_pings.py": "🏥 Testing Database Ping APIs",
        "test_cache_pings.py": "🏥 Testing Cache Ping APIs",
        "test_datetime_utils.py": "🔧 Testing DateTime Utilities",
        "test_file_utils.py": "🔧 Testing File Utilities",
        "test_notifications.py": "🔧 Testing Notification System",
        "test_security.py": "🔧 Testing Security Utilities",
        "test_article_apis.py": "📡 Testing Article APIs",
        "test_background_jobs.py": "⚙️ Testing Background Jobs",
    }

    # Get the label for this test file
    label = module_labels.get(test_file.name, f"🧪 Testing {test_file.stem}")

    # Print the label with some styling (only once per module)
    if not hasattr(pytest_runtest_logstart, "_printed_modules"):
        pytest_runtest_logstart._printed_modules = set()

    if test_file.name not in pytest_runtest_logstart._printed_modules:
        print(f"\n{'='*60}")
        print(f"  {label}")
        print(f"{'='*60}")
        pytest_runtest_logstart._printed_modules.add(test_file.name)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def app_fixture():
    """Fixture to provide the FastAPI app instance."""
    print("DEBUG: app_fixture starting")
    # Import app here to ensure it's imported AFTER the dramatiq broker patch
    from src.main import app

    return app


@pytest.fixture(scope="session")
def test_engine():
    """Create a session-scoped async engine for tests."""
    return create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


@pytest.fixture(scope="session", autouse=True)
def patch_global_engine(test_engine):
    """
    Patch the global database engine to use the test engine.
    This ensures src.main.lifespan uses the test DB.
    """
    from unittest.mock import patch

    # Patch the engine in src.db.session
    # We also need to patch it in src.main because it imports it directly
    # But patching src.db.session.engine might be enough if done before src.main import
    with patch("src.db.session.engine", test_engine):
        yield


@pytest.fixture(name="async_session")
async def async_session_fixture(test_engine):
    """Create an async in-memory SQLite database for testing."""
    # Create all tables using our SQLAlchemy Base
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        bind=test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # Clear all tables before each test to ensure isolation
        # We iterate in reverse order of dependencies to avoid FK constraint violations
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

        yield session


@pytest.fixture(name="client")
def client_fixture(async_session: AsyncSession, app_fixture):
    """Create a test client with database dependency override."""
    app = app_fixture
    from src.db.session import get_db, get_db_with_trace_id

    async def get_session_override():
        return async_session

    app.dependency_overrides[get_db_with_trace_id] = get_session_override
    app.dependency_overrides[get_db] = get_session_override

    from unittest.mock import MagicMock, patch

    # Patch RedisBroker to prevent connection attempts during lifespan
    # This is redundant with session fixture but ensures safety at function level
    with patch("dramatiq.brokers.redis.RedisBroker") as MockRedisBroker:
        MockRedisBroker.return_value = MagicMock()

        with patch("dramatiq.set_broker"):
            with TestClient(app) as client:
                yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def configure_dramatiq_broker():
    """
    Ensure Dramatiq broker patches are active during tests.
    Prevents src.main.lifespan from overwriting our global StubBroker.
    """
    print("DEBUG: configure_dramatiq_broker starting")
    from unittest.mock import MagicMock, patch

    # Patch set_broker to prevent src.main.lifespan from overwriting our StubBroker
    # Patch RedisBroker to prevent connection attempts during lifespan
    with (
        patch("dramatiq.set_broker"),
        patch("dramatiq.brokers.redis.RedisBroker") as MockRedisBroker,
    ):

        # Configure MockRedisBroker to return a mock that behaves nicely if accessed
        MockRedisBroker.return_value = MagicMock()

        yield dramatiq_broker
        dramatiq_broker.flush_all()
        dramatiq_broker.close()


@pytest.fixture(name="async_client")
async def async_client_fixture(async_session: AsyncSession, app_fixture):
    """Create an async test client with database dependency override."""
    app = app_fixture
    from httpx import ASGITransport, AsyncClient

    from src.db.session import get_db, get_db_with_trace_id

    async def get_session_override():
        return async_session

    app.dependency_overrides[get_db_with_trace_id] = get_session_override
    app.dependency_overrides[get_db] = get_session_override

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_async_session_local(async_session: AsyncSession):
    """
    Patch AsyncSessionLocal to return the test session.
    This ensures that code using AsyncSessionLocal() directly (like AuditService)
    uses the in-memory SQLite database instead of the real database.
    """
    from unittest.mock import patch

    # Create a context manager that yields the existing async_session
    class MockSessionContext:
        async def __aenter__(self):
            return async_session

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    # Patch the AsyncSessionLocal in src.db.session
    # Patch where it is defined, so imports get the mock
    with patch("src.db.session.AsyncSessionLocal") as mock_session_local:
        mock_session_local.return_value = MockSessionContext()
        yield mock_session_local


# Test data fixtures
@pytest.fixture
def sample_articles_data():
    """Sample article data for testing."""
    return [
        {
            "title": "Test Article 1",
            "content": "This is the first test article content for testing purposes.",
        },
        {
            "title": "Test Article 2",
            "content": "This is the second test article content for testing purposes.",
        },
        {
            "title": "Advanced Testing Article",
            "content": "This article contains more complex content for comprehensive testing.",
        },
    ]


@pytest.fixture
def sample_article_update_data():
    """Sample article update data for testing."""
    return {
        "title": "Updated Test Article",
        "content": "This is updated test article content with new information.",
    }


@pytest.fixture
def sample_article_search_queries():
    """Sample search queries for testing article search functionality."""
    return [
        "test",
        "article",
        "content",
        "advanced",
        "testing",
    ]


@pytest.fixture
def sample_article_authors():
    """Sample authors for testing article author functionality."""
    return [
        "John Doe",
        "Jane Smith",
        "Test Author",
        "Advanced Tester",
    ]


@pytest.fixture
def sample_article_tags():
    """Sample tags for testing article tag functionality."""
    return [
        ["test", "api", "integration"],
        ["advanced", "testing", "comprehensive"],
        ["sample", "data", "fixture"],
        ["pytest", "fastapi", "sqlalchemy"],
    ]


@pytest.fixture
def sample_article_edge_cases():
    """Sample edge case data for testing article edge cases."""
    return [
        {
            "title": "A" * 255,  # Maximum length title
            "content": "Short content",
        },
        {
            "title": "Short title",
            "content": "A" * 10000,  # Very long content
        },
        {
            "title": "Unicode Test: 测试文章标题 🚀",
            "content": "Unicode content: 这是一个测试文章的内容。Special chars: @#$%^&*()",
        },
        {
            "title": "Special Characters: !@#$%^&*()_+-=[]{}|;':\",./<>?",
            "content": "Content with special characters and symbols.",
        },
    ]


# Mock fixtures for testing
@pytest.fixture
def mock_article():
    """Mock article object for testing."""
    article_id = str(uuid4())
    return type(
        "MockArticle",
        (),
        {
            "id": article_id,
            "title": "Test Article",
            "content": "This is a test article content for testing purposes.",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        },
    )()


@pytest.fixture
def mock_articles_list():
    """Mock articles list for testing."""
    return [
        type(
            "MockArticle",
            (),
            {
                "id": str(uuid4()),
                "title": "Article 1",
                "content": "Content 1",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )(),
        type(
            "MockArticle",
            (),
            {
                "id": str(uuid4()),
                "title": "Article 2",
                "content": "Content 2",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
            },
        )(),
    ]
