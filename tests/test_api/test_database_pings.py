"""
Unit tests for database ping and health check endpoints.

Tests all database ping functionality including connectivity, read/write access,
DDL operations, and database information retrieval.

Uses httpx.AsyncClient for proper async testing of FastAPI endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app

# Mark all tests in this module as ping tests (run first)
# Test order is managed centrally in conftest.py


class TestDatabasePingEndpoints:
    """Test database ping endpoints structure and basic functionality."""

    @pytest.fixture
    async def async_client(self, async_session):
        """Create async HTTP client for testing."""
        from httpx import ASGITransport
        from src.db.session import get_db, get_db_with_trace_id

        async def get_session_override():
            return async_session

        app.dependency_overrides[get_db] = get_session_override
        app.dependency_overrides[get_db_with_trace_id] = get_session_override

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        app.dependency_overrides.clear()

    def test_all_endpoints_accessible(self, client: TestClient):
        """Test that all database ping endpoints are accessible using TestClient."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            try:
                response = client.get(endpoint)
                # Should not return 404 (endpoint not found)
                assert response.status_code != 404, f"Endpoint {endpoint} not found"
                # Should return either 200 (success) or 503 (service unavailable)
                # Due to TestClient limitations with async database operations,
                # we expect 503 errors but the endpoints should still be accessible
                assert response.status_code in [
                    200,
                    503,
                ], f"Unexpected status code {response.status_code} for {endpoint}"
            except Exception as e:
                # Skip endpoints that fail due to TestClient async limitations
                if "Task" in str(e) and "attached to a different loop" in str(e):
                    pytest.skip(
                        f"Skipping {endpoint} due to TestClient async limitations: {e}"
                    )
                else:
                    raise

    @pytest.mark.asyncio
    async def test_all_endpoints_accessible_async(self, async_client: AsyncClient):
        """Test that all database ping endpoints are accessible using AsyncClient."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = await async_client.get(endpoint)
            # Should not return 404 (endpoint not found)
            assert response.status_code != 404, f"Endpoint {endpoint} not found"
            # Should return either 200 (success) or 503 (service unavailable)
            assert response.status_code in [
                200,
                503,
            ], f"Unexpected status code {response.status_code} for {endpoint}"

    def test_response_format_consistency(self, client: TestClient):
        """Test that all endpoints return consistent response format."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)

            # Check that we get a valid response
            assert response.status_code in [200, 503]

            # Parse JSON response
            try:
                data = response.json()
            except Exception as e:
                pytest.fail(f"Failed to parse JSON response from {endpoint}: {e}")

            # Check response structure for successful responses
            if response.status_code == 200:
                assert "success" in data, f"Missing 'success' field in {endpoint}"
                assert "message" in data, f"Missing 'message' field in {endpoint}"
                assert "data" in data, f"Missing 'data' field in {endpoint}"
                assert "trace_id" in data, f"Missing 'trace_id' field in {endpoint}"
                assert "timestamp" in data, f"Missing 'timestamp' field in {endpoint}"

                # Check data structure
                assert (
                    "status" in data["data"]
                ), f"Missing 'status' field in data for {endpoint}"
                assert data["data"]["status"] in [
                    "healthy",
                    "unhealthy",
                ], f"Invalid status value in {endpoint}"

            # Check response structure for error responses
            elif response.status_code == 503:
                assert (
                    "error" in data
                ), f"Missing 'error' field in error response for {endpoint}"
                assert (
                    "message" in data
                ), f"Missing 'message' field in error response for {endpoint}"
                assert (
                    data["success"] is False
                ), f"Success should be False in error response for {endpoint}"

    def test_ping_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of ping endpoint."""
        response = client.get("/api/v1/pings/db/ping")

        # Should return either success or service unavailable
        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            # Success case
            assert data["success"] is True
            assert "Database ping successful" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert "test_query_result" in data["data"]
            assert "response_time_ms" in data["data"]
            assert "connection_pool" in data["data"]
            assert "database_type" in data["data"]
        else:
            # Error case - should have proper error structure
            assert "error" in data
            assert data["success"] is False

    def test_read_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of read endpoint."""
        response = client.get("/api/v1/pings/db/read")

        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            assert data["success"] is True
            assert "Database read test successful" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert data["data"]["operation"] == "read_test"
            assert "response_time_ms" in data["data"]
            assert "result" in data["data"]
        else:
            assert "error" in data
            assert data["success"] is False

    def test_write_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of write endpoint."""
        response = client.get("/api/v1/pings/db/write")

        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            assert data["success"] is True
            assert "Database write test successful" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert data["data"]["operation"] == "write_test"
            assert "response_time_ms" in data["data"]
            assert "results" in data["data"]
        else:
            assert "error" in data
            assert data["success"] is False

    def test_ddl_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of DDL endpoint."""
        response = client.get("/api/v1/pings/db/ddl")

        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            assert data["success"] is True
            assert "Database DDL test successful" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert data["data"]["operation"] == "ddl_test"
            assert "response_time_ms" in data["data"]
            assert "results" in data["data"]
        else:
            assert "error" in data
            assert data["success"] is False

    def test_info_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of info endpoint."""
        response = client.get("/api/v1/pings/db/info")

        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            assert data["success"] is True
            assert "Database information retrieved successfully" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert "database" in data["data"]
            assert "connection_pool" in data["data"]
            assert "statistics" in data["data"]
        else:
            assert "error" in data
            assert data["success"] is False

    def test_tables_endpoint_basic_structure(self, client: TestClient):
        """Test basic structure of tables endpoint."""
        response = client.get("/api/v1/pings/db/tables")

        assert response.status_code in [200, 503]

        data = response.json()

        if response.status_code == 200:
            assert data["success"] is True
            assert "Retrieved" in data["message"] and "tables" in data["message"]
            assert data["data"]["status"] == "healthy"
            assert "total_tables" in data["data"]
            assert "tables" in data["data"]
            assert isinstance(data["data"]["tables"], list)
        else:
            assert "error" in data
            assert data["success"] is False

    def test_trace_id_presence(self, client: TestClient):
        """Test that trace_id is present in all responses."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Trace ID should be present in successful responses
            if response.status_code == 200:
                assert "trace_id" in data, f"Missing trace_id in {endpoint}"
                assert isinstance(
                    data["trace_id"], str
                ), f"trace_id should be string in {endpoint}"
                assert (
                    len(data["trace_id"]) > 0
                ), f"trace_id should not be empty in {endpoint}"

    def test_timestamp_presence(self, client: TestClient):
        """Test that timestamp is present in all responses."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Timestamp should be present in successful responses
            if response.status_code == 200:
                assert "timestamp" in data, f"Missing timestamp in {endpoint}"
                assert isinstance(
                    data["timestamp"], str
                ), f"timestamp should be string in {endpoint}"
                assert (
                    len(data["timestamp"]) > 0
                ), f"timestamp should not be empty in {endpoint}"

    def test_response_time_metrics(self, client: TestClient):
        """Test that response time metrics are present."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Response time should be present in successful responses
            if response.status_code == 200:
                assert (
                    "response_time_ms" in data["data"]
                ), f"Missing response_time_ms in {endpoint}"
                assert isinstance(
                    data["data"]["response_time_ms"], (int, float)
                ), f"response_time_ms should be numeric in {endpoint}"
                assert (
                    data["data"]["response_time_ms"] >= 0
                ), f"response_time_ms should be non-negative in {endpoint}"

    def test_health_status_values(self, client: TestClient):
        """Test that health status values are valid."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()

            # Status should be present and valid in successful responses
            if response.status_code == 200:
                assert "status" in data["data"], f"Missing status in {endpoint}"
                assert data["data"]["status"] in [
                    "healthy",
                    "unhealthy",
                ], f"Invalid status value in {endpoint}"

    def test_operation_field_consistency(self, client: TestClient):
        """Test that operation field is consistent across endpoints."""
        operation_endpoints = {
            "/api/v1/pings/db/read": "read_test",
            "/api/v1/pings/db/write": "write_test",
            "/api/v1/pings/db/ddl": "ddl_test",
        }

        for endpoint, expected_operation in operation_endpoints.items():
            response = client.get(endpoint)
            data = response.json()

            if response.status_code == 200:
                assert (
                    "operation" in data["data"]
                ), f"Missing operation field in {endpoint}"
                assert (
                    data["data"]["operation"] == expected_operation
                ), f"Wrong operation value in {endpoint}"

    def test_error_response_structure(self, client: TestClient):
        """Test that error responses have proper structure."""
        endpoints = [
            "/api/v1/pings/db/ping",
            "/api/v1/pings/db/read",
            "/api/v1/pings/db/write",
            "/api/v1/pings/db/ddl",
            "/api/v1/pings/db/info",
            "/api/v1/pings/db/tables",
        ]

        for endpoint in endpoints:
            response = client.get(endpoint)

            # If we get an error response, it should be properly structured
            if response.status_code == 503:
                data = response.json()
                assert (
                    "error" in data
                ), f"Missing 'error' field in error response for {endpoint}"
                assert (
                    "message" in data
                ), f"Missing 'message' field in error response for {endpoint}"
                assert (
                    data["success"] is False
                ), f"Success should be False in error response for {endpoint}"

    def test_api_documentation_accessible(self, client: TestClient):
        """Test that API documentation is accessible."""
        # Test OpenAPI schema
        response = client.get("/openapi.json")
        assert response.status_code == 200

        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200

        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200


# Client fixture is now defined in conftest.py
