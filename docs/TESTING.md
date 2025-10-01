# Testing Guide

This document describes the testing setup and configuration for the FastAPI application.

## Test Configuration

The project uses **pytest** as the testing framework with comprehensive configuration in `pyproject.toml`.

### Key Features

- ✅ **Async test support** with `pytest-asyncio`
- ✅ **Coverage reporting** with `pytest-cov`
- ✅ **Test timeouts** with `pytest-timeout`
- ✅ **Test markers** for categorizing tests
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
testpaths = ["app/tests", "tests"]
norecursedirs = ["venv", ".venv", "env", ".env", ".git", "dist", "build"]
addopts = ["-v", "--tb=short", "--strict-markers", "--color=yes"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests"
]
asyncio_mode = "auto"
timeout = 300
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

## Continuous Integration

For CI/CD pipelines, use:

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=app --cov-report=xml --cov-fail-under=80

# Run only fast tests in CI
pytest -m "not slow"
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
