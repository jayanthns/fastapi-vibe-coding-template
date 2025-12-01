"""
Caching utilities and decorators for Redis.
Provides easy-to-use caching functions throughout the application.
"""

import json
import pickle
from collections.abc import Callable
from functools import wraps
from typing import Any

from src.core.cache.unified_cache import unified_cache_service


class CacheManager:
    """Redis-based cache manager with serialization support."""

    @staticmethod
    async def get(key: str, default: Any = None) -> Any:
        """Get value from cache with automatic deserialization."""
        try:
            value = await unified_cache_service.get(key)
            if value is None:
                return default

            # Try to deserialize as JSON first, then pickle
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                try:
                    return pickle.loads(value.encode("latin1"))
                except (pickle.PickleError, UnicodeDecodeError):
                    return value
        except Exception:
            return default

    @staticmethod
    async def set(key: str, value: Any, expire: int | None = None, serialize: str = "json") -> bool:
        """Set value in cache with automatic serialization."""
        try:
            if serialize == "json":
                serialized_value = json.dumps(value, default=str)
            elif serialize == "pickle":
                serialized_value = pickle.dumps(value).decode("latin1")
            else:
                serialized_value = str(value)

            return await unified_cache_service.set(key, serialized_value, expire)
        except Exception:
            return False

    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache."""
        return await unified_cache_service.delete(key)

    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in cache."""
        return await unified_cache_service.exists(key)

    @staticmethod
    async def expire(key: str, seconds: int) -> bool:
        """Set expiration for key."""
        return await unified_cache_service.expire(key, seconds)

    @staticmethod
    async def ttl(key: str) -> int:
        """Get TTL for key."""
        return await unified_cache_service.ttl(key)

    @staticmethod
    async def clear_pattern(pattern: str) -> int:
        """Clear all keys matching pattern."""
        keys = await unified_cache_service.keys(pattern)
        if not keys:
            return 0

        deleted_count = 0
        for key in keys:
            if await unified_cache_service.delete(key):
                deleted_count += 1

        return deleted_count


# Global cache manager instance
cache = CacheManager()


def cache_key(prefix: str, *args, **kwargs) -> str:
    """Generate cache key from prefix and arguments."""
    key_parts = [prefix]

    # Add positional arguments
    for arg in args:
        if hasattr(arg, "id"):
            key_parts.append(f"id:{arg.id}")
        else:
            key_parts.append(str(arg))

    # Add keyword arguments
    for k, v in sorted(kwargs.items()):
        if hasattr(v, "id"):
            key_parts.append(f"{k}:{v.id}")
        else:
            key_parts.append(f"{k}:{v}")

    return ":".join(key_parts)


def cached(key_prefix: str, expire: int | None = None, serialize: str = "json"):
    """
    Decorator to cache function results in Redis.

    Args:
        key_prefix: Prefix for cache key
        expire: Expiration time in seconds
        serialize: Serialization method ("json" or "pickle")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache
            cached_result = await cache.get(key)
            if cached_result is not None:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache.set(key, result, expire, serialize)

            return result

        return wrapper

    return decorator


def cached_sync(key_prefix: str, expire: int | None = None, serialize: str = "json"):
    """
    Decorator to cache sync function results in Redis.

    Args:
        key_prefix: Prefix for cache key
        expire: Expiration time in seconds
        serialize: Serialization method ("json" or "pickle")
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key = cache_key(key_prefix, *args, **kwargs)

            # Try to get from cache (sync)
            try:
                cached_result = unified_cache_service.get_sync(key)
                if cached_result is not None:
                    if serialize == "json":
                        return json.loads(cached_result)
                    elif serialize == "pickle":
                        return pickle.loads(cached_result.encode("latin1"))
                    else:
                        return cached_result
            except Exception:
                pass

            # Execute function and cache result
            result = func(*args, **kwargs)

            try:
                if serialize == "json":
                    serialized_value = json.dumps(result, default=str)
                elif serialize == "pickle":
                    serialized_value = pickle.dumps(result).decode("latin1")
                else:
                    serialized_value = str(result)

                unified_cache_service.set_sync(key, serialized_value, expire)
            except Exception:
                pass

            return result

        return wrapper

    return decorator


# Common cache key generators
def user_cache_key(user_id: int) -> str:
    """Generate cache key for user data."""
    return f"user:{user_id}"


def article_cache_key(article_id: int) -> str:
    """Generate cache key for article data."""
    return f"article:{article_id}"


def articles_list_cache_key(skip: int = 0, limit: int = 100) -> str:
    """Generate cache key for articles list."""
    return f"articles:list:skip:{skip}:limit:{limit}"


def background_job_cache_key(job_id: str) -> str:
    """Generate cache key for background job."""
    return f"job:{job_id}"


# Cache invalidation helpers
async def invalidate_user_cache(user_id: int) -> None:
    """Invalidate all user-related cache."""
    await cache.clear_pattern(f"user:{user_id}*")


async def invalidate_article_cache(article_id: int) -> None:
    """Invalidate all article-related cache."""
    await cache.clear_pattern(f"article:{article_id}*")
    await cache.clear_pattern("articles:list:*")


async def invalidate_articles_cache() -> None:
    """Invalidate all articles list cache."""
    await cache.clear_pattern("articles:list:*")


async def invalidate_job_cache(job_id: str) -> None:
    """Invalidate job-related cache."""
    await cache.clear_pattern(f"job:{job_id}*")
