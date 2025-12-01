#!/usr/bin/env python3
"""
Test runner script for Article API tests.

This script demonstrates how to run the TestArticleAPIs class
similar to Python's unittest module.
"""

import sys
import unittest
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest  # noqa: E402, isort:skip


from tests.test_api.test_article_apis import TestArticleAPIs  # noqa: E402, isort:skip


def run_article_tests():
    """Run the Article API test suite."""
    print("🧪 Running Article API Test Suite")
    print("=" * 50)

    # Run the specific test class
    test_class_path = "tests/test_api/test_article_apis.py::TestArticleAPIs"

    # Pytest arguments
    pytest_args = [
        test_class_path,
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--durations=10",  # Show 10 slowest tests
        "--cov=src",  # Coverage reporting
        "--cov-report=term-missing",  # Show missing lines
    ]

    print(f"Running: pytest {' '.join(pytest_args)}")
    print()

    # Run pytest
    exit_code = pytest.main(pytest_args)

    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")

    return exit_code


def run_article_tests_unittest():
    """Run the Article API test suite using unittest directly."""
    print("🧪 Running Article API Test Suite (unittest)")
    print("=" * 50)

    # Create a test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestArticleAPIs)

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print(f"\n❌ Tests failed: {len(result.failures)} failures, {len(result.errors)} errors")
        return 1


def run_specific_test_method(test_method: str):
    """Run a specific test method."""
    print(f"🧪 Running specific test: {test_method}")
    print("=" * 50)

    test_path = f"tests/test_api/test_article_apis.py::TestArticleAPIs::{test_method}"

    pytest_args = [
        test_path,
        "-v",
        "--tb=short",
    ]

    print(f"Running: pytest {' '.join(pytest_args)}")
    print()

    exit_code = pytest.main(pytest_args)
    return exit_code


def list_available_tests():
    """List all available test methods in the TestArticleAPIs class."""
    print("📋 Available test methods in TestArticleAPIs:")
    print("=" * 50)

    # Get all test methods from the class
    test_methods = []
    for attr_name in dir(TestArticleAPIs):
        if attr_name.startswith("test_") and callable(getattr(TestArticleAPIs, attr_name)):
            test_methods.append(attr_name)

    # Group tests by category
    categories = {
        "GET Operations": [],
        "POST Operations": [],
        "PATCH Operations": [],
        "DELETE Operations": [],
        "Edge Cases": [],
        "Documentation": [],
        "Integration": [],
        "Other": [],
    }

    for method in sorted(test_methods):
        if "get_article" in method:
            categories["GET Operations"].append(method)
        elif "create_article" in method:
            categories["POST Operations"].append(method)
        elif "update_article" in method:
            categories["PATCH Operations"].append(method)
        elif "delete_article" in method:
            categories["DELETE Operations"].append(method)
        elif "article_with" in method or "concurrent" in method:
            categories["Edge Cases"].append(method)
        elif "api_documentation" in method or "openapi" in method:
            categories["Documentation"].append(method)
        elif "crud_workflow" in method:
            categories["Integration"].append(method)
        else:
            categories["Other"].append(method)

    for category, methods in categories.items():
        if methods:
            print(f"\n{category}:")
            for method in methods:
                print(f"  - {method}")

    print(f"\nTotal: {len(test_methods)} test methods")


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "list":
            list_available_tests()
        elif command == "run":
            if len(sys.argv) > 2:
                test_method = sys.argv[2]
                exit_code = run_specific_test_method(test_method)
            else:
                exit_code = run_article_tests()
            sys.exit(exit_code)
        elif command == "unittest":
            # Run using pure unittest (no pytest)
            exit_code = run_article_tests_unittest()
            sys.exit(exit_code)
        elif command == "help":
            print("Usage:")
            print("  python scripts/run_article_tests.py list          # List available tests")
            print("  python scripts/run_article_tests.py run           # Run all tests (pytest)")
            print("  python scripts/run_article_tests.py unittest      # Run all tests (unittest)")
            print("  python scripts/run_article_tests.py run <method>  # Run specific test")
            print("  python scripts/run_article_tests.py help          # Show this help")
        else:
            print(f"Unknown command: {command}")
            print("Use 'help' to see available commands")
            sys.exit(1)
    else:
        # Default: run all tests with pytest
        exit_code = run_article_tests()
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
