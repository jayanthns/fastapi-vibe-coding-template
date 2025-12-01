"""
Unified cache service that switches between Redis and in-memory cache
based on the USE_REDIS configuration flag.
"""

from src.core.cache.memory_cache import memory_cache_service
from src.core.cache.redis_cache import redis_cache_service
from src.core.config import settings


class UnifiedCacheService:
    """
    Unified cache service that automatically switches between Redis and memory cache
    based on the USE_REDIS configuration flag.
    """

    def __init__(self):
        self._service = None
        self._service_type = None

    def _get_service(self):
        """Get the appropriate cache service based on configuration."""
        if self._service is None or self._service_type != settings.use_redis:
            if settings.use_redis:
                self._service = redis_cache_service
                self._service_type = True
            else:
                self._service = memory_cache_service
                self._service_type = False

        return self._service

    async def ping(self) -> bool:
        """Ping the cache service."""
        return await self._get_service().ping()

    def ping_sync(self) -> bool:
        """Ping the cache service (sync)."""
        return self._get_service().ping_sync()

    async def get(self, key: str) -> str | None:
        """Get value from cache."""
        return await self._get_service().get(key)

    def get_sync(self, key: str) -> str | None:
        """Get value from cache (sync)."""
        return self._get_service().get_sync(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> bool:
        """Set value in cache with optional expiration."""
        return await self._get_service().set(key, value, expire)

    def set_sync(self, key: str, value: str, expire: int | None = None) -> bool:
        """Set value in cache with optional expiration (sync)."""
        return self._get_service().set_sync(key, value, expire)

    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        return await self._get_service().delete(key)

    def delete_sync(self, key: str) -> bool:
        """Delete key from cache (sync)."""
        return self._get_service().delete_sync(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return await self._get_service().exists(key)

    def exists_sync(self, key: str) -> bool:
        """Check if key exists in cache (sync)."""
        return self._get_service().exists_sync(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        return await self._get_service().expire(key, seconds)

    def expire_sync(self, key: str, seconds: int) -> bool:
        """Set expiration for key (sync)."""
        return self._get_service().expire_sync(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        return await self._get_service().ttl(key)

    def ttl_sync(self, key: str) -> int:
        """Get TTL for key (sync)."""
        return self._get_service().ttl_sync(key)

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        return await self._get_service().keys(pattern)

    def keys_sync(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern (sync)."""
        return self._get_service().keys_sync(pattern)

    async def info(self) -> dict:
        """Get cache service information."""
        info = await self._get_service().info()
        info["cache_type"] = "redis" if settings.use_redis else "memory"
        info["use_redis"] = settings.use_redis
        return info

    def info_sync(self) -> dict:
        """Get cache service information (sync)."""
        info = self._get_service().info_sync()
        info["cache_type"] = "redis" if settings.use_redis else "memory"
        info["use_redis"] = settings.use_redis
        return info

    async def clear(self) -> int:
        """Clear all keys from cache."""
        service = self._get_service()
        if hasattr(service, "clear"):
            return await service.clear()
        return 0

    def clear_sync(self) -> int:
        """Clear all keys from cache (sync)."""
        service = self._get_service()
        if hasattr(service, "clear_sync"):
            return service.clear_sync()
        return 0

    async def clear_pattern(self, pattern: str) -> int:
        """Clear keys matching pattern."""
        service = self._get_service()
        if hasattr(service, "clear_pattern"):
            return await service.clear_pattern(pattern)
        return 0

    def clear_pattern_sync(self, pattern: str) -> int:
        """Clear keys matching pattern (sync)."""
        service = self._get_service()
        if hasattr(service, "clear_pattern_sync"):
            return service.clear_pattern_sync(pattern)
        return 0

    @property
    def service_type(self) -> str:
        """Get the current cache service type."""
        return "redis" if settings.use_redis else "memory"

    @property
    def is_redis(self) -> bool:
        """Check if using Redis."""
        return settings.use_redis

    @property
    def is_memory(self) -> bool:
        """Check if using memory cache."""
        return not settings.use_redis


# Global unified cache service instance
unified_cache_service = UnifiedCacheService()
