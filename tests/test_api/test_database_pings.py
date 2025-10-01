"""
Unit tests for database ping and health check endpoints.

Tests all database ping functionality including connectivity, read/write access,
DDL operations, and database information retrieval.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError

from app.main import app


class TestDatabasePing:
    """Test the main database ping endpoint."""

    def test_ping_database_success(self, client: TestClient):
        """Test successful database ping."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            # Mock database connection and query
            mock_db = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_db.execute.return_value = mock_result

            # Mock connection pool
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_pool.invalid.return_value = 0

            mock_bind = MagicMock()
            mock_bind.pool = mock_pool
            mock_bind.dialect.name = "postgresql"
            mock_db.get_bind.return_value = mock_bind

            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/ping")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Database ping successful"
            assert data["data"]["status"] == "healthy"
            assert data["data"]["test_query_result"] == 1
            assert "response_time_ms" in data["data"]
            assert "connection_pool" in data["data"]
            assert data["data"]["database_type"] == "postgresql"

    def test_ping_database_sqlalchemy_error(self, client: TestClient):
        """Test database ping with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("Connection failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/ping")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Database connection failed" in data["message"]
            assert data["data"]["status"] == "unhealthy"
            assert "Connection failed" in data["data"]["error"]

    def test_ping_database_unexpected_result(self, client: TestClient):
        """Test database ping with unexpected query result."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_result = MagicMock()
            mock_result.scalar.return_value = 0  # Unexpected result
            mock_db.execute.return_value = mock_result

            # Mock connection pool
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_pool.invalid.return_value = 0

            mock_bind = MagicMock()
            mock_bind.pool = mock_pool
            mock_bind.dialect.name = "postgresql"
            mock_db.get_bind.return_value = mock_bind

            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/ping")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is False
            assert "unexpected result" in data["message"]
            assert data["data"]["status"] == "unhealthy"
            assert data["data"]["test_query_result"] == 0


class TestDatabaseRead:
    """Test the database read access endpoint."""

    def test_database_read_success(self, client: TestClient):
        """Test successful database read operation."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_result = MagicMock()
            mock_result.fetchone.return_value = (
                "read_test",
                5,
                "2024-01-01 12:00:00",
                "PostgreSQL 15.0",
            )
            mock_db.execute.return_value = mock_result
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/read")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Database read test successful"
            assert data["data"]["status"] == "healthy"
            assert data["data"]["operation"] == "read_test"
            assert "response_time_ms" in data["data"]
            assert "result" in data["data"]

    def test_database_read_sqlalchemy_error(self, client: TestClient):
        """Test database read with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("Read operation failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/read")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Database read test failed" in data["message"]
            assert data["data"]["status"] == "unhealthy"
            assert data["data"]["operation"] == "read_test"


class TestDatabaseWrite:
    """Test the database write access endpoint."""

    def test_database_write_success(self, client: TestClient):
        """Test successful database write operations."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()

            # Mock different query results
            def mock_execute(query):
                mock_result = MagicMock()
                if "CREATE TEMPORARY TABLE" in str(query):
                    mock_result.rowcount = 0
                elif "INSERT" in str(query):
                    mock_result.rowcount = 1
                elif "UPDATE" in str(query):
                    mock_result.rowcount = 1
                elif "SELECT COUNT" in str(query):
                    mock_result.scalar.return_value = 1
                elif "DELETE" in str(query):
                    mock_result.rowcount = 1
                else:
                    mock_result.rowcount = 0
                return mock_result

            mock_db.execute.side_effect = mock_execute
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/write")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Database write test successful"
            assert data["data"]["status"] == "healthy"
            assert data["data"]["operation"] == "write_test"
            assert "response_time_ms" in data["data"]
            assert "results" in data["data"]
            assert data["data"]["results"]["insert_count"] == 1
            assert data["data"]["results"]["update_count"] == 1
            assert data["data"]["results"]["delete_count"] == 1

    def test_database_write_sqlalchemy_error(self, client: TestClient):
        """Test database write with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("Write operation failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/write")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Database write test failed" in data["message"]
            assert data["data"]["status"] == "unhealthy"
            assert data["data"]["operation"] == "write_test"


class TestDatabaseDDL:
    """Test the database DDL operations endpoint."""

    def test_database_ddl_success(self, client: TestClient):
        """Test successful database DDL operations."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()

            # Mock DDL operations
            def mock_execute(query):
                mock_result = MagicMock()
                if "CREATE TEMPORARY TABLE" in str(query):
                    mock_result.rowcount = 0
                elif "ALTER TABLE" in str(query):
                    mock_result.rowcount = 0
                elif "SELECT EXISTS" in str(query):
                    mock_result.scalar.return_value = True
                else:
                    mock_result.rowcount = 0
                return mock_result

            mock_db.execute.side_effect = mock_execute

            # Mock inspector
            mock_inspector = MagicMock()
            mock_inspector.get_columns.return_value = [
                {"name": "id"},
                {"name": "name"},
                {"name": "description"},
                {"name": "created_at"},
            ]

            mock_bind = MagicMock()
            mock_bind.dialect.name = "postgresql"
            mock_db.get_bind.return_value = mock_bind

            with patch(
                "app.api.v1.database_pings.inspect", return_value=mock_inspector
            ):
                mock_get_db.return_value = mock_db

                response = client.get("/api/v1/db/ddl")

                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["message"] == "Database DDL test successful"
                assert data["data"]["status"] == "healthy"
                assert data["data"]["operation"] == "ddl_test"
                assert "response_time_ms" in data["data"]
                assert "results" in data["data"]
                assert data["data"]["results"]["table_created"] is True
                assert "id" in data["data"]["results"]["columns"]

    def test_database_ddl_sqlalchemy_error(self, client: TestClient):
        """Test database DDL with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("DDL operation failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/ddl")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Database DDL test failed" in data["message"]
            assert data["data"]["status"] == "unhealthy"
            assert data["data"]["operation"] == "ddl_test"


class TestDatabaseInfo:
    """Test the database information endpoint."""

    def test_database_info_success(self, client: TestClient):
        """Test successful database info retrieval."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()

            # Mock different query results
            def mock_execute(query):
                mock_result = MagicMock()
                if "SELECT VERSION()" in str(query):
                    mock_result.scalar.return_value = "PostgreSQL 15.0"
                elif "SELECT DATABASE()" in str(query):
                    mock_result.scalar.return_value = "test_db"
                elif "SELECT ROUND(SUM" in str(query):
                    mock_result.scalar.return_value = 1024.5
                elif "SELECT COUNT(*) as table_count" in str(query):
                    mock_result.scalar.return_value = 10
                elif "SHOW PROCESSLIST" in str(query):
                    mock_result.fetchall.return_value = [
                        ("1", "user", "localhost", "test_db", "Query", 0, "")
                    ]
                else:
                    mock_result.scalar.return_value = None
                return mock_result

            mock_db.execute.side_effect = mock_execute

            # Mock connection pool
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_pool.invalid.return_value = 0

            mock_bind = MagicMock()
            mock_bind.pool = mock_pool
            mock_bind.dialect.name = "postgresql"
            mock_db.get_bind.return_value = mock_bind

            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/info")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Database information retrieved successfully"
            assert data["data"]["status"] == "healthy"
            assert "database" in data["data"]
            assert "connection_pool" in data["data"]
            assert "statistics" in data["data"]
            assert data["data"]["database"]["version"] == "PostgreSQL 15.0"
            assert data["data"]["database"]["name"] == "test_db"

    def test_database_info_sqlalchemy_error(self, client: TestClient):
        """Test database info with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("Info query failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/info")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Failed to get database information" in data["message"]
            assert data["data"]["status"] == "unhealthy"


class TestDatabaseTables:
    """Test the database tables listing endpoint."""

    def test_database_tables_success(self, client: TestClient):
        """Test successful database tables listing."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()

            # Mock table query result
            mock_result = MagicMock()
            mock_result.fetchall.return_value = [
                (
                    "articles",
                    "BASE TABLE",
                    100,
                    1.5,
                    "2024-01-01 10:00:00",
                    "2024-01-01 12:00:00",
                ),
                ("users", "BASE TABLE", 50, 0.8, "2024-01-01 09:00:00", None),
            ]
            mock_db.execute.return_value = mock_result
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/tables")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["message"] == "Retrieved 2 tables"
            assert data["data"]["status"] == "healthy"
            assert data["data"]["total_tables"] == 2
            assert len(data["data"]["tables"]) == 2

            # Check first table
            first_table = data["data"]["tables"][0]
            assert first_table["name"] == "articles"
            assert first_table["type"] == "BASE TABLE"
            assert first_table["rows"] == 100
            assert first_table["size_mb"] == 1.5

    def test_database_tables_sqlalchemy_error(self, client: TestClient):
        """Test database tables with SQLAlchemy error."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()
            mock_db.execute.side_effect = SQLAlchemyError("Tables query failed")
            mock_get_db.return_value = mock_db

            response = client.get("/api/v1/db/tables")

            assert response.status_code == 503
            data = response.json()
            assert data["success"] is False
            assert "Failed to list database tables" in data["message"]
            assert data["data"]["status"] == "unhealthy"


class TestDatabasePingIntegration:
    """Integration tests for database ping endpoints."""

    def test_all_endpoints_accessible(self, client: TestClient):
        """Test that all database ping endpoints are accessible."""
        endpoints = [
            "/api/v1/db/ping",
            "/api/v1/db/read",
            "/api/v1/db/write",
            "/api/v1/db/ddl",
            "/api/v1/db/info",
            "/api/v1/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # Should not return 404 (endpoint not found)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"

    def test_response_format_consistency(self, client: TestClient):
        """Test that all endpoints return consistent response format."""
        with patch("app.api.v1.database_pings.get_db") as mock_get_db:
            mock_db = AsyncMock()

            # Mock successful responses for all endpoints
            def mock_execute(query):
                mock_result = MagicMock()
                if "SELECT 1" in str(query):
                    mock_result.scalar.return_value = 1
                elif "SELECT 'read_test'" in str(query):
                    mock_result.fetchone.return_value = (
                        "read_test",
                        5,
                        "2024-01-01 12:00:00",
                        "PostgreSQL 15.0",
                    )
                elif "CREATE TEMPORARY TABLE" in str(query):
                    mock_result.rowcount = 0
                elif "INSERT" in str(query):
                    mock_result.rowcount = 1
                elif "UPDATE" in str(query):
                    mock_result.rowcount = 1
                elif "SELECT COUNT" in str(query):
                    mock_result.scalar.return_value = 1
                elif "DELETE" in str(query):
                    mock_result.rowcount = 1
                elif "SELECT VERSION()" in str(query):
                    mock_result.scalar.return_value = "PostgreSQL 15.0"
                elif "SELECT DATABASE()" in str(query):
                    mock_result.scalar.return_value = "test_db"
                elif "SELECT ROUND(SUM" in str(query):
                    mock_result.scalar.return_value = 1024.5
                elif "SELECT COUNT(*) as table_count" in str(query):
                    mock_result.scalar.return_value = 10
                elif "SHOW PROCESSLIST" in str(query):
                    mock_result.fetchall.return_value = [
                        ("1", "user", "localhost", "test_db", "Query", 0, "")
                    ]
                elif "SELECT table_name" in str(query):
                    mock_result.fetchall.return_value = [
                        (
                            "articles",
                            "BASE TABLE",
                            100,
                            1.5,
                            "2024-01-01 10:00:00",
                            "2024-01-01 12:00:00",
                        )
                    ]
                else:
                    mock_result.scalar.return_value = None
                return mock_result

            mock_db.execute.side_effect = mock_execute

            # Mock connection pool
            mock_pool = MagicMock()
            mock_pool.size.return_value = 10
            mock_pool.checkedin.return_value = 8
            mock_pool.checkedout.return_value = 2
            mock_pool.overflow.return_value = 0
            mock_pool.invalid.return_value = 0

            mock_bind = MagicMock()
            mock_bind.pool = mock_pool
            mock_bind.dialect.name = "postgresql"
            mock_db.get_bind.return_value = mock_bind

            # Mock inspector for DDL test
            mock_inspector = MagicMock()
            mock_inspector.get_columns.return_value = [
                {"name": "id"},
                {"name": "name"},
                {"name": "description"},
                {"name": "created_at"},
            ]

            with patch(
                "app.api.v1.database_pings.inspect", return_value=mock_inspector
            ):
                mock_get_db.return_value = mock_db

                endpoints = [
                    "/api/v1/db/ping",
                    "/api/v1/db/read",
                    "/api/v1/db/write",
                    "/api/v1/db/ddl",
                    "/api/v1/db/info",
                    "/api/v1/db/tables",
                ]

                for endpoint in endpoints:
                    response = client.get(endpoint)
                    assert response.status_code == 200
                    data = response.json()

                    # Check consistent response structure
                    assert "success" in data
                    assert "message" in data
                    assert "data" in data
                    assert "trace_id" in data
                    assert "timestamp" in data

                    # Check data structure
                    assert "status" in data["data"]
                    assert data["data"]["status"] == "healthy"


@pytest.fixture
def client():
    """Create test client for database ping endpoints."""
    return TestClient(app)
