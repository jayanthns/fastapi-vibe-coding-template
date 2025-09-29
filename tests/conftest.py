"""
Shared test fixtures and configuration.
"""

from unittest.mock import AsyncMock, patch

import pytest


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
