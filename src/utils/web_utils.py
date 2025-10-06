"""
Web & API utilities for HTTP client operations, retry mechanisms, and more.

This module provides comprehensive web utilities including:
- HTTP Client Utilities
- Retry mechanisms with exponential backoff
- Rate limiting and throttling
- Request/response logging
- Circuit breaker patterns
- HTTP client pooling
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
    """Token bucket rate limiter implementation."""

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
    """Circuit breaker implementation."""

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
    """HTTP client with advanced features."""

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
            self._client = AsyncClient(
                base_url=self.base_url, timeout=timeout, **self.client_kwargs
            )

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

                self._pools[base_url] = HTTPClientManager(
                    base_url=base_url, limits=limits, **client_kwargs
                )

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
