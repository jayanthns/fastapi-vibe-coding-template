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

from src.core.cache.base_cache import BaseCacheService
from src.core.cache.cache import CacheManager, cached, cached_sync
from src.core.cache.fallback_cache import FallbackCacheService, fallback_cache_service
from src.core.cache.memory_cache import MemoryCacheService, memory_cache_service
from src.core.cache.redis_cache import RedisCacheService, redis_cache_service
from src.core.cache.unified_cache import UnifiedCacheService, unified_cache_service

# Main cache interface - industry standard fallback pattern
cache = fallback_cache_service

__all__ = [
    # Main cache interface (industry standard fallback)
    "cache",
    # Base classes
    "BaseCacheService",
    # Cache implementations
    "RedisCacheService",
    "MemoryCacheService",
    "UnifiedCacheService",
    "FallbackCacheService",
    # Service instances (for advanced usage)
    "redis_cache_service",
    "memory_cache_service",
    "unified_cache_service",
    "fallback_cache_service",
    # Cache manager and utilities
    "CacheManager",
    "cached",
    "cached_sync",
]
