"""
Base cache service that provides common functionality for both Redis and memory cache.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import Optional


class BaseCacheService(ABC):
    """
    Abstract base class for cache services.
    Provides common functionality and interface for both Redis and memory cache.
    """

    def __init__(self):
        self._lock = asyncio.Lock()

    @abstractmethod
    async def ping(self) -> bool:
        """Ping the cache service."""
        pass

    @abstractmethod
    def ping_sync(self) -> bool:
        """Ping the cache service (sync)."""
        pass

    @abstractmethod
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        pass

    @abstractmethod
    def get_sync(self, key: str) -> Optional[str]:
        """Get value from cache (sync)."""
        pass

    @abstractmethod
    async def set(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration."""
        pass

    @abstractmethod
    def set_sync(self, key: str, value: str, expire: Optional[int] = None) -> bool:
        """Set value in cache with optional expiration (sync)."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass

    @abstractmethod
    def delete_sync(self, key: str) -> bool:
        """Delete key from cache (sync)."""
        pass

    @abstractmethod
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass

    @abstractmethod
    def exists_sync(self, key: str) -> bool:
        """Check if key exists in cache (sync)."""
        pass

    @abstractmethod
    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for key."""
        pass

    @abstractmethod
    def expire_sync(self, key: str, seconds: int) -> bool:
        """Set expiration for key (sync)."""
        pass

    @abstractmethod
    async def ttl(self, key: str) -> int:
        """Get TTL for key."""
        pass

    @abstractmethod
    def ttl_sync(self, key: str) -> int:
        """Get TTL for key (sync)."""
        pass

    @abstractmethod
    async def keys(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern."""
        pass

    @abstractmethod
    def keys_sync(self, pattern: str = "*") -> list[str]:
        """Get keys matching pattern (sync)."""
        pass

    @abstractmethod
    async def info(self) -> dict:
        """Get cache service information."""
        pass

    @abstractmethod
    def info_sync(self) -> dict:
        """Get cache service information (sync)."""
        pass

    # Common utility methods
    def _is_expired(self, expires_at: Optional[float]) -> bool:
        """Check if a timestamp has expired."""
        if expires_at is None:
            return False
        return time.time() > expires_at

    def _calculate_ttl(self, expires_at: Optional[float]) -> int:
        """Calculate TTL from expiration timestamp."""
        if expires_at is None:
            return -1
        ttl = int(expires_at - time.time())
        return ttl if ttl > 0 else -2

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        keys = await self.keys(pattern)
        if not keys:
            return 0

        deleted_count = 0
        for key in keys:
            if await self.delete(key):
                deleted_count += 1

        return deleted_count

    def clear_pattern_sync(self, pattern: str) -> int:
        """Clear all keys matching pattern (sync)."""
        keys = self.keys_sync(pattern)
        if not keys:
            return 0

        deleted_count = 0
        for key in keys:
            if self.delete_sync(key):
                deleted_count += 1

        return deleted_count
