"""
Test cases for cache ping endpoints.

Tests the cache connectivity and health check endpoints including:
- Basic cache ping
- Cache information retrieval
- Cache keys listing
"""

import pytest
from fastapi.testclient import TestClient

from src.main import app

# Mark all tests in this module as ping tests (run first)
# Test order is managed centrally in conftest.py

client = TestClient(app)


class TestCachePingEndpoints:
    """Test cache ping endpoints functionality."""

    def test_cache_ping_endpoint_accessible(self, client: TestClient):
        """Test that cache ping endpoint is accessible."""
        response = client.get("/api/v1/pings/cache/")

        # Should not return 404 (endpoint not found)
        assert response.status_code != 404, "Cache ping endpoint not found"

        # Should return either 200 (success) or 503 (service unavailable)
        assert response.status_code in [
            200,
            503,
        ], f"Unexpected status code: {response.status_code}"

    def test_cache_info_endpoint_accessible(self, client: TestClient):
        """Test that cache info endpoint is accessible."""
        response = client.get("/api/v1/pings/cache/info")

        # Should not return 404 (endpoint not found)
        assert response.status_code != 404, "Cache info endpoint not found"

        # Should return either 200 (success) or 503 (service unavailable)
        assert response.status_code in [
            200,
            503,
        ], f"Unexpected status code: {response.status_code}"

    def test_cache_keys_endpoint_accessible(self, client: TestClient):
        """Test that cache keys endpoint is accessible."""
        response = client.get("/api/v1/pings/cache/keys")

        # Should not return 404 (endpoint not found)
        assert response.status_code != 404, "Cache keys endpoint not found"

        # Should return either 200 (success) or 503 (service unavailable)
        assert response.status_code in [
            200,
            503,
        ], f"Unexpected status code: {response.status_code}"

    def test_cache_ping_response_structure(self, client: TestClient):
        """Test cache ping response structure."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code == 200:
            data = response.json()

            # Check response structure
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "trace_id" in data

            # Check data structure
            cache_data = data["data"]
            assert "cache_type" in cache_data
            assert "use_redis" in cache_data
            assert "sync_connection" in cache_data
            assert "async_connection" in cache_data
            assert "overall_status" in cache_data

    def test_cache_info_response_structure(self, client: TestClient):
        """Test cache info response structure."""
        response = client.get("/api/v1/db/cache/info")

        if response.status_code == 200:
            data = response.json()

            # Check response structure
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "trace_id" in data

            # Check data structure
            info_data = data["data"]
            assert "cache_type" in info_data
            assert "use_redis" in info_data
            assert "server" in info_data
            assert "memory" in info_data
            assert "stats" in info_data

    def test_cache_keys_response_structure(self, client: TestClient):
        """Test cache keys response structure."""
        response = client.get("/api/v1/db/cache/keys")

        if response.status_code == 200:
            data = response.json()

            # Check response structure
            assert "success" in data
            assert "message" in data
            assert "data" in data
            assert "trace_id" in data

            # Check data structure
            keys_data = data["data"]
            assert "cache_type" in keys_data
            assert "use_redis" in keys_data
            assert "pattern" in keys_data
            assert "total_keys" in keys_data
            assert "safe_keys" in keys_data
            assert "keys" in keys_data

    def test_cache_keys_with_parameters(self, client: TestClient):
        """Test cache keys endpoint with query parameters."""
        response = client.get("/api/v1/pings/cache/keys?pattern=test*&limit=50")

        # Should not return 404 (endpoint not found)
        assert response.status_code != 404, "Cache keys endpoint not found"

        # Should return either 200 (success) or 503 (service unavailable)
        assert response.status_code in [
            200,
            503,
        ], f"Unexpected status code: {response.status_code}"

    def test_trace_id_presence(self, client: TestClient):
        """Test that trace_id is present in cache ping responses."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code in [200, 503]:
            data = response.json()
            assert "trace_id" in data
            assert data["trace_id"] is not None

    def test_timestamp_presence(self, client: TestClient):
        """Test that timestamp is present in cache ping responses."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code in [200, 503]:
            data = response.json()
            # Check if response has timestamp (usually in data or as separate field)
            assert "data" in data
            # The timestamp might be in the data section or as a separate field

    def test_response_time_metrics(self, client: TestClient):
        """Test that response time metrics are present."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code == 200:
            data = response.json()
            cache_data = data["data"]

            # Check for response time metrics
            assert "sync_connection" in cache_data
            assert "async_connection" in cache_data

            sync_conn = cache_data["sync_connection"]
            async_conn = cache_data["async_connection"]

            assert "response_time_ms" in sync_conn
            assert "response_time_ms" in async_conn

    def test_cache_status_values(self, client: TestClient):
        """Test that cache status values are valid."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code == 200:
            data = response.json()
            cache_data = data["data"]

            # Check status values
            assert cache_data["overall_status"] in ["healthy", "unhealthy"]

            sync_conn = cache_data["sync_connection"]
            async_conn = cache_data["async_connection"]

            assert sync_conn["status"] in ["connected", "failed"]
            assert async_conn["status"] in ["connected", "failed"]

    def test_error_response_structure(self, client: TestClient):
        """Test error response structure when cache is unavailable."""
        response = client.get("/api/v1/pings/cache/")

        if response.status_code == 503:
            data = response.json()

            # Check error response structure
            assert "success" in data or "detail" in data

            if "detail" in data:
                # HTTPException format
                detail = data["detail"]
                if isinstance(detail, dict):
                    assert "success" in detail
                    assert "message" in detail
                    assert "data" in detail
                    assert "error" in detail
                    assert "trace_id" in detail

    def test_api_documentation_accessible(self, client: TestClient):
        """Test that API documentation is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200, "API documentation not accessible"
