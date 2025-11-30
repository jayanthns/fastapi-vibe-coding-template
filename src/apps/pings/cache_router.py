"""
Ping API endpoints for checking service connectivity.
Includes Redis ping functionality to verify Redis connection.
"""

import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from src.core.logging import get_logger
from src.core.schemas import APIResponse
from src.middleware.trace import get_trace_id
from src.utils.security import secure_response

router = APIRouter(tags=["cache-health"])


def _is_sensitive_key(key: str) -> bool:
    """Check if a key contains sensitive information that shouldn't be exposed."""
    sensitive_patterns = [
        "password",
        "passwd",
        "pwd",
        "secret",
        "token",
        "key",
        "auth",
        "credential",
        "session",
        "jwt",
        "api_key",
        "private",
        "sensitive",
    ]
    key_lower = key.lower()
    return any(pattern in key_lower for pattern in sensitive_patterns)


@router.get(
    "/",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def ping_cache(request: Request):
    """
    Ping cache service to check connectivity.

    Returns:
        Cache connection status and response time
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info("Pinging cache service")

    try:
        from src.core.cache import cache
        from src.core.config import settings

        # Test sync cache connection
        sync_start_time = time.time()
        sync_pong = cache.ping_sync()
        sync_response_time = (time.time() - sync_start_time) * 1000  # Convert to ms

        # Test async cache connection
        async_start_time = time.time()
        async_pong = await cache.ping()
        async_response_time = (time.time() - async_start_time) * 1000  # Convert to ms

        # Log Redis unavailability if both connections failed
        if not sync_pong and not async_pong:
            logger.warning(
                f"Redis cache is unavailable - Sync: {sync_pong}, Async: {async_pong}, "
                f"Response times: Sync={sync_response_time:.2f}ms, Async={async_response_time:.2f}ms"
            )
        elif not sync_pong or not async_pong:
            logger.warning(
                f"Redis cache partial failure - Sync: {sync_pong}, Async: {async_pong}, "
                f"Response times: Sync={sync_response_time:.2f}ms, Async={async_response_time:.2f}ms"
            )

        # Prepare response data
        response_data = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": settings.redis_url if settings.use_redis else None,
            "sync_connection": {
                "status": "connected" if sync_pong else "failed",
                "response_time_ms": round(sync_response_time, 2),
                "ping_result": sync_pong,
            },
            "async_connection": {
                "status": "connected" if async_pong else "failed",
                "response_time_ms": round(async_response_time, 2),
                "ping_result": async_pong,
            },
            "overall_status": "healthy" if (sync_pong and async_pong) else "unhealthy",
        }

        # Log success or failure status
        if sync_pong and async_pong:
            logger.info(
                f"Cache ping successful - Type: {cache.service_type}, "
                f"Sync: {sync_pong}, Async: {async_pong}, "
                f"Response times: Sync={sync_response_time:.2f}ms, Async={async_response_time:.2f}ms"
            )
        else:
            logger.info(
                f"Cache ping completed with issues - Type: {cache.service_type}, "
                f"Sync: {sync_pong}, Async: {async_pong}, "
                f"Response times: Sync={sync_response_time:.2f}ms, Async={async_response_time:.2f}ms"
            )

        # Create secure response with automatic masking
        secure_data = secure_response(response_data)
        return APIResponse.create_with_trace_id(
            data=secure_data["data"],
            message=(
                f"{cache.service_type.title()} cache ping successful"
                if (sync_pong and async_pong)
                else f"{cache.service_type.title()} cache ping failed"
            ),
            status_code=200,
            trace_id=trace_id,
        )

    except ImportError as e:
        logger.error(f"Redis packages not installed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Redis packages not installed. Please install redis and aioredis packages.",
        )

    except Exception as e:
        logger.error(f"Cache ping failed: {str(e)}")

        # Return error response with connection details
        error_data = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": settings.redis_url if settings.use_redis else None,
            "error": str(e),
            "overall_status": "unhealthy",
        }

        # Create secure response with automatic masking
        secure_data = secure_response(error_data)

        # Use HTTPException to properly set status code
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": "Cache ping failed",
                "data": secure_data["data"],
                "error": str(e),
                "trace_id": trace_id,
            },
        )


@router.get(
    "/info",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_cache_info(request: Request):
    """
    Get cache service information and statistics.

    Returns:
        Cache service info, memory usage, and connection details
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info("Getting cache service information")

    try:
        from src.core.cache import cache
        from src.core.config import settings

        # Test connection first
        if not cache.ping_sync():
            raise Exception("Cache service is not responding")

        # Get cache info
        info = cache.info_sync()

        # Extract relevant information
        redis_info = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": settings.redis_url if settings.use_redis else None,
            "server": {
                "version": info.get("redis_version", "unknown"),
                "mode": info.get("redis_mode", "unknown"),
                "os": info.get("os", "unknown"),
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
            },
            "memory": {
                "used_memory_human": info.get("used_memory_human", "unknown"),
                "used_memory_peak_human": info.get("used_memory_peak_human", "unknown"),
                "maxmemory_human": info.get("maxmemory_human", "0B"),
                "mem_fragmentation_ratio": info.get("mem_fragmentation_ratio", 0),
            },
            "stats": {
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "expired_keys": info.get("expired_keys", 0),
            },
            "databases": {},
            "status": "healthy",
        }

        # Get database information
        for key, value in info.items():
            if key.startswith("db"):
                redis_info["databases"][key] = value  # type: ignore

        logger.info(f"Cache info retrieved successfully - Type: {cache.service_type}")

        # Create secure response with automatic masking
        secure_data = secure_response(redis_info)
        return APIResponse.create_with_trace_id(
            data=secure_data["data"],
            message="Cache service information retrieved successfully",
            status_code=200,
            trace_id=trace_id,
        )

    except ImportError as e:
        logger.error(f"Redis packages not installed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Redis packages not installed. Please install redis and aioredis packages.",
        )

    except Exception as e:
        logger.error(f"Failed to get cache info: {str(e)}")

        error_data = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": (settings.redis_url if settings.use_redis else None),
            "error": str(e),
            "status": "unhealthy",
        }

        # Create secure response with automatic masking
        secure_data = secure_response(error_data)

        # Use HTTPException to properly set status code
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": "Failed to get cache service information",
                "data": secure_data["data"],
                "error": str(e),
                "trace_id": trace_id,
            },
        )


@router.get(
    "/keys",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_cache_keys(request: Request, pattern: str = "*", limit: int = 100):
    """
    Get cache keys matching a pattern.

    Args:
        pattern: Key pattern to match (default: "*")
        limit: Maximum number of keys to return (default: 100)

    Returns:
        List of cache keys matching the pattern
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Getting cache keys with pattern: {pattern}, limit: {limit}")

    try:
        from src.core.cache import cache
        from src.core.config import settings

        # Test connection first
        if not cache.ping_sync():
            raise Exception("Cache service is not responding")

        # Get keys matching pattern
        keys = cache.keys_sync(pattern)

        # Filter out sensitive keys for security
        safe_keys = [key for key in keys if not _is_sensitive_key(key)]
        limited_keys = safe_keys[:limit] if len(safe_keys) > limit else safe_keys

        # Count sensitive keys (without exposing them)
        sensitive_count = len(keys) - len(safe_keys)

        # Get key types and TTL for each key
        key_info = []
        for key in limited_keys:
            # For memory cache, we don't have type information, so use "string"
            key_type = "string" if not settings.use_redis else "unknown"
            ttl = cache.ttl_sync(key)

            key_info.append(
                {
                    "key": key,
                    "type": key_type,
                    "ttl": ttl if ttl > 0 else None,  # None means no expiration
                    "ttl_human": f"{ttl}s" if ttl > 0 else "no expiration",
                }
            )

        response_data = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": settings.redis_url if settings.use_redis else None,
            "pattern": pattern,
            "total_keys": len(keys),
            "safe_keys": len(safe_keys),
            "sensitive_keys_filtered": sensitive_count,
            "returned_keys": len(limited_keys),
            "limit": limit,
            "keys": key_info,
            "status": "healthy",
        }

        logger.info(
            f"Retrieved {len(limited_keys)} safe cache keys out of {len(keys)} total "
            f"({sensitive_count} sensitive keys filtered for security)"
        )

        # Create secure response with automatic masking
        secure_data = secure_response(response_data)
        return APIResponse.create_with_trace_id(
            data=secure_data["data"],
            message=f"Retrieved {len(limited_keys)} cache keys",
            status_code=200,
            trace_id=trace_id,
        )

    except ImportError as e:
        logger.error(f"Redis packages not installed: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="Redis packages not installed. Please install redis and aioredis packages.",
        )

    except Exception as e:
        logger.error(f"Failed to get cache keys: {str(e)}")

        error_data = {
            "cache_type": cache.service_type,
            "use_redis": settings.use_redis,
            "redis_url": (settings.redis_url if settings.use_redis else None),
            "pattern": pattern,
            "error": str(e),
            "status": "unhealthy",
        }

        # Create secure response with automatic masking
        secure_data = secure_response(error_data)

        # Use HTTPException to properly set status code
        raise HTTPException(
            status_code=503,
            detail={
                "success": False,
                "message": "Failed to get cache keys",
                "data": secure_data["data"],
                "error": str(e),
                "trace_id": trace_id,
            },
        )
