"""
Cache module for the FastAPI application.

This module provides a unified caching interface that can switch between
Redis and in-memory cache based on configuration.

Main Components:
- BaseCacheService: Abstract base class for all cache implementations
- RedisCacheService: Redis-based cache implementation
- MemoryCacheService: In-memory cache implementation
- UnifiedCacheService: Switches between Redis and memory cache
- CacheManager: High-level cache operations with serialization
- cache: Global cache manager instance
"""

from .base_cache import BaseCacheService
from .cache import CacheManager, cache, cached, cached_sync
from .memory_cache import MemoryCacheService, memory_cache_service
from .redis_cache import RedisCacheService, redis_cache_service
from .unified_cache import UnifiedCacheService, unified_cache_service

__all__ = [
    # Base classes
    "BaseCacheService",
    # Cache implementations
    "RedisCacheService",
    "MemoryCacheService",
    "UnifiedCacheService",
    # Service instances
    "redis_cache_service",
    "memory_cache_service",
    "unified_cache_service",
    # Cache manager and utilities
    "CacheManager",
    "cache",
    "cached",
    "cached_sync",
]
