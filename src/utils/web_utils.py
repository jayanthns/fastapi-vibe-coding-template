"""
Web & API Utilities Module

This module provides comprehensive web and API utilities for FastAPI applications,
including advanced HTTP client operations, retry mechanisms, rate limiting, and
circuit breaker patterns for robust API interactions.

Key Features:
- HTTP Client with advanced configuration and connection pooling
- Retry mechanisms with exponential backoff and jitter
- Rate limiting with token bucket algorithm
- Circuit breaker pattern for fault tolerance
- Request/response logging and monitoring
- Connection pooling for efficient resource usage
- Async/await support for modern Python applications

Classes:
    RetryConfig: Configuration for retry mechanisms
    RateLimitConfig: Configuration for rate limiting
    CircuitBreakerConfig: Configuration for circuit breaker
    RateLimiter: Token bucket rate limiter implementation
    CircuitBreaker: Circuit breaker pattern implementation
    RetryHandler: Retry mechanism with exponential backoff
    RequestLogger: Request/response logging utilities
    HTTPClientManager: Advanced HTTP client with all features
    ConnectionPool: HTTP client connection pooling

Example:
    ```python
    from src.utils.web_utils import HTTPClientManager, RetryConfig

    # Create HTTP client with retry and rate limiting
    retry_config = RetryConfig(max_attempts=3, backoff_factor=2.0)
    client = HTTPClientManager(
        base_url="https://api.example.com",
        retry_config=retry_config,
        enable_logging=True
    )

    # Make requests with automatic retry and rate limiting
    async with client as http_client:
        response = await http_client.get("/users")
        data = response.json()
    ```

Advanced Features:
    - Automatic retry on transient failures
    - Rate limiting to respect API quotas
    - Circuit breaker to prevent cascade failures
    - Connection pooling for performance
    - Comprehensive logging and monitoring
    - Async context manager support

Security Note:
    This module provides robust HTTP client functionality. Always validate
    and sanitize data from external APIs and implement proper authentication.
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncGenerator, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from httpx import AsyncClient, Response, Timeout

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, requests fail fast
    HALF_OPEN = "half_open"  # Testing if service is back


@dataclass
class RetryConfig:
    """Configuration for retry mechanisms."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retryable_status_codes: List[int] = field(
        default_factory=lambda: [429, 500, 502, 503, 504]
    )
    retryable_exceptions: List[type] = field(
        default_factory=lambda: [
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.NetworkError,
        ]
    )


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""

    requests_per_second: float = 10.0
    burst_size: int = 20
    window_size: float = 60.0  # seconds


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = httpx.HTTPStatusError
    success_threshold: int = 3  # For half-open state


@dataclass
class RequestLog:
    """Request/response logging data."""

    method: str
    url: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    request_size: Optional[int] = None
    response_size: Optional[int] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class RateLimiter:
    """
    Token bucket rate limiter implementation for API rate limiting.

    This class implements a token bucket algorithm for rate limiting HTTP requests,
    allowing burst traffic while maintaining average rate limits.

    Features:
        - Token bucket algorithm with configurable rate and burst size
        - Thread-safe async operations
        - Automatic token refill based on time elapsed
        - Burst allowance for handling traffic spikes

    Methods:
        acquire: Acquire a token (returns True if successful)
        wait_for_token: Wait until a token is available
        _refill_tokens: Internal method to refill tokens based on time

    Example:
        ```python
        from src.utils.web_utils import RateLimiter, RateLimitConfig

        # Create rate limiter: 10 requests per second, burst of 20
        config = RateLimitConfig(rate=10, burst_size=20)
        limiter = RateLimiter(config)

        # Check if request is allowed
        if await limiter.acquire():
            # Make API request
            response = await make_api_request()
        else:
            # Rate limit exceeded
            print("Rate limit exceeded")

        # Wait for token to become available
        await limiter.wait_for_token()
        response = await make_api_request()
        ```

    Algorithm:
        The token bucket algorithm works by:
        1. Tokens are added to the bucket at a constant rate
        2. Each request consumes one token
        3. If tokens are available, request is allowed
        4. If no tokens available, request is rate limited
        5. Burst size determines maximum tokens that can accumulate
    """

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.tokens = float(config.burst_size)
        self.last_update = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self) -> bool:
        """Acquire a token from the rate limiter."""
        async with self._lock:
            now = time.time()
            time_passed = now - self.last_update

            # Add tokens based on time passed
            self.tokens = min(
                self.config.burst_size,
                self.tokens + time_passed * self.config.requests_per_second,
            )
            self.last_update = now

            if self.tokens >= 1:
                self.tokens -= 1
                return True

            return False

    async def wait_for_token(self) -> None:
        """Wait until a token is available."""
        while not await self.acquire():
            await asyncio.sleep(0.1)


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance and system protection.

    This class implements the circuit breaker pattern to prevent cascade failures
    by monitoring request success/failure rates and temporarily stopping requests
    when failure thresholds are exceeded.

    States:
        - CLOSED: Normal operation, requests are allowed
        - OPEN: Circuit is open, requests are blocked
        - HALF_OPEN: Testing state, limited requests allowed

    Features:
        - Configurable failure threshold and timeout
        - Automatic state transitions
        - Success counting for recovery
        - Thread-safe async operations
        - Fast-fail when circuit is open

    Methods:
        call: Execute function with circuit breaker protection
        _should_attempt_reset: Check if circuit should transition to half-open
        _on_success: Handle successful request
        _on_failure: Handle failed request

    Example:
        ```python
        from src.utils.web_utils import CircuitBreaker, CircuitBreakerConfig

        # Create circuit breaker: open after 5 failures, timeout 60s
        config = CircuitBreakerConfig(
            failure_threshold=5,
            timeout=60.0,
            success_threshold=3
        )
        breaker = CircuitBreaker(config)

        # Use circuit breaker to protect API calls
        try:
            result = await breaker.call(make_api_request)
            print(f"Success: {result}")
        except CircuitBreakerOpenError:
            print("Circuit breaker is open, request blocked")
        except Exception as e:
            print(f"Request failed: {e}")
        ```

    Pattern:
        The circuit breaker pattern works by:
        1. Monitor request success/failure rates
        2. Open circuit when failure threshold exceeded
        3. Block requests when circuit is open
        4. Allow test requests when timeout expires (half-open)
        5. Close circuit when success threshold reached
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self._lock = asyncio.Lock()

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if time.time() - self.last_failure_time > self.config.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                else:
                    raise httpx.HTTPStatusError(
                        "Circuit breaker is OPEN", request=None, response=None
                    )

        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.config.expected_exception as e:
            await self._on_failure()
            raise e

    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
            else:
                self.failure_count = 0

    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN


class RetryHandler:
    """Retry mechanism with exponential backoff."""

    def __init__(self, config: RetryConfig):
        self.config = config

    async def execute_with_retry(self, func, *args, **kwargs):
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(self.config.max_attempts):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e

                # Check if we should retry
                if not self._should_retry(e, attempt):
                    raise e

                # Calculate delay
                delay = self._calculate_delay(attempt)

                if attempt < self.config.max_attempts - 1:
                    logger.warning(
                        f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s"
                    )
                    await asyncio.sleep(delay)

        raise last_exception

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry based on exception and attempt count."""
        if attempt >= self.config.max_attempts - 1:
            return False

        # Check if exception is retryable
        if isinstance(exception, httpx.HTTPStatusError):
            return exception.response.status_code in self.config.retryable_status_codes

        return any(
            isinstance(exception, exc_type)
            for exc_type in self.config.retryable_exceptions
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter."""
        delay = min(
            self.config.base_delay * (self.config.exponential_base**attempt),
            self.config.max_delay,
        )

        if self.config.jitter:
            # Add random jitter (±25%)
            import random

            jitter = delay * 0.25 * (2 * random.random() - 1)
            delay += jitter

        return delay


class RequestLogger:
    """Request/response logging utility."""

    def __init__(self, log_requests: bool = True, log_responses: bool = True):
        self.log_requests = log_requests
        self.log_responses = log_responses
        self.logs: List[RequestLog] = []
        self._lock = asyncio.Lock()

    async def log_request(
        self, method: str, url: str, request_size: Optional[int] = None
    ):
        """Log outgoing request."""
        if not self.log_requests:
            return

        log = RequestLog(method=method, url=url, request_size=request_size)

        async with self._lock:
            self.logs.append(log)

    async def log_response(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        response_size: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Log response details."""
        if not self.log_responses:
            return

        log = RequestLog(
            method=method,
            url=url,
            status_code=status_code,
            response_time=response_time,
            response_size=response_size,
            error=error,
        )

        async with self._lock:
            self.logs.append(log)

    async def get_logs(self, limit: Optional[int] = None) -> List[RequestLog]:
        """Get recent logs."""
        async with self._lock:
            logs = self.logs[-limit:] if limit else self.logs
            return logs.copy()

    async def clear_logs(self):
        """Clear all logs."""
        async with self._lock:
            self.logs.clear()


class HTTPClientManager:
    """
    Advanced HTTP client with retry mechanisms, rate limiting, and circuit breaker.

    This class provides a comprehensive HTTP client with built-in resilience patterns
    including automatic retries, rate limiting, circuit breaker, and request logging.

    Features:
        - Automatic retry with exponential backoff
        - Rate limiting with token bucket algorithm
        - Circuit breaker for fault tolerance
        - Request/response logging
        - Connection pooling
        - Async context manager support
        - Configurable timeouts and limits

    Methods:
        get: Make GET request
        post: Make POST request
        put: Make PUT request
        patch: Make PATCH request
        delete: Make DELETE request
        request: Make custom HTTP request
        close: Close the HTTP client

    Example:
        ```python
        from src.utils.web_utils import HTTPClientManager, RetryConfig

        # Create client with retry configuration
        retry_config = RetryConfig(max_attempts=3, backoff_factor=2.0)
        client = HTTPClientManager(
            base_url="https://api.example.com",
            retry_config=retry_config,
            enable_logging=True
        )

        # Use as async context manager
        async with client as http_client:
            # Make requests with automatic retry and rate limiting
            response = await http_client.get("/users")
            users = response.json()

            # POST request with data
            new_user = await http_client.post("/users", json={"name": "John"})
        ```

    Configuration:
        - base_url: Base URL for all requests
        - timeout: Request timeout in seconds
        - retry_config: Retry mechanism configuration
        - rate_limit_config: Rate limiting configuration
        - circuit_breaker_config: Circuit breaker configuration
        - enable_logging: Enable request/response logging
        - **client_kwargs: Additional httpx.AsyncClient parameters
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
        retry_config: Optional[RetryConfig] = None,
        rate_limit_config: Optional[RateLimitConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        enable_logging: bool = True,
        **client_kwargs,
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.retry_handler = RetryHandler(retry_config or RetryConfig())
        self.rate_limiter = (
            RateLimiter(rate_limit_config or RateLimitConfig())
            if rate_limit_config
            else None
        )
        self.circuit_breaker = (
            CircuitBreaker(circuit_breaker_config or CircuitBreakerConfig())
            if circuit_breaker_config
            else None
        )
        self.logger = RequestLogger(enable_logging, enable_logging)
        self.client_kwargs = client_kwargs
        self._client: Optional[AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            timeout = Timeout(self.timeout)
            client_kwargs = self.client_kwargs.copy()
            if self.base_url is not None:
                client_kwargs["base_url"] = self.base_url
            self._client = AsyncClient(timeout=timeout, **client_kwargs)

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _make_request(self, method: str, url: str, **kwargs) -> Response:
        """Make HTTP request with all features enabled."""
        await self._ensure_client()

        # Apply rate limiting
        if self.rate_limiter:
            await self.rate_limiter.wait_for_token()

        # Prepare request
        full_url = urljoin(self.base_url or "", url) if self.base_url else url

        # Log request
        request_size = None
        if "content" in kwargs:
            content = kwargs["content"]
            if isinstance(content, (str, bytes)):
                request_size = len(content)

        await self.logger.log_request(method, full_url, request_size)

        # Define the actual request function
        async def _request():
            return await self._client.request(method, url, **kwargs)

        # Apply circuit breaker if enabled
        if self.circuit_breaker:
            response = await self.circuit_breaker.call(_request)
        else:
            response = await _request()

        # Log response
        response_time = time.time() - response.request.extensions.get(
            "start_time", time.time()
        )
        response_size = len(response.content) if response.content else None

        await self.logger.log_response(
            method, full_url, response.status_code, response_time, response_size
        )

        return response

    async def request(
        self, method: str, url: str, retry: bool = True, **kwargs
    ) -> Response:
        """Make HTTP request with optional retry."""
        if retry:
            return await self.retry_handler.execute_with_retry(
                self._make_request, method, url, **kwargs
            )
        else:
            return await self._make_request(method, url, **kwargs)

    async def get(self, url: str, **kwargs) -> Response:
        """Make GET request."""
        return await self.request("GET", url, **kwargs)

    async def post(self, url: str, **kwargs) -> Response:
        """Make POST request."""
        return await self.request("POST", url, **kwargs)

    async def put(self, url: str, **kwargs) -> Response:
        """Make PUT request."""
        return await self.request("PUT", url, **kwargs)

    async def patch(self, url: str, **kwargs) -> Response:
        """Make PATCH request."""
        return await self.request("PATCH", url, **kwargs)

    async def delete(self, url: str, **kwargs) -> Response:
        """Make DELETE request."""
        return await self.request("DELETE", url, **kwargs)

    async def head(self, url: str, **kwargs) -> Response:
        """Make HEAD request."""
        return await self.request("HEAD", url, **kwargs)

    async def options(self, url: str, **kwargs) -> Response:
        """Make OPTIONS request."""
        return await self.request("OPTIONS", url, **kwargs)


class ConnectionPool:
    """HTTP connection pool manager."""

    def __init__(
        self,
        max_connections: int = 100,
        max_keepalive_connections: int = 20,
        keepalive_expiry: float = 30.0,
    ):
        self.max_connections = max_connections
        self.max_keepalive_connections = max_keepalive_connections
        self.keepalive_expiry = keepalive_expiry
        self._pools: Dict[str, HTTPClientManager] = {}
        self._lock = asyncio.Lock()

    async def get_client(self, base_url: str, **client_kwargs) -> HTTPClientManager:
        """Get or create HTTP client for base URL."""
        async with self._lock:
            if base_url not in self._pools:
                # Configure connection limits
                limits = httpx.Limits(
                    max_connections=self.max_connections,
                    max_keepalive_connections=self.max_keepalive_connections,
                    keepalive_expiry=self.keepalive_expiry,
                )

                client = HTTPClientManager(
                    base_url=base_url, limits=limits, **client_kwargs
                )
                await client._ensure_client()
                self._pools[base_url] = client

            return self._pools[base_url]

    async def close_all(self):
        """Close all connection pools."""
        async with self._lock:
            for client in self._pools.values():
                await client.close()
            self._pools.clear()


# Global connection pool instance
_global_pool = ConnectionPool()


@asynccontextmanager
async def http_client(
    base_url: Optional[str] = None,
    timeout: float = 30.0,
    retry_config: Optional[RetryConfig] = None,
    rate_limit_config: Optional[RateLimitConfig] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    enable_logging: bool = True,
    use_pool: bool = True,
    **client_kwargs,
) -> AsyncGenerator[HTTPClientManager, None]:
    """Context manager for HTTP client with advanced features."""
    if use_pool and base_url:
        client = await _global_pool.get_client(
            base_url,
            timeout=timeout,
            retry_config=retry_config,
            rate_limit_config=rate_limit_config,
            circuit_breaker_config=circuit_breaker_config,
            enable_logging=enable_logging,
            **client_kwargs,
        )
    else:
        client = HTTPClientManager(
            base_url=base_url,
            timeout=timeout,
            retry_config=retry_config,
            rate_limit_config=rate_limit_config,
            circuit_breaker_config=circuit_breaker_config,
            enable_logging=enable_logging,
            **client_kwargs,
        )
        await client._ensure_client()

    try:
        yield client
    finally:
        if not use_pool or not base_url:
            await client.close()


# Convenience functions
async def make_request(
    method: str,
    url: str,
    base_url: Optional[str] = None,
    timeout: float = 30.0,
    retry: bool = True,
    **kwargs,
) -> Response:
    """Convenience function for making HTTP requests."""
    async with http_client(base_url=base_url, timeout=timeout) as client:
        return await client.request(method, url, retry=retry, **kwargs)


async def get(url: str, **kwargs) -> Response:
    """Convenience function for GET requests."""
    return await make_request("GET", url, **kwargs)


async def post(url: str, **kwargs) -> Response:
    """Convenience function for POST requests."""
    return await make_request("POST", url, **kwargs)


async def put(url: str, **kwargs) -> Response:
    """Convenience function for PUT requests."""
    return await make_request("PUT", url, **kwargs)


async def patch(url: str, **kwargs) -> Response:
    """Convenience function for PATCH requests."""
    return await make_request("PATCH", url, **kwargs)


async def delete(url: str, **kwargs) -> Response:
    """Convenience function for DELETE requests."""
    return await make_request("DELETE", url, **kwargs)


def create_retry_config(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
) -> RetryConfig:
    """Create a retry configuration."""
    return RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
    )


def create_rate_limit_config(
    requests_per_second: float = 10.0, burst_size: int = 20
) -> RateLimitConfig:
    """Create a rate limit configuration."""
    return RateLimitConfig(
        requests_per_second=requests_per_second, burst_size=burst_size
    )


def create_circuit_breaker_config(
    failure_threshold: int = 5, recovery_timeout: float = 60.0
) -> CircuitBreakerConfig:
    """Create a circuit breaker configuration."""
    return CircuitBreakerConfig(
        failure_threshold=failure_threshold, recovery_timeout=recovery_timeout
    )
