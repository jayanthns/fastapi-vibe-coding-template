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
from .cache import CacheManager, cached, cached_sync
from .memory_cache import MemoryCacheService, memory_cache_service
from .redis_cache import RedisCacheService, redis_cache_service
from .unified_cache import UnifiedCacheService, unified_cache_service

# Main cache interface - simplified and framework-like
cache = unified_cache_service

__all__ = [
    # Main cache interface (simplified)
    "cache",
    # Base classes
    "BaseCacheService",
    # Cache implementations
    "RedisCacheService",
    "MemoryCacheService",
    "UnifiedCacheService",
    # Service instances (for advanced usage)
    "redis_cache_service",
    "memory_cache_service",
    "unified_cache_service",
    # Cache manager and utilities
    "CacheManager",
    "cached",
    "cached_sync",
]
