"""
In-memory cache implementation as an alternative to Redis.
Provides the same interface as Redis service but uses local memory.
"""

import time
from typing import Any, Dict, Optional

from app.core.cache.base_cache import BaseCacheService


class MemoryCacheService(BaseCacheService):
    """
    In-memory cache service that provides Redis-like interface.
    Uses asyncio-safe operations and supports TTL.
    """

    def __init__(self):
        super().__init__()
        self._cache: Dict[str, Dict[str, Any]] = {}  # type: ignore

    async def ping(self) -> bool:
        """Ping the memory cache (always returns True)."""
        return True

    def ping_sync(self) -> bool:
        """Ping the memory cache (always returns True)."""
        return True

    async def get(self, key: str) -> Optional[str]:
        """Get value from memory cache."""
        async with self._lock:
            if key not in self._cache:
                return None

            item = self._cache[key]

            # Check if expired
            if self._is_expired(item.get("expires_at")):
                del self._cache[key]
                return None

            return item["value"]

    def get_sync(self, key: str) -> Optional[str]:
        """Get value from memory cache (sync)."""
        if key not in self._cache:
            return None

        item = self._cache[key]

        # Check if expired
        if self._is_expired(item.get("expires_at")):
            del self._cache[key]
            return None

        return item["value"]

    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in memory cache with optional expiration."""
        async with self._lock:
            expires_at = None
            if expire:
                expires_at = time.time() + expire

            self._cache[key] = {
                "value": value,
                "expires_at": expires_at,
                "created_at": time.time(),
            }
            return True

    def set_sync(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in memory cache with optional expiration (sync)."""
        expires_at = None
        if expire:
            expires_at = time.time() + expire

        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time(),
        }
        return True

    async def delete(self, key: str) -> bool:
        """Delete key from memory cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def delete_sync(self, key: str) -> bool:
        """Delete key from memory cache (sync)."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        async with self._lock:
            if key not in self._cache:
                return False

            item = self._cache[key]

            # Check if expired
            if self._is_expired(item.get("expires_at")):
                del self._cache[key]
                return False

            return True

    def exists_sync(self, key: str) -> bool:
        """Check if key exists in memory cache (sync)."""
        if key not in self._cache:
            return False

        item = self._cache[key]

        # Check if expired
        if self._is_expired(item.get("expires_at")):
            del self._cache[key]
            return False

        return True

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        async with self._lock:
            if key in self._cache:
                self._cache[key]["expires_at"] = time.time() + seconds
                return True
            return False

    def expire_sync(self, key: str, seconds: int) -> bool:
        """Set expiration for key (sync)."""
        if key in self._cache:
            self._cache[key]["expires_at"] = time.time() + seconds
            return True
        return False

    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        async with self._lock:
            if key not in self._cache:
                return -2

            item = self._cache[key]

            if not item.get("expires_at"):
                return -1

            ttl = self._calculate_ttl(item["expires_at"])
            if ttl == -2:
                del self._cache[key]
            return ttl

    def ttl_sync(self, key: str) -> int:
        """Get TTL for key (sync)."""
        if key not in self._cache:
            return -2

        item = self._cache[key]

        if not item.get("expires_at"):
            return -1

        ttl = self._calculate_ttl(item["expires_at"])
        if ttl == -2:
            del self._cache[key]
        return ttl

    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        async with self._lock:
            # Clean expired keys first
            await self._cleanup_expired()

            if pattern == "*":
                return list(self._cache.keys())

            # Simple pattern matching (supports * wildcard)
            import fnmatch

            return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

    def keys_sync(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern (sync)."""
        # Clean expired keys first
        self._cleanup_expired_sync()

        if pattern == "*":
            return list(self._cache.keys())

        # Simple pattern matching (supports * wildcard)
        import fnmatch

        return [key for key in self._cache.keys() if fnmatch.fnmatch(key, pattern)]

    async def info(self) -> dict:
        """Get memory cache information."""
        async with self._lock:
            await self._cleanup_expired()

            total_keys = len(self._cache)
            total_memory = sum(len(str(item)) for item in self._cache.values())

            return {
                "memory_cache": True,
                "total_keys": total_keys,
                "estimated_memory_bytes": total_memory,
                "uptime_seconds": 0,  # Memory cache doesn't track uptime
                "version": "1.0.0",
            }

    def info_sync(self) -> dict:
        """Get memory cache information (sync)."""
        self._cleanup_expired_sync()

        total_keys = len(self._cache)
        total_memory = sum(len(str(item)) for item in self._cache.values())

        return {
            "memory_cache": True,
            "total_keys": total_keys,
            "estimated_memory_bytes": total_memory,
            "uptime_seconds": 0,  # Memory cache doesn't track uptime
            "version": "1.0.0",
        }

    async def _cleanup_expired(self) -> None:
        """Remove expired keys from cache."""
        expired_keys = [
            key
            for key, item in self._cache.items()
            if self._is_expired(item.get("expires_at"))
        ]
        for key in expired_keys:
            del self._cache[key]

    def _cleanup_expired_sync(self) -> None:
        """Remove expired keys from cache (sync)."""
        expired_keys = [
            key
            for key, item in self._cache.items()
            if self._is_expired(item.get("expires_at"))
        ]
        for key in expired_keys:
            del self._cache[key]

    async def clear(self) -> int:
        """Clear all keys from cache."""
        async with self._lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def clear_sync(self) -> int:
        """Clear all keys from cache (sync)."""
        count = len(self._cache)
        self._cache.clear()
        return count

    # clear_pattern methods are inherited from BaseCacheService


# Global memory cache service instance
memory_cache_service = MemoryCacheService()
