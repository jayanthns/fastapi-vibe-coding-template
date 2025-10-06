# Testing Guide

This document describes the testing setup and configuration for the FastAPI application.

## Test Configuration

The project uses **pytest** as the testing framework with comprehensive configuration in `pyproject.toml`.

### Key Features

- ✅ **Async test support** with `pytest-asyncio`
- ✅ **Coverage reporting** with `pytest-cov`
- ✅ **Test timeouts** with `pytest-timeout`
- ✅ **Test markers** for categorizing tests
- ✅ **Test ordering** with `pytest-order` for logical execution flow
- ✅ **Virtual environment exclusion** (venv, .venv, etc.)
- ✅ **Colored output** and verbose reporting
- ✅ **Performance monitoring** (shows 10 slowest tests)

## Test Structure

```sh
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_background_jobs.py  # Background jobs tests
└── ...                      # Additional test files
```

## Test Discovery

Tests are automatically discovered from:

- `tests/` directory
- Files matching `test_*.py` or `*_test.py` patterns
- Classes starting with `Test`
- Functions starting with `test_`

## Excluded Directories

The following directories are automatically excluded from test discovery:

- `venv`, `.venv` - Virtual environments
- `env`, `.env` - Environment directories
- `.git` - Git repository
- `dist`, `build` - Build artifacts
- `__pycache__`, `.pytest_cache` - Cache directories
- `tmp`, `logs` - Temporary and log files

## Test Markers

Tests can be categorized using markers:

```python
@pytest.mark.slow
def test_long_running_operation():
    """This test takes a long time to run."""
    pass

@pytest.mark.integration
def test_api_integration():
    """This is an integration test."""
    pass

@pytest.mark.unit
def test_unit_functionality():
    """This is a unit test."""
    pass

@pytest.mark.api
def test_api_endpoint():
    """This tests an API endpoint."""
    pass

@pytest.mark.background
def test_background_job():
    """This tests background job functionality."""
    pass
```

## Test Ordering

The project uses a **centralized test order management system** to ensure tests run in a logical sequence for optimal feedback and debugging.

### 🎯 Centralized Order Management

All test execution order is managed from a single configuration file: `tests/test_config.py`

```python
# tests/test_config.py - Single source of truth for test order
TEST_ORDER_CONFIG = {
    # Order 1: Health checks (fastest, most critical)
    "test_api/test_database_pings.py": 1,
    "test_api/test_cache_pings.py": 1,

    # Order 2: Core utilities (foundational functionality)
    "test_utils/test_datetime_utils.py": 2,
    "test_utils/test_file_utils.py": 2,
    "test_utils/test_notifications.py": 2,
    "test_utils/test_security.py": 2,

    # Order 3: API integration tests (business logic)
    "test_api/test_article_apis.py": 3,

    # Order 4: Background job tests (slowest, resource intensive)
    "test_background_jobs.py": 4,
}
```

### Execution Order

Tests are executed in the following priority order:

1. **🏥 Ping Tests (Order 1)** - Health checks and connectivity tests
2. **🔧 Utility Tests (Order 2)** - Core utility functions and helpers
3. **📡 API Tests (Order 3)** - Article and other API integration tests
4. **⚙️ Background Job Tests (Order 4)** - Long-running and complex operations

### How It Works

1. **Configuration**: All test orders defined in `tests/test_config.py`
2. **Automatic Application**: `conftest.py` automatically applies orders using `pytest_collection_modifyitems`
3. **No Manual Markers**: Individual test files don't need order markers
4. **Dynamic Assignment**: Orders applied based on file path patterns

### Benefits of Centralized Ordering

- **🎛️ Single Source of Truth**: All test order managed in one file
- **⚡ Easy to Modify**: Change order by updating one configuration dictionary
- **🔧 No Impact on Other Modules**: Adding new tests doesn't require updating existing files
- **📋 Automatic Application**: Orders applied automatically via pytest hooks
- **✅ Validation**: Built-in validation to catch configuration errors
- **📚 Documentation**: Clear comments explaining each order level
- **🏷️ Visual Module Labels**: Clear labels printed for each test module during execution

### Modifying Test Order

To change test execution order, **only edit `tests/test_config.py`**:

```python
# Move articles to order 2 (before utilities)
"test_api/test_article_apis.py": 2,

# Move background jobs to order 3
"test_background_jobs.py": 3,

# Add new test files
"test_api/test_user_apis.py": 3,
"test_integration/": 5,
```

### Validating Configuration

```bash
# Validate test configuration
python tests/test_config.py

# Output:
# ✅ Test configuration is valid
# 📊 Order distribution: {1: 2, 2: 4, 3: 1, 4: 1}
# 📋 Test order configuration:
#   Order 1: test_api/test_database_pings.py
#   Order 1: test_api/test_cache_pings.py
#   Order 2: test_utils/test_datetime_utils.py
#   ...
```

### Order-Specific Commands

```bash
# Run tests in the specified order
make test-pings    # Quick health checks first
make test-utils    # Core utilities second
make test-last     # Background jobs last

# Or run all tests with the new ordering
make pytest-all    # All tests with coverage
```

### Visual Module Labels

During test execution, each test module displays a clear label indicating what's being tested:

```text
============================================================
  🏥 Testing Database Ping APIs
============================================================

============================================================
  🔧 Testing DateTime Utilities
============================================================

============================================================
  📡 Testing Article APIs
============================================================

============================================================
  ⚙️ Testing Background Jobs
============================================================
```

**Module Label Icons:**

- 🏥 **Ping Tests**: Health checks and connectivity tests
- 🔧 **Utility Tests**: Core utility functions and helpers
- 📡 **API Tests**: Article and other API integration tests
- ⚙️ **Background Jobs**: Long-running and complex operations

**Benefits:**

- **Clear Visual Separation**: Easy to see which module is currently running
- **Progress Tracking**: Know exactly what's being tested at any moment
- **Debugging Aid**: Quickly identify which module has issues
- **Professional Output**: Clean, organized test execution display

## Running Tests

### Using Makefile Commands (Recommended)

```bash
# Run all tests
make test

# Run tests with verbose output
make test-verbose

# Run tests with coverage report
make test-coverage

# Run only fast tests (exclude slow tests)
make test-fast

# Run specific test categories
make test-unit
make test-integration
make test-api
make test-background

# Run tests in logical order
make test-pings    # Ping tests first (health checks)
make test-utils    # Utility tests second (core functions)
make test-last     # Background job tests last (complex operations)

# Run tests with coverage and HTML reports
make pytest-all    # All tests with coverage + HTML report
make pytest-fast   # Fast tests only (excludes slow tests)
make pytest-slow   # Slow tests only

# Run tests in watch mode (requires pytest-watch)
make test-watch
```

### Using pytest Directly

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_background_jobs.py

# Run tests matching pattern
pytest -k "test_job"

# Run tests with specific marker
pytest -m "not slow"
pytest -m "integration"
pytest -m "unit"

# Run tests with timeout
pytest --timeout=60

# Run tests in parallel (requires pytest-xdist)
pytest -n auto
```

## Test Fixtures

### Shared Fixtures (conftest.py)

```python
@pytest.fixture
def mock_request():
    """Mock FastAPI Request object."""
    request = AsyncMock()
    request.state.trace_id = "test-trace-id-123"
    return request

@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("app.core.logging.get_logger") as mock:
        mock_logger = AsyncMock()
        mock.return_value = mock_logger
        yield mock_logger

@pytest.fixture
def sample_article_data():
    """Sample article data for testing."""
    return {
        "title": "Test Article",
        "content": "This is a test article content."
    }
```

### Using Fixtures in Tests

```python
def test_article_creation(sample_article_data, mock_logger):
    """Test article creation with fixtures."""
    # Use the sample data
    article = create_article(sample_article_data)
    assert article.title == "Test Article"

    # Verify logging was called
    mock_logger.info.assert_called_once()

@pytest.mark.asyncio
async def test_async_operation(mock_request):
    """Test async operation with mock request."""
    trace_id = mock_request.state.trace_id
    assert trace_id == "test-trace-id-123"
```

## Async Testing

The project supports async testing with `pytest-asyncio`:

```python
@pytest.mark.asyncio
async def test_background_job():
    """Test async background job."""
    job_service = BackgroundJobService()

    job_id = await job_service.create_job(
        job_type="test_job",
        parameters={"test": "value"},
        trace_id="test-trace"
    )

    assert job_id is not None
```

## Coverage Reporting

Coverage reports are generated in multiple formats:

- **Terminal**: Shows missing lines in terminal
- **HTML**: Generates `htmlcov/index.html` for detailed coverage
- **XML**: Generates `coverage.xml` for CI/CD integration

```bash
# Generate coverage report
make test-coverage

# View HTML coverage report
open htmlcov/index.html
```

## Test Configuration Files

### pyproject.toml (Primary Configuration)

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
norecursedirs = ["venv", ".venv", "env", ".env", ".git", "dist", "build", "__pycache__", ".pytest_cache", ".mypy_cache", ".coverage", "tmp", "logs"]
addopts = ["-v", "--tb=short", "--strict-markers", "--strict-config", "--disable-warnings", "--color=yes", "--durations=10", "--cov=src", "--cov-report=term-missing", "--cov-report=html", "--cov-report=xml", "--cov-fail-under=80"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "api: marks tests as API tests",
    "background: marks tests as background job tests",
    "pings: marks tests as ping/health check tests (run first)",
    "utils: marks tests as utility tests (run middle)",
    "last: marks tests to run last (background jobs)"
]
asyncio_mode = "auto"
minversion = "8.0"

[tool.coverage.run]
branch = true
omit = ["**/tests/*", "**/migrations/*.py", "**/urls.py", "**/settings/*", "**/wsgi.py", "**/asgi.py", "manage.py", "fabfile.py", "settings.py", "**/endpoints.py", "**/admin.py", "**/venv/**", "**/.venv/**", "**/env/**", "**/.env/**", "**/__pycache__/**", "**/.pytest_cache/**", "**/.mypy_cache/**", "**/.coverage/**", "**/tmp/**", "**/logs/**"]
source = ["src"]

[tool.coverage.report]
show_missing = true
precision = 2
fail_under = 80
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]

[tool.coverage.html]
directory = "htmlcov"
```

### pytest.ini (Alternative Configuration)

The `pytest.ini` file provides an alternative configuration format, though `pyproject.toml` takes precedence.

## Best Practices

### 1. Test Organization

- Group related tests in classes
- Use descriptive test names
- Keep tests focused and atomic
- Use appropriate markers for categorization

### 2. Async Testing

- Always use `@pytest.mark.asyncio` for async tests
- Use `AsyncMock` for mocking async functions
- Test both success and failure scenarios

### 3. Fixtures

- Use fixtures for common test data
- Keep fixtures simple and focused
- Use `autouse=True` sparingly
- Share fixtures via `conftest.py`

### 4. Mocking

- Mock external dependencies
- Use `patch` context managers
- Verify mock calls when important
- Don't over-mock internal code

### 5. Performance

- Mark slow tests with `@pytest.mark.slow`
- Use `make test-fast` for quick feedback
- Monitor test execution times
- Consider parallel execution for large test suites

### 6. Test Ordering

- **Centralized Management**: All test order managed in `tests/test_config.py`
- **Single Source of Truth**: Never add order markers to individual test files
- **Logical Sequence**: Run critical health checks first (ping tests)
- **Progressive Complexity**: Place utility tests in the middle, background jobs last
- **Easy Modification**: Change order by updating the configuration dictionary
- **Validation**: Use `python tests/test_config.py` to validate configuration
- **Order-Specific Commands**: Use `make test-pings`, `make test-utils`, `make test-last`

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests with coverage (ordered execution)
pytest --cov=src --cov-report=xml --cov-fail-under=80

# Run only fast tests in CI (excludes slow background jobs)
pytest -m "not slow"

# Run tests in logical order for better feedback (centralized ordering)
make test-pings    # Health checks first (Order 1)
make test-utils    # Core utilities second (Order 2)
make test-last     # Background jobs last (Order 4, if time permits)

# Or run all tests with automatic ordering
make pytest-all    # All tests with centralized order management
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Async Test Failures**: Check `@pytest.mark.asyncio` decorator
3. **Mock Issues**: Verify mock setup and assertions
4. **Slow Tests**: Use `-m "not slow"` to skip slow tests

### Debug Mode

```bash
# Run tests with debug output
pytest -v -s --tb=long

# Run specific test with debug
pytest -v -s tests/test_background_jobs.py::TestBackgroundJobService::test_create_job
```

## Examples

See `tests/test_background_jobs.py` for comprehensive examples of:

- Unit tests for service classes
- Integration tests for background jobs
- Async test patterns
- Mock usage
- Test markers and categorization
- Fixture usage
