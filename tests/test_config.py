"""
Centralized test configuration and ordering management.

This file provides a single source of truth for test execution order,
making it easy to manage and modify test priorities across the entire test suite.
"""

# ============================================================================
# TEST EXECUTION ORDER CONFIGURATION
# ============================================================================

# Define test execution order based on file patterns
# Lower numbers run first, higher numbers run last
TEST_ORDER_CONFIG = {
    # Order 1: Health checks and ping tests (fastest, most critical)
    "test_api/test_database_pings.py": 1,
    "test_api/test_cache_pings.py": 1,
    # Order 2: Core utility tests (foundational functionality)
    "test_utils/test_datetime_utils.py": 2,
    "test_utils/test_file_utils.py": 2,
    "test_utils/test_notifications.py": 2,
    "test_utils/test_security.py": 2,
    # Order 3: API integration tests (business logic)
    "test_api/test_article_apis.py": 3,
    # Add more API tests here as they are created
    # "test_api/test_user_apis.py": 3,
    # "test_api/test_sensitive_field_apis.py": 3,
    # Order 4: Background job tests (slowest, resource intensive)
    "test_background_jobs.py": 4,
    # Order 5: End-to-end integration tests (if any)
    # "test_integration/": 5,
    # Order 6: Performance tests (if any)
    # "test_performance/": 6,
}

# Default order for any unmatched test files
DEFAULT_ORDER = 99

# Test categories for better organization
TEST_CATEGORIES = {
    "health_checks": [1, 2],  # Orders 1-2
    "utilities": [2],  # Order 2
    "api_tests": [3],  # Order 3
    "background_jobs": [4],  # Order 4
    "integration": [5],  # Order 5
    "performance": [6],  # Order 6
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_test_order(file_path: str) -> int:
    """
    Get the execution order for a test file.

    Args:
        file_path: Path to the test file

    Returns:
        Order number (lower = earlier execution)
    """
    for pattern, order in TEST_ORDER_CONFIG.items():
        if pattern in file_path:
            return order
    return DEFAULT_ORDER


def get_test_category(file_path: str) -> str:
    """
    Get the category for a test file.

    Args:
        file_path: Path to the test file

    Returns:
        Category name
    """
    order = get_test_order(file_path)
    for category, orders in TEST_CATEGORIES.items():
        if order in orders:
            return category
    return "unknown"


def is_health_check(file_path: str) -> bool:
    """Check if a test file is a health check."""
    return get_test_category(file_path) == "health_checks"


def is_api_test(file_path: str) -> bool:
    """Check if a test file is an API test."""
    return get_test_category(file_path) == "api_tests"


def is_background_job_test(file_path: str) -> bool:
    """Check if a test file is a background job test."""
    return get_test_category(file_path) == "background_jobs"


# ============================================================================
# CONFIGURATION VALIDATION
# ============================================================================


def validate_config():
    """Validate the test configuration."""
    # Check for negative orders
    orders = list(TEST_ORDER_CONFIG.values())
    if any(order < 0 for order in orders):
        raise ValueError("Negative orders are not allowed")

    # Check for reasonable order range
    if max(orders) > 100:
        print("⚠️  Warning: Very high order numbers detected")

    print("✅ Test configuration is valid")
    from collections import Counter

    order_counts = Counter(orders)
    print(f"📊 Order distribution: {dict(order_counts)}")


if __name__ == "__main__":
    # Run validation when this file is executed directly
    validate_config()
    print("📋 Test order configuration:")
    for pattern, order in sorted(TEST_ORDER_CONFIG.items(), key=lambda x: x[1]):
        print(f"  Order {order}: {pattern}")
