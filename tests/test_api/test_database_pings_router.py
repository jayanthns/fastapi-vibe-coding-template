import pytest
from unittest.mock import MagicMock, AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from fastapi import status
from src.db.session import get_db


@pytest.fixture
def mock_db_session(app_fixture):
    mock_session = AsyncMock()
    # get_bind is a synchronous method on the session
    mock_session.get_bind = MagicMock()
    app = app_fixture
    app.dependency_overrides[get_db] = lambda: mock_session
    yield mock_session
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_db_info_success(async_client, mock_db_session):
    # Mock version query result
    mock_result_version = MagicMock()
    mock_result_version.scalar.return_value = "PostgreSQL 15.0"

    # Mock db name query result
    mock_result_name = MagicMock()
    mock_result_name.scalar.return_value = "test_db"

    # Mock size query result
    mock_result_size = MagicMock()
    mock_result_size.scalar.return_value = 100.5

    # Mock table count query result
    mock_result_count = MagicMock()
    mock_result_count.scalar.return_value = 10

    # Mock connections query result
    mock_result_connections = MagicMock()
    mock_result_connections.fetchall.return_value = [1, 2, 3]

    # Setup side effects for execute
    # We need to match the queries. Since they are text objects, direct comparison is hard.
    # We can just return different mocks based on call count or use side_effect with logic.
    # But for simplicity, let's just return a generic mock that can handle all scalar/fetchall calls
    # or use side_effect to return specific results.

    async def execute_side_effect(query, *args, **kwargs):
        query_str = str(query).upper()
        if "VERSION()" in query_str:
            return mock_result_version
        elif "DATABASE()" in query_str:
            return mock_result_name
        elif "PG_TOTAL_RELATION_SIZE" in query_str:
            return mock_result_size
        elif "COUNT(*)" in query_str:
            return mock_result_count
        elif "SHOW PROCESSLIST" in query_str:
            return mock_result_connections
        return MagicMock()

    mock_db_session.execute.side_effect = execute_side_effect

    # Mock pool info
    mock_engine = MagicMock()
    mock_pool = MagicMock()
    mock_pool.size.return_value = 5
    mock_pool.checkedin.return_value = 2
    mock_pool.checkedout.return_value = 3
    mock_pool.overflow.return_value = 0
    mock_pool.invalid.return_value = 0
    mock_engine.pool = mock_pool
    mock_db_session.get_bind.return_value = mock_engine

    response = await async_client.get("/api/v1/pings/db/info")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["database"]["version"] == "PostgreSQL 15.0"
    assert data["database"]["name"] == "test_db"
    assert data["statistics"]["size_mb"] == 100.5
    assert data["statistics"]["table_count"] == 10
    assert data["statistics"]["active_connections"] == 3


@pytest.mark.asyncio
async def test_db_tables_success(async_client, mock_db_session):
    mock_result = MagicMock()
    # name, type, rows, size_mb, created, updated
    mock_result.fetchall.return_value = [
        ("users", "BASE TABLE", 100, 10.5, "2024-01-01", "2024-01-02"),
        ("posts", "BASE TABLE", 500, 50.2, "2024-01-01", "2024-01-03"),
    ]
    mock_db_session.execute.return_value = mock_result

    response = await async_client.get("/api/v1/pings/db/tables")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()["data"]
    assert data["total_tables"] == 2
    assert data["tables"][0]["name"] == "users"
    assert data["tables"][1]["name"] == "posts"


@pytest.mark.asyncio
async def test_db_info_failure(async_client, mock_db_session):
    mock_db_session.execute.side_effect = SQLAlchemyError("DB Error")

    response = await async_client.get("/api/v1/pings/db/info")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Failed to get database information" in response.json()["message"]


@pytest.mark.asyncio
async def test_db_tables_failure(async_client, mock_db_session):
    mock_db_session.execute.side_effect = SQLAlchemyError("DB Error")

    response = await async_client.get("/api/v1/pings/db/tables")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Failed to list database tables" in response.json()["message"]


@pytest.mark.asyncio
async def test_db_ping_success(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 1
    mock_db_session.execute.return_value = mock_result

    mock_engine = MagicMock()
    mock_pool = MagicMock()
    mock_pool.size.return_value = 5
    mock_pool.checkedin.return_value = 2
    mock_pool.checkedout.return_value = 3
    mock_pool.overflow.return_value = 0
    mock_pool.invalid.return_value = 0
    mock_engine.pool = mock_pool
    mock_engine.dialect.name = "postgresql"
    mock_db_session.get_bind.return_value = mock_engine

    response = await async_client.get("/api/v1/pings/db/ping")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_db_ping_failure_unexpected_result(async_client, mock_db_session):
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0  # Unexpected result
    mock_db_session.execute.return_value = mock_result

    mock_engine = MagicMock()
    mock_pool = MagicMock()
    mock_pool.size.return_value = 5
    mock_pool.checkedin.return_value = 2
    mock_pool.checkedout.return_value = 3
    mock_pool.overflow.return_value = 0
    mock_pool.invalid.return_value = 0
    mock_engine.pool = mock_pool
    mock_db_session.get_bind.return_value = mock_engine

    response = await async_client.get("/api/v1/pings/db/ping")

    # The endpoint returns 200 OK but with success=False and status=unhealthy in data
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is False
    assert response.json()["data"]["status"] == "unhealthy"


@pytest.mark.asyncio
async def test_db_ping_failure_exception(async_client, mock_db_session):
    mock_db_session.execute.side_effect = SQLAlchemyError("Connection failed")

    response = await async_client.get("/api/v1/pings/db/ping")

    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "Database connection failed" in response.json()["message"]
