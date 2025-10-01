# Flexible Caching Guide

This guide explains how to use the industry-standard caching system with automatic fallback throughout the FastAPI application.

## 🎯 **Overview**

The caching system provides:
- **High Availability**: Automatic fallback from Redis to memory cache
- **Industry Standard**: Follows Netflix/Uber patterns for cache resilience
- **Zero Downtime**: Seamless switching when Redis is unavailable
- **Automatic Recovery**: Switches back to Redis when it recovers
- **Comprehensive Monitoring**: Detailed logging and statistics

### **Cache Architecture:**
- **Primary Cache**: Redis (shared, persistent, distributed)
- **Fallback Cache**: Memory (local, fast, reliable)
- **Automatic Switching**: Based on Redis health checks
- **Health Monitoring**: Every 30 seconds when using fallback

## 🚀 **Quick Start**

### **1. Install Redis**

```bash
# Using Docker (recommended)
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Or install locally
# macOS: brew install redis
# Ubuntu: sudo apt-get install redis-server
```

### **2. Configure Redis**

```bash
# .env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password  # Optional

# Or use full URL
REDIS_URL=redis://:password@localhost:6379/0
```

### **3. Test Cache Connection**

```bash
# Test cache ping (works with both Redis and fallback)
curl "http://localhost:8000/api/v1/pings/cache"

# Get cache info (shows current cache type and fallback status)
curl "http://localhost:8000/api/v1/pings/cache/info"

# List cache keys (works with both Redis and memory cache)
curl "http://localhost:8000/api/v1/pings/cache/keys"
```

## 🔄 **Automatic Fallback System**

The cache system implements industry-standard fallback patterns for high availability:

### **How It Works:**

1. **Primary Cache**: Tries Redis first for all operations
2. **Health Monitoring**: Checks Redis every 30 seconds when using fallback
3. **Automatic Fallback**: Switches to memory cache when Redis fails
4. **Automatic Recovery**: Switches back to Redis when it recovers
5. **Transparent Operation**: Your code works unchanged

### **Fallback Behavior:**

#### **When Redis is Available:**
```
✅ Redis cache connection established successfully
```

#### **When Redis is Unavailable:**
```
✅ Memory cache (fallback) connection established successfully
   Redis unavailable, using memory cache fallback
```

#### **When Redis Recovers:**
```
Redis recovered, switched back to primary cache
```

### **Monitoring Fallback Status:**

```python
from app.core.cache import cache

# Check current cache type
print(f"Cache type: {cache.service_type}")  # "redis" or "memory"
print(f"Is Redis: {cache.is_redis}")        # True or False
print(f"Fallback active: {cache.is_fallback_active}")  # True or False

# Get detailed fallback statistics
info = await cache.info()
fallback_stats = info["fallback_stats"]
print(f"Fallback events: {fallback_stats['events']}")
```

### **Fallback Statistics:**

The system tracks comprehensive fallback metrics:

```python
{
    "fallback_active": true,
    "primary_cache_type": "redis",
    "active_cache_type": "memory",
    "events": {
        "switched_to_fallback": 1,    # Times Redis failed
        "switched_to_primary": 0,     # Times Redis recovered
        "redis_failures": 1           # Total Redis failures
    },
    "last_redis_check": 1759312308.236404
}
```

## 📁 **Cache Module Structure**

The cache system follows industry best practices with a clean, modular architecture:

```
app/core/cache/
├── __init__.py              # Main exports and public API
├── base_cache.py            # Abstract base class for all implementations
├── redis_cache.py           # Redis-based cache implementation
├── memory_cache.py          # In-memory cache implementation
├── fallback_cache.py        # Industry-standard fallback service
├── unified_cache.py         # Legacy unified service (deprecated)
└── cache.py                 # High-level cache manager with serialization
```

### **Key Components:**

- **`FallbackCacheService`**: Main cache service with automatic Redis/Memory switching
- **`BaseCacheService`**: Abstract base class ensuring consistent interface
- **`RedisCacheService`**: Redis implementation with connection pooling
- **`MemoryCacheService`**: In-memory implementation with TTL support
- **`CacheManager`**: High-level operations with automatic serialization

## 🔧 **Usage Patterns**

### **1. Direct Cache Usage (With Automatic Fallback)**

```python
from app.core.cache import cache

# In API endpoint - works with Redis or fallback automatically
async def my_endpoint(request: Request):
    # Use cache directly - fallback is transparent

    # Set value (tries Redis, falls back to memory if needed)
    await cache.set("key", "value", expire=300)  # 5 minutes

    # Get value (works with current active cache)
    value = await cache.get("key")

    # Check existence
    exists = await cache.exists("key")

    # Check which cache is currently active
    cache_type = cache.service_type  # "redis" or "memory"
    is_fallback = cache.is_fallback_active  # True if using fallback

    return {
        "value": value,
        "exists": exists,
        "cache_type": cache_type,
        "is_fallback": is_fallback
    }
```

### **2. Cache Manager Usage**

```python
from app.core.cache import cache

# Set complex objects
data = {"user_id": 123, "name": "John"}
await cache.set("user:123", data, expire=600)

# Get objects
user_data = await cache.get("user:123")

# Check existence
exists = await cache.exists("user:123")
```

### **3. Caching Function Results**

```python
from app.core.cache import cached

@cached("expensive_calculation", expire=300)
async def expensive_calculation(n: int) -> int:
    # This will be cached for 5 minutes
    import asyncio
    await asyncio.sleep(1)  # Simulate work
    return n * n * n

# Usage
result = await expensive_calculation(5)  # Cached
```

### **4. Database Query Caching**

```python
async def get_article(article_id: int, db: AsyncSession):
    # Try cache first
    cache_key = f"article:{article_id}"
    cached_article = await cache.get(cache_key)

    if cached_article:
        return Article(**cached_article)

    # Fetch from database
    article = await article_service.get_article(db, article_id)

    # Cache the result
    await cache.set(cache_key, article.dict(), expire=1800)

    return article
```

## 📋 **Common Use Cases**

### **1. API Response Caching**

```python
@router.get("/articles/{article_id}")
async def get_article(article_id: int, request: Request):
    cache_key = f"article:{article_id}"

    # Try cache first
    cached_data = await cache.get(cache_key)
    if cached_data:
        return {"data": cached_data, "from_cache": True}

    # Fetch and cache
    article = await fetch_article(article_id)
    await cache.set(cache_key, article.dict(), expire=1800)

    return {"data": article, "from_cache": False}
```

### **2. Session Management**

```python
async def create_session(user_id: int):
    session_id = f"session:{uuid4()}"
    session_data = {
        "user_id": user_id,
        "login_time": datetime.now().isoformat(),
        "permissions": ["read", "write"]
    }

    await cache.set(session_id, session_data, expire=3600)  # 1 hour
    return session_id

async def get_session(session_id: str):
    return await cache.get(session_id)
```

### **3. Rate Limiting**

```python
async def check_rate_limit(client_ip: str, limit: int = 10):
    key = f"rate_limit:{client_ip}"
    current_count = await cache.get(key) or 0
    current_count = int(current_count)

    if current_count >= limit:
        return False

    await cache.set(key, str(current_count + 1), expire=60)
    return True
```

### **4. Background Job Status**

```python
async def start_background_job(job_id: str):
    # Set job status
    await cache.set(f"job:{job_id}", "running", expire=3600)

    # Start job
    asyncio.create_task(process_job(job_id))

async def get_job_status(job_id: str):
    return await cache.get(f"job:{job_id}")

async def process_job(job_id: str):
    try:
        # Do work
        await asyncio.sleep(5)
        await cache.set(f"job:{job_id}", "completed", expire=3600)
    except Exception as e:
        await cache.set(f"job:{job_id}", f"failed: {e}", expire=3600)
```

### **5. Distributed Locking**

```python
async def with_distributed_lock(lock_key: str, timeout: int = 30):
    acquired = await redis_service.set(lock_key, "locked", expire=timeout, nx=True)

    if not acquired:
        raise Exception("Lock already held")

    try:
        # Do work
        yield
    finally:
        await redis_service.delete(lock_key)
```

## 🎨 **Cache Invalidation**

### **1. Manual Invalidation**

```python
from app.core.cache import invalidate_article_cache, invalidate_articles_cache

# Invalidate specific article
await invalidate_article_cache(article_id)

# Invalidate articles list
await invalidate_articles_cache()

# Invalidate by pattern
await cache.clear_pattern("user:*")
```

### **2. Automatic Invalidation**

```python
@router.post("/articles/{article_id}")
async def update_article(article_id: int, payload: ArticleUpdate):
    # Update article
    article = await article_service.update_article(article_id, payload)

    # Invalidate related caches
    await invalidate_article_cache(article_id)
    await invalidate_articles_cache()

    return article
```

## 🔍 **Monitoring and Debugging**

### **1. Cache Statistics**

```python
@router.get("/cache/stats")
async def get_cache_stats():
    redis = await get_redis()
    info = await redis.info()

    return {
        "memory_used": info.get("used_memory_human"),
        "connected_clients": info.get("connected_clients"),
        "total_keys": len(await redis.keys("*")),
        "uptime": info.get("uptime_in_seconds")
    }
```

### **2. Cache Keys Inspection**

```python
# List all cache keys
keys = await redis_service.keys("*")

# List specific pattern
article_keys = await redis_service.keys("article:*")

# Get key info
key_type = redis_service.sync_client.type("article:123")
ttl = redis_service.ttl_sync("article:123")
```

## ⚙️ **Configuration**

### **Environment Variables**

```bash
# Redis connection
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your_password

# Cache settings
CACHE_DEFAULT_TTL=3600  # 1 hour
CACHE_MAX_SIZE=1000
```

### **Redis Service Configuration**

```python
# app/core/redis.py
class RedisService:
    def __init__(self):
        self._sync_client = None
        self._async_client = None
        self._lock = asyncio.Lock()

    # Singleton pattern ensures single instance
    _instance = None
```

## 🚨 **Error Handling**

### **1. Graceful Degradation**

```python
async def get_cached_data(key: str):
    try:
        return await cache.get(key)
    except Exception as e:
        logger.warning(f"Cache error: {e}")
        return None  # Fallback to database
```

### **2. Connection Health Checks**

```python
async def health_check():
    try:
        redis = await get_redis()
        return await redis.ping()
    except Exception:
        return False
```

## 📊 **Performance Tips**

### **1. Cache Key Design**

```python
# Good: Hierarchical keys
"user:123:profile"
"user:123:permissions"
"article:456:comments"

# Bad: Flat keys
"user123profile"
"user123permissions"
```

### **2. Expiration Strategy**

```python
# Short-lived: Frequently changing data
await cache.set("user:123:last_seen", timestamp, expire=300)  # 5 min

# Medium-lived: Moderately changing data
await cache.set("article:456", article_data, expire=1800)  # 30 min

# Long-lived: Rarely changing data
await cache.set("user:123:profile", profile_data, expire=3600)  # 1 hour
```

### **3. Batch Operations**

```python
# Efficient: Batch operations
async def get_multiple_articles(article_ids: List[int]):
    keys = [f"article:{id}" for id in article_ids]
    # Use Redis pipeline for batch operations
    return await redis_service.mget(keys)
```

## 🧪 **Testing**

### **1. Test Redis Connection**

```python
def test_redis_connection():
    redis = redis_service
    assert redis.ping_sync() == True
```

### **2. Test Caching**

```python
async def test_caching():
    await cache.set("test:key", "test_value", expire=60)
    value = await cache.get("test:key")
    assert value == "test_value"
```

## 🔗 **API Endpoints**

- `GET /api/v1/pings/redis` - Test Redis connection
- `GET /api/v1/pings/redis/info` - Get Redis server info
- `GET /api/v1/pings/redis/keys` - List Redis keys

## 📚 **Examples**

See `app/examples/redis_usage.py` for comprehensive usage examples including:
- Direct Redis service usage
- Cache manager patterns
- Function result caching
- Database query caching
- Session management
- Rate limiting
- Background job tracking
- Distributed locking
- Pub/sub messaging
- Batch operations
- Cache warming

## 🎯 **Best Practices**

1. **Use appropriate expiration times** based on data volatility
2. **Design cache keys hierarchically** for easy management
3. **Implement cache invalidation** when data changes
4. **Handle Redis failures gracefully** with fallbacks
5. **Monitor cache hit rates** and performance
6. **Use batch operations** for multiple keys
7. **Test caching logic** thoroughly
8. **Document cache strategies** for your team

This Redis caching system provides a robust foundation for high-performance FastAPI applications! 🚀
