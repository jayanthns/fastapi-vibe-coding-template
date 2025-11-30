# Testing Guide

We use **pytest** for testing, with **pytest-asyncio** for async support.

## Running Tests

### Standard Run
Run all tests with coverage:
```bash
make pytest
```

### Specific Tests
Run tests matching a keyword:
```bash
make pytest-k K=test_create_animal
```

Run a specific file:
```bash
pytest tests/test_api/test_animals_scenarios.py
```

### Fast Tests
Run tests excluding slow ones (marked with `@pytest.mark.slow`):
```bash
make test-fast
```

## Writing Tests

### 1. Test Structure
Tests are located in `tests/`.
- `tests/test_api/`: Integration tests for API endpoints.
- `tests/test_unit/`: Unit tests for services/utils.

### 2. Fixtures (`conftest.py`)
Common fixtures are defined in `tests/conftest.py`:
- `async_client`: An `httpx.AsyncClient` for making API requests.
- `db_session`: An isolated database session (rolls back after each test).
- `test_app`: The FastAPI application instance with overrides.

### 3. Example Integration Test

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_animal(async_client: AsyncClient):
    payload = {"name": "Rex", "species": "Dog"}
    response = await async_client.post("/api/v1/animals/", json=payload)
    
    assert response.status_code == 201
    data = response.json()["data"]
    assert data["name"] == "Rex"
    assert "id" in data
```

### 4. Database Isolation
Tests use an **in-memory SQLite database** by default (configured in `conftest.py`). This ensures tests are fast and isolated.
Dependency overrides are used to replace the production `get_db` with the test database session.

### 5. Mocking
Use `unittest.mock` or `pytest-mock` for external services (e.g., S3, Email).

```python
def test_notification(mocker):
    mock_send = mocker.patch("src.utils.notifications.send_email")
    # ... trigger logic ...
    mock_send.assert_called_once()
```

## Coverage
We aim for **80% code coverage**.
HTML reports are generated in `coverage_html_report/`.
Open the report:
```bash
make test-report
```
