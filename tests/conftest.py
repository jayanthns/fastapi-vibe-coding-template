"""
Pytest configuration and fixtures for the FastAPI application.
"""

import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Import all models to ensure they are registered with SQLAlchemy
from src.apps.articles.models import Article
from src.apps.sensitive_fields.models import SensitiveField
from src.apps.users.models import User
from src.db.session import Base, get_db_with_trace_id
from src.main import app

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


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(name="async_session")
async def async_session_fixture():
    """Create an async in-memory SQLite database for testing using SQLAlchemy Base."""
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Create all tables using our SQLAlchemy Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_maker = async_sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(async_session: AsyncSession):
    """Create a test client with database dependency override."""

    async def get_session_override():
        return async_session

    app.dependency_overrides[get_db_with_trace_id] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


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
