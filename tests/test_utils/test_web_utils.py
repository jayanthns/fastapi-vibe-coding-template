"""
Tests for web utilities module.

This module tests all web utility functions including:
- HTTP Client Utilities
- Retry mechanisms with exponential backoff
- Rate limiting and throttling
- Request/response logging
- Circuit breaker patterns
- HTTP client pooling
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.utils.web_utils import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ConnectionPool,
    HTTPClientManager,
    RateLimitConfig,
    RateLimiter,
    RequestLogger,
    RetryConfig,
    RetryHandler,
    create_circuit_breaker_config,
    create_rate_limit_config,
    create_retry_config,
    delete,
    get,
    http_client,
    make_request,
)
from src.utils.web_utils import patch as patch_request
from src.utils.web_utils import post, put


class TestRetryConfig:
    """Test RetryConfig dataclass."""

    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()
        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.jitter is True
        assert 429 in config.retryable_status_codes
        assert 500 in config.retryable_status_codes

    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            jitter=False,
        )
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.jitter is False


class TestRateLimitConfig:
    """Test RateLimitConfig dataclass."""

    def test_default_config(self):
        """Test default rate limit configuration."""
        config = RateLimitConfig()
        assert config.requests_per_second == 10.0
        assert config.burst_size == 20
        assert config.window_size == 60.0

    def test_custom_config(self):
        """Test custom rate limit configuration."""
        config = RateLimitConfig(
            requests_per_second=5.0, burst_size=10, window_size=30.0
        )
        assert config.requests_per_second == 5.0
        assert config.burst_size == 10
        assert config.window_size == 30.0


class TestCircuitBreakerConfig:
    """Test CircuitBreakerConfig dataclass."""

    def test_default_config(self):
        """Test default circuit breaker configuration."""
        config = CircuitBreakerConfig()
        assert config.failure_threshold == 5
        assert config.recovery_timeout == 60.0
        assert config.expected_exception == httpx.HTTPStatusError
        assert config.success_threshold == 3

    def test_custom_config(self):
        """Test custom circuit breaker configuration."""
        config = CircuitBreakerConfig(
            failure_threshold=3, recovery_timeout=30.0, success_threshold=2
        )
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 30.0
        assert config.success_threshold == 2


class TestRateLimiter:
    """Test RateLimiter class."""

    @pytest.mark.asyncio
    async def test_acquire_token(self):
        """Test token acquisition."""
        config = RateLimitConfig(requests_per_second=10.0, burst_size=2)
        limiter = RateLimiter(config)

        # Should be able to acquire tokens up to burst size
        assert await limiter.acquire() is True
        assert await limiter.acquire() is True
        assert await limiter.acquire() is False  # No more tokens

    @pytest.mark.asyncio
    async def test_token_refill(self):
        """Test token refill over time."""
        config = RateLimitConfig(requests_per_second=10.0, burst_size=1)
        limiter = RateLimiter(config)

        # Acquire initial token
        assert await limiter.acquire() is True
        assert await limiter.acquire() is False

        # Wait for token refill
        await asyncio.sleep(0.2)  # Should refill ~2 tokens
        assert await limiter.acquire() is True

    @pytest.mark.asyncio
    async def test_wait_for_token(self):
        """Test waiting for token availability."""
        config = RateLimitConfig(requests_per_second=10.0, burst_size=1)
        limiter = RateLimiter(config)

        # Acquire initial token
        await limiter.acquire()

        # Wait for token should eventually succeed
        start_time = time.time()
        await limiter.wait_for_token()
        elapsed = time.time() - start_time

        # Should have waited some time
        assert elapsed > 0.05  # At least 50ms


class TestCircuitBreaker:
    """Test CircuitBreaker class."""

    @pytest.mark.asyncio
    async def test_closed_state_success(self):
        """Test circuit breaker in closed state with successful calls."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)

        async def success_func():
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_closed_to_open_transition(self):
        """Test circuit breaker transition from closed to open."""
        config = CircuitBreakerConfig(failure_threshold=2)
        breaker = CircuitBreaker(config)

        async def failing_func():
            raise httpx.HTTPStatusError("Error", request=None, response=None)

        # First failure
        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)
        assert breaker.state == CircuitState.CLOSED

        # Second failure - should open circuit
        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)
        assert breaker.state == CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_open_state_fast_fail(self):
        """Test circuit breaker in open state fails fast."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=1.0)
        breaker = CircuitBreaker(config)

        # Force circuit to open
        async def failing_func():
            raise httpx.HTTPStatusError("Error", request=None, response=None)

        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

        # Should fail fast without calling function
        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_open_to_half_open_transition(self):
        """Test circuit breaker transition from open to half-open."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)

        # Force circuit to open
        async def failing_func():
            raise httpx.HTTPStatusError("Error", request=None, response=None)

        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)

        assert breaker.state == CircuitState.OPEN

        # Wait for recovery timeout
        await asyncio.sleep(0.2)

        # Next call should be in half-open state
        async def success_func():
            return "success"

        result = await breaker.call(success_func)
        assert result == "success"
        assert breaker.state == CircuitState.HALF_OPEN

    @pytest.mark.asyncio
    async def test_half_open_to_closed_transition(self):
        """Test circuit breaker transition from half-open to closed."""
        config = CircuitBreakerConfig(
            failure_threshold=1, recovery_timeout=0.1, success_threshold=2
        )
        breaker = CircuitBreaker(config)

        # Force circuit to open then half-open
        async def failing_func():
            raise httpx.HTTPStatusError("Error", request=None, response=None)

        with pytest.raises(httpx.HTTPStatusError):
            await breaker.call(failing_func)

        await asyncio.sleep(0.2)

        # Successful calls in half-open state
        async def success_func():
            return "success"

        await breaker.call(success_func)
        assert breaker.state == CircuitState.HALF_OPEN

        await breaker.call(success_func)
        assert breaker.state == CircuitState.CLOSED


class TestRetryHandler:
    """Test RetryHandler class."""

    @pytest.mark.asyncio
    async def test_successful_call_no_retry(self):
        """Test successful call without retry."""
        config = RetryConfig(max_attempts=3)
        handler = RetryHandler(config)

        async def success_func():
            return "success"

        result = await handler.execute_with_retry(success_func)
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_retryable_exception(self):
        """Test retry on retryable exception."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        handler = RetryHandler(config)

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.TimeoutException("Timeout")
            return "success"

        result = await handler.execute_with_retry(failing_func)
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_on_http_status_error(self):
        """Test retry on HTTP status error."""
        config = RetryConfig(max_attempts=3, base_delay=0.01)
        handler = RetryHandler(config)

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                response = MagicMock()
                response.status_code = 500
                raise httpx.HTTPStatusError(
                    "Server Error", request=None, response=response
                )
            return "success"

        result = await handler.execute_with_retry(failing_func)
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_no_retry_on_non_retryable_exception(self):
        """Test no retry on non-retryable exception."""
        config = RetryConfig(max_attempts=3)
        handler = RetryHandler(config)

        call_count = 0

        async def failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Non-retryable error")

        with pytest.raises(ValueError):
            await handler.execute_with_retry(failing_func)

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(self):
        """Test behavior when max attempts exceeded."""
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        handler = RetryHandler(config)

        call_count = 0

        async def always_failing_func():
            nonlocal call_count
            call_count += 1
            raise httpx.TimeoutException("Always timeout")

        with pytest.raises(httpx.TimeoutException):
            await handler.execute_with_retry(always_failing_func)

        assert call_count == 2


class TestRequestLogger:
    """Test RequestLogger class."""

    @pytest.mark.asyncio
    async def test_log_request(self):
        """Test request logging."""
        logger = RequestLogger()

        await logger.log_request("GET", "https://example.com", request_size=100)
        logs = await logger.get_logs()

        assert len(logs) == 1
        assert logs[0].method == "GET"
        assert logs[0].url == "https://example.com"
        assert logs[0].request_size == 100

    @pytest.mark.asyncio
    async def test_log_response(self):
        """Test response logging."""
        logger = RequestLogger()

        await logger.log_response(
            "GET", "https://example.com", 200, 0.5, response_size=200
        )
        logs = await logger.get_logs()

        assert len(logs) == 1
        assert logs[0].method == "GET"
        assert logs[0].url == "https://example.com"
        assert logs[0].status_code == 200
        assert logs[0].response_time == 0.5
        assert logs[0].response_size == 200

    @pytest.mark.asyncio
    async def test_log_with_error(self):
        """Test logging with error."""
        logger = RequestLogger()

        await logger.log_response(
            "GET", "https://example.com", None, None, error="Connection failed"
        )
        logs = await logger.get_logs()

        assert len(logs) == 1
        assert logs[0].error == "Connection failed"

    @pytest.mark.asyncio
    async def test_get_logs_with_limit(self):
        """Test getting logs with limit."""
        logger = RequestLogger()

        for i in range(5):
            await logger.log_request("GET", f"https://example{i}.com")

        logs = await logger.get_logs(limit=3)
        assert len(logs) == 3

    @pytest.mark.asyncio
    async def test_clear_logs(self):
        """Test clearing logs."""
        logger = RequestLogger()

        await logger.log_request("GET", "https://example.com")
        assert len(await logger.get_logs()) == 1

        await logger.clear_logs()
        assert len(await logger.get_logs()) == 0


class TestHTTPClientManager:
    """Test HTTPClientManager class."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test HTTPClientManager as context manager."""
        async with HTTPClientManager() as client:
            assert client._client is not None
            assert isinstance(client._client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_close_client(self):
        """Test client closing."""
        client = HTTPClientManager()
        await client._ensure_client()
        assert client._client is not None

        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_make_request_with_mock(self):
        """Test making requests with mocked response."""
        client = HTTPClientManager()

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"Hello World"
            mock_response.request = MagicMock()
            mock_response.request.extensions = {"start_time": time.time()}
            mock_request.return_value = mock_response

            response = await client._make_request("GET", "https://example.com")

            assert response.status_code == 200
            mock_request.assert_called_once_with("GET", "https://example.com")

    @pytest.mark.asyncio
    async def test_http_methods(self):
        """Test HTTP method convenience functions."""
        client = HTTPClientManager()

        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b""
            mock_response.request = MagicMock()
            mock_response.request.extensions = {"start_time": time.time()}
            mock_request.return_value = mock_response

            # Test all HTTP methods
            await client.get("https://example.com")
            await client.post("https://example.com", json={"key": "value"})
            await client.put("https://example.com", json={"key": "value"})
            await client.patch("https://example.com", json={"key": "value"})
            await client.delete("https://example.com")
            await client.head("https://example.com")
            await client.options("https://example.com")

            assert mock_request.call_count == 7


class TestConnectionPool:
    """Test ConnectionPool class."""

    @pytest.mark.asyncio
    async def test_get_client(self):
        """Test getting client from pool."""
        pool = ConnectionPool()

        client1 = await pool.get_client("https://api1.example.com")
        client2 = await pool.get_client("https://api2.example.com")
        client1_again = await pool.get_client("https://api1.example.com")

        # Should return same client for same base URL
        assert client1 is client1_again
        # Should return different client for different base URL
        assert client1 is not client2

    @pytest.mark.asyncio
    async def test_close_all(self):
        """Test closing all clients in pool."""
        pool = ConnectionPool()

        client1 = await pool.get_client("https://api1.example.com")
        client2 = await pool.get_client("https://api2.example.com")

        with (
            patch.object(client1, "close") as mock_close1,
            patch.object(client2, "close") as mock_close2,
        ):
            await pool.close_all()
            mock_close1.assert_called_once()
            mock_close2.assert_called_once()


class TestConvenienceFunctions:
    """Test convenience functions."""

    @pytest.mark.asyncio
    async def test_http_client_context_manager(self):
        """Test http_client context manager."""
        async with http_client(base_url="https://api.example.com") as client:
            assert client.base_url == "https://api.example.com"
            assert client._client is not None

    @pytest.mark.asyncio
    async def test_make_request(self):
        """Test make_request convenience function."""
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"Hello"
            mock_response.request = MagicMock()
            mock_response.request.extensions = {"start_time": time.time()}
            mock_request.return_value = mock_response

            response = await make_request("GET", "https://example.com")
            assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_http_method_convenience_functions(self):
        """Test HTTP method convenience functions."""
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b""
            mock_response.request = MagicMock()
            mock_response.request.extensions = {"start_time": time.time()}
            mock_request.return_value = mock_response

            await get("https://example.com")
            await post("https://example.com", json={"key": "value"})
            await put("https://example.com", json={"key": "value"})
            await patch_request("https://example.com", json={"key": "value"})
            await delete("https://example.com")

            assert mock_request.call_count == 5


class TestConfigCreationFunctions:
    """Test configuration creation functions."""

    def test_create_retry_config(self):
        """Test create_retry_config function."""
        config = create_retry_config(max_attempts=5, base_delay=2.0, max_delay=120.0)
        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 120.0

    def test_create_rate_limit_config(self):
        """Test create_rate_limit_config function."""
        config = create_rate_limit_config(requests_per_second=5.0, burst_size=10)
        assert config.requests_per_second == 5.0
        assert config.burst_size == 10

    def test_create_circuit_breaker_config(self):
        """Test create_circuit_breaker_config function."""
        config = create_circuit_breaker_config(
            failure_threshold=3, recovery_timeout=30.0
        )
        assert config.failure_threshold == 3
        assert config.recovery_timeout == 30.0


class TestIntegration:
    """Integration tests for web utilities."""

    @pytest.mark.asyncio
    async def test_full_featured_client(self):
        """Test HTTP client with all features enabled."""
        retry_config = RetryConfig(max_attempts=2, base_delay=0.01)
        rate_limit_config = RateLimitConfig(requests_per_second=100.0, burst_size=10)
        circuit_config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=0.1)

        async with HTTPClientManager(
            retry_config=retry_config,
            rate_limit_config=rate_limit_config,
            circuit_breaker_config=circuit_config,
            enable_logging=True,
        ) as client:
            assert client.retry_handler is not None
            assert client.rate_limiter is not None
            assert client.circuit_breaker is not None
            assert client.logger is not None

    @pytest.mark.asyncio
    async def test_error_handling_chain(self):
        """Test error handling with retry, circuit breaker, and rate limiting."""
        retry_config = RetryConfig(max_attempts=2, base_delay=0.01)
        circuit_config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1)

        async with HTTPClientManager(
            retry_config=retry_config, circuit_breaker_config=circuit_config
        ) as client:
            with patch("httpx.AsyncClient.request") as mock_request:
                # First call fails, second succeeds
                mock_request.side_effect = [
                    httpx.TimeoutException("Timeout"),
                    MagicMock(
                        status_code=200,
                        content=b"Success",
                        request=MagicMock(extensions={"start_time": time.time()}),
                    ),
                ]

                response = await client.get("https://example.com")
                assert response.status_code == 200
                assert mock_request.call_count == 2
