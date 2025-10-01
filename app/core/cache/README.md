# Cache Module

This module provides a unified caching system for the FastAPI application, following Single Responsibility Principle (SRP) and Object-Oriented Programming concepts.

## 📁 Structure

```
app/core/cache/
├── __init__.py              # Module exports and public API
├── base_cache.py            # Abstract base class for all cache implementations
├── redis_cache.py           # Redis-based cache implementation
├── memory_cache.py          # In-memory cache implementation
├── unified_cache.py         # Unified service that switches between cache types
├── cache.py                 # High-level cache manager with serialization
└── README.md               # This file
```

## 🏗️ Architecture

### Base Class (`base_cache.py`)
- **`BaseCacheService`**: Abstract base class defining the cache interface
- Common utility methods: `_is_expired()`, `_calculate_ttl()`, `clear_pattern()`
- Ensures consistent interface across all cache implementations

### Cache Implementations
- **`RedisCacheService`**: Redis-based caching with connection pooling
- **`MemoryCacheService`**: In-memory caching with TTL support
- Both inherit from `BaseCacheService` for consistent interface

### Unified Service (`unified_cache.py`)
- **`UnifiedCacheService`**: Automatically switches between Redis and memory cache
- Configuration-driven: `USE_REDIS=1` for Redis, `USE_REDIS=0` for memory
- Singleton pattern for efficient resource management

### Cache Manager (`cache.py`)
- **`CacheManager`**: High-level cache operations with automatic serialization
- **`cached`**: Decorator for function result caching
- **`cached_sync`**: Decorator for sync function result caching
- **`cache`**: Global cache manager instance

## 🚀 Usage

### Basic Usage
```python
from app.core.cache import unified_cache_service, cache

# Direct cache operations
await unified_cache_service.set("key", "value", expire=300)
value = await unified_cache_service.get("key")

# High-level cache manager
await cache.set("user:123", {"name": "John"}, expire=600)
user_data = await cache.get("user:123")
```

### Function Caching
```python
from app.core.cache import cached

@cached("expensive_calculation", expire=300)
async def expensive_calculation(n: int) -> int:
    return n * n * n
```

### Cache Type Detection
```python
from app.core.cache import unified_cache_service

if unified_cache_service.is_redis:
    print("Using Redis cache")
else:
    print("Using memory cache")
```

## ⚙️ Configuration

```bash
# .env
USE_REDIS=0  # Use memory cache
USE_REDIS=1  # Use Redis cache

# Redis configuration (only used when USE_REDIS=1)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis
```

## 🎯 Benefits

1. **Single Responsibility**: Each file has a clear, focused purpose
2. **Open/Closed Principle**: Easy to add new cache types by extending `BaseCacheService`
3. **Dependency Inversion**: High-level modules depend on abstractions, not concretions
4. **Interface Segregation**: Clean, focused interfaces for different cache operations
5. **Maintainability**: Changes to common functionality in one place (base class)
6. **Testability**: Each component can be tested independently
7. **Flexibility**: Easy to switch between cache types via configuration

## 🔧 Adding New Cache Types

To add a new cache type (e.g., Memcached):

1. Create `memcached_cache.py` in this directory
2. Inherit from `BaseCacheService`
3. Implement all abstract methods
4. Add to `unified_cache.py` switching logic
5. Update `__init__.py` exports

This modular structure makes the cache system highly maintainable and extensible! 🚀
