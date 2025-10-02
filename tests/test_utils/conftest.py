"""
Conftest for utils tests - no database required.
"""

import pytest


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment for utils tests."""
    # This fixture runs automatically before each test
    # No database setup needed for utils tests
    pass
