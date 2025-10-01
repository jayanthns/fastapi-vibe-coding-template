"""
Fallback Cache Service

Implements industry standard cache fallback pattern:
- Primary: Redis cache (shared, persistent)
- Fallback: Memory cache (local, fast)
- Automatic switching based on Redis availability
- Health check monitoring for Redis recovery
"""

import time
from typing import Any, Dict, List, Optional

from app.core.cache.base_cache import BaseCacheService
from app.core.cache.memory_cache import memory_cache_service
from app.core.cache.redis_cache import redis_cache_service
from app.core.config import settings
from app.core.logging import get_logger_for_trace_id


class FallbackCacheService(BaseCacheService):
    """
    Fallback cache service that automatically switches between Redis and memory cache.

    Industry standard pattern:
    1. Try Redis first (primary)
    2. Fall back to memory cache if Redis fails
    3. Monitor Redis health and switch back when available
    4. Log all fallback events for operational visibility
    """

    def __init__(self):
        self.primary_cache = redis_cache_service
        self.fallback_cache = memory_cache_service
        self.use_fallback = False
        self.last_redis_check = 0
        self.redis_check_interval = 30  # Check Redis every 30 seconds
        self.logger = get_logger_for_trace_id("fallback-cache")

        # Track fallback events for monitoring
        self.fallback_events = {
            "switched_to_fallback": 0,
            "switched_to_primary": 0,
            "redis_failures": 0,
        }

    def _should_check_redis(self) -> bool:
        """Check if we should test Redis connectivity."""
        return (
            time.time() - self.last_redis_check > self.redis_check_interval
            or self.use_fallback
        )

    async def _check_redis_health(self) -> bool:
        """Check if Redis is available and switch back if possible."""
        if not settings.use_redis:
            return False

        try:
            is_healthy = await self.primary_cache.ping()
            self.last_redis_check = time.time()

            if is_healthy and self.use_fallback:
                # Redis is back online, switch back to primary
                self.use_fallback = False
                self.fallback_events["switched_to_primary"] += 1
                self.logger.info(
                    "Redis recovered, switched back to primary cache",
                    extra={
                        "fallback_events": self.fallback_events,
                        "cache_type": "redis",
                    },
                )
            elif not is_healthy and not self.use_fallback:
                # Redis just failed, switch to fallback
                self.use_fallback = True
                self.fallback_events["switched_to_fallback"] += 1
                self.fallback_events["redis_failures"] += 1
                self.logger.warning(
                    "Redis unavailable, switched to memory cache fallback",
                    extra={
                        "fallback_events": self.fallback_events,
                        "cache_type": "memory",
                    },
                )

            return is_healthy

        except Exception as e:
            self.fallback_events["redis_failures"] += 1
            self.logger.error(
                f"Redis health check failed: {e}",
                extra={
                    "fallback_events": self.fallback_events,
                    "error": str(e),
                },
            )
            return False

    def _get_active_cache(self) -> BaseCacheService:
        """Get the currently active cache service."""
        if settings.use_redis and not self.use_fallback:
            return self.primary_cache
        else:
            return self.fallback_cache

    async def _execute_with_fallback(
        self, operation_name: str, operation_func, *args, **kwargs
    ):
        """Execute cache operation with automatic fallback."""
        # Check Redis health if needed
        if self._should_check_redis():
            await self._check_redis_health()

        # Get active cache service
        cache = self._get_active_cache()

        try:
            # Try the operation
            result = await operation_func(cache, *args, **kwargs)

            # If we're using fallback and Redis is back, log the operation
            if self.use_fallback and settings.use_redis:
                self.logger.debug(
                    f"Cache operation '{operation_name}' executed on fallback cache",
                    extra={
                        "operation": operation_name,
                        "cache_type": "memory",
                        "fallback_active": True,
                    },
                )

            return result

        except Exception as e:
            # If primary cache fails and we're not already using fallback, switch
            if not self.use_fallback and settings.use_redis:
                self.use_fallback = True
                self.fallback_events["switched_to_fallback"] += 1
                self.fallback_events["redis_failures"] += 1

                self.logger.warning(
                    f"Primary cache failed during '{operation_name}', switched to fallback",
                    extra={
                        "operation": operation_name,
                        "fallback_events": self.fallback_events,
                        "error": str(e),
                    },
                )

                # Retry with fallback cache
                try:
                    return await operation_func(self.fallback_cache, *args, **kwargs)
                except Exception as fallback_error:
                    self.logger.error(
                        f"Both primary and fallback cache failed for '{operation_name}'",
                        extra={
                            "operation": operation_name,
                            "primary_error": str(e),
                            "fallback_error": str(fallback_error),
                        },
                    )
                    raise fallback_error
            else:
                # Already using fallback or Redis disabled, just raise the error
                raise e

    # Async methods
    async def ping(self) -> bool:
        """Ping the active cache service."""
        return await self._execute_with_fallback("ping", lambda cache: cache.ping())

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self._execute_with_fallback(
            "get", lambda cache, k: cache.get(k), key
        )

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in cache."""
        return await self._execute_with_fallback(
            "set", lambda cache, k, v, e: cache.set(k, v, e), key, value, expire
        )

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return await self._execute_with_fallback(
            "delete", lambda cache, k: cache.delete(k), key
        )

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self._execute_with_fallback(
            "exists", lambda cache, k: cache.exists(k), key
        )

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        return await self._execute_with_fallback(
            "expire", lambda cache, k, s: cache.expire(k, s), key, seconds
        )

    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        return await self._execute_with_fallback(
            "ttl", lambda cache, k: cache.ttl(k), key
        )

    async def keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        return await self._execute_with_fallback(
            "keys", lambda cache, p: cache.keys(p), pattern
        )

    # Sync methods
    def ping_sync(self) -> bool:
        """Ping the active cache service (sync)."""
        cache = self._get_active_cache()
        return cache.ping_sync()

    def get_sync(self, key: str) -> Optional[str]:
        """Get value from cache (sync)."""
        cache = self._get_active_cache()
        return cache.get_sync(key)

    def set_sync(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in cache (sync)."""
        cache = self._get_active_cache()
        return cache.set_sync(key, value, expire)

    def delete_sync(self, key: str) -> bool:
        """Delete key from cache (sync)."""
        cache = self._get_active_cache()
        return cache.delete_sync(key)

    def exists_sync(self, key: str) -> bool:
        """Check if key exists in cache (sync)."""
        cache = self._get_active_cache()
        return cache.exists_sync(key)

    def expire_sync(self, key: str, seconds: int) -> bool:
        """Set expiration for key (sync)."""
        cache = self._get_active_cache()
        return cache.expire_sync(key, seconds)

    def ttl_sync(self, key: str) -> int:
        """Get TTL for key (sync)."""
        cache = self._get_active_cache()
        return cache.ttl_sync(key)

    def keys_sync(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern (sync)."""
        cache = self._get_active_cache()
        return cache.keys_sync(pattern)

    # Properties
    @property
    def service_type(self) -> str:
        """Get the service type of the active cache."""
        if settings.use_redis and not self.use_fallback:
            return "redis"
        else:
            return "memory"

    @property
    def is_redis(self) -> bool:
        """Check if currently using Redis."""
        return settings.use_redis and not self.use_fallback

    @property
    def is_fallback_active(self) -> bool:
        """Check if fallback cache is currently active."""
        return self.use_fallback

    @property
    def fallback_stats(self) -> Dict[str, Any]:
        """Get fallback statistics for monitoring."""
        return {
            "fallback_active": self.use_fallback,
            "primary_cache_type": "redis" if settings.use_redis else "memory",
            "active_cache_type": self.service_type,
            "events": self.fallback_events.copy(),
            "last_redis_check": self.last_redis_check,
        }

    async def info(self) -> Dict[str, Any]:
        """Get cache service information."""
        cache = self._get_active_cache()
        info = await cache.info()

        # Add fallback-specific information
        info.update(
            {
                "fallback_active": self.use_fallback,
                "primary_cache_type": "redis" if settings.use_redis else "memory",
                "fallback_stats": self.fallback_stats,
            }
        )

        return info

    def info_sync(self) -> Dict[str, Any]:
        """Get cache service information (sync)."""
        cache = self._get_active_cache()
        info = cache.info_sync()

        # Add fallback-specific information
        info.update(
            {
                "fallback_active": self.use_fallback,
                "primary_cache_type": "redis" if settings.use_redis else "memory",
                "fallback_stats": self.fallback_stats,
            }
        )

        return info

    async def close_async_client(self):
        """Close async client connections."""
        if settings.use_redis:
            await self.primary_cache.close_async_client()
        # Memory cache doesn't need cleanup


# Create the fallback cache service instance
fallback_cache_service = FallbackCacheService()
