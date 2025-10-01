"""
Redis cache service for caching and background jobs.
Provides both sync and async Redis clients as singletons.
"""

import asyncio
from typing import Optional

import redis as redis_sync
import redis.asyncio as redis
from redis import Redis

from app.core.cache.base_cache import BaseCacheService
from app.core.config import settings


class RedisCacheService(BaseCacheService):
    """
    Singleton Redis service that manages Redis connections.
    Provides both sync and async Redis clients.
    """

    _instance: Optional["RedisCacheService"] = None
    _sync_client: Optional[Redis] = None
    _async_client: Optional[redis.Redis] = None
    _lock = asyncio.Lock()

    def __new__(cls) -> "RedisCacheService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self._sync_client = None
        self._async_client = None

    @property
    def sync_client(self) -> Redis:
        """Get sync Redis client (creates if not exists)."""
        if self._sync_client is None:
            self._sync_client = redis_sync.from_url(settings.redis_url)
        return self._sync_client

    async def get_async_client(self) -> redis.Redis:
        """Get async Redis client (creates if not exists)."""
        if self._async_client is None:
            async with self._lock:
                if self._async_client is None:
                    self._async_client = redis.from_url(settings.redis_url)
        return self._async_client

    async def close_async_client(self) -> None:
        """Close async Redis client."""
        if self._async_client is not None:
            await self._async_client.close()
            self._async_client = None

    def close_sync_client(self) -> None:
        """Close sync Redis client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def ping(self) -> bool:
        """Ping Redis server using async client."""
        try:
            client = await self.get_async_client()
            return await client.ping()
        except Exception:
            return False

    def ping_sync(self) -> bool:
        """Ping Redis server using sync client."""
        try:
            return self.sync_client.ping()  # type: ignore
        except Exception:
            return False

    async def get(self, key: str) -> Optional[str]:
        """Get value from Redis."""
        client = await self.get_async_client()
        return await client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration."""
        client = await self.get_async_client()
        return await client.set(key, value, ex=expire)

    async def delete(self, key: str) -> bool:
        """Delete key from Redis."""
        client = await self.get_async_client()
        return await client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists in Redis."""
        client = await self.get_async_client()
        return await client.exists(key)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        client = await self.get_async_client()
        return await client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        client = await self.get_async_client()
        return await client.ttl(key)

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        client = await self.get_async_client()
        keys = await client.keys(pattern)
        return [key.decode("utf-8") if isinstance(key, bytes) else key for key in keys]

    async def info(self) -> dict:
        """Get Redis server information."""
        client = await self.get_async_client()
        return await client.info()

    # Sync methods for non-async contexts
    def get_sync(self, key: str) -> Optional[str]:
        """Get value from Redis (sync)."""
        return self.sync_client.get(key)  # type: ignore

    def set_sync(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in Redis with optional expiration (sync)."""
        return self.sync_client.set(key, value, ex=expire)  # type: ignore

    def delete_sync(self, key: str) -> bool:
        """Delete key from Redis (sync)."""
        return self.sync_client.delete(key)  # type: ignore

    def exists_sync(self, key: str) -> bool:
        """Check if key exists in Redis (sync)."""
        return self.sync_client.exists(key)  # type: ignore

    def expire_sync(self, key: str, seconds: int) -> bool:
        """Set expiration for key (sync)."""
        return self.sync_client.expire(key, seconds)  # type: ignore

    def ttl_sync(self, key: str) -> int:
        """Get TTL for key (sync)."""
        return self.sync_client.ttl(key)  # type: ignore

    def keys_sync(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern (sync)."""
        keys = self.sync_client.keys(pattern)
        return [key.decode("utf-8") if isinstance(key, bytes) else key for key in keys]  # type: ignore

    def info_sync(self) -> dict:
        """Get Redis server information (sync)."""
        return self.sync_client.info()  # type: ignore


# Global Redis cache service instance
redis_cache_service = RedisCacheService()


# Dependency functions for FastAPI
async def get_redis() -> RedisCacheService:
    """FastAPI dependency to get Redis cache service."""
    return redis_cache_service


def get_redis_sync() -> RedisCacheService:
    """Get Redis cache service for sync contexts."""
    return redis_cache_service
