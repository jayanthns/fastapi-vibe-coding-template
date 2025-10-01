"""
Ping API endpoints for checking service connectivity.
Includes Redis ping functionality to verify Redis connection.
"""

import time
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from app.core.logging import get_logger
from app.middleware.trace import get_trace_id
from app.schemas.article import APIResponse

router = APIRouter()


@router.get(
    "/redis",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def ping_redis(request: Request):
    """
    Ping Redis server to check connectivity.

    Returns:
        Redis connection status and response time
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info("Pinging Redis server")

    try:
        from app.core.config import settings
        from app.core.redis import redis_service

        # Test sync Redis connection
        sync_start_time = time.time()
        sync_pong = redis_service.ping_sync()
        sync_response_time = (time.time() - sync_start_time) * 1000  # Convert to ms

        # Test async Redis connection
        async_start_time = time.time()
        async_pong = await redis_service.ping()
        async_response_time = (time.time() - async_start_time) * 1000  # Convert to ms

        # Prepare response data
        response_data = {
            "redis_url": settings.redis_url,
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

        logger.info(f"Redis ping successful - Sync: {sync_pong}, Async: {async_pong}")

        return APIResponse.create_with_trace_id(
            data=response_data,
            message=(
                "Redis ping successful"
                if (sync_pong and async_pong)
                else "Redis ping failed"
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
        logger.error(f"Redis ping failed: {str(e)}")

        # Return error response with connection details
        error_data = {
            "redis_url": settings.redis_url,
            "error": str(e),
            "overall_status": "unhealthy",
        }

        return APIResponse.create_with_trace_id(
            data=error_data,
            message="Redis ping failed",
            status_code=503,
            success=False,
            error=str(e),
            trace_id=trace_id,
        )


@router.get(
    "/redis/info",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_redis_info(request: Request):
    """
    Get Redis server information and statistics.

    Returns:
        Redis server info, memory usage, and connection details
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info("Getting Redis server information")

    try:
        from app.core.config import settings
        from app.core.redis import redis_service

        # Test connection first
        if not redis_service.ping_sync():
            raise Exception("Redis server is not responding")

        # Get Redis info
        info = redis_service.info_sync()

        # Extract relevant information
        redis_info = {
            "redis_url": settings.redis_url,
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

        logger.info(
            f"Redis info retrieved successfully - Version: {redis_info['server']['version']}"  # type: ignore
        )

        return APIResponse.create_with_trace_id(
            data=redis_info,
            message="Redis server information retrieved successfully",
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
        logger.error(f"Failed to get Redis info: {str(e)}")

        error_data = {
            "redis_url": settings.redis_url,
            "error": str(e),
            "status": "unhealthy",
        }

        return APIResponse.create_with_trace_id(
            data=error_data,
            message="Failed to get Redis server information",
            status_code=503,
            success=False,
            error=str(e),
            trace_id=trace_id,
        )


@router.get(
    "/redis/keys",
    response_model=APIResponse[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_redis_keys(request: Request, pattern: str = "*", limit: int = 100):
    """
    Get Redis keys matching a pattern.

    Args:
        pattern: Key pattern to match (default: "*")
        limit: Maximum number of keys to return (default: 100)

    Returns:
        List of Redis keys matching the pattern
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Getting Redis keys with pattern: {pattern}, limit: {limit}")

    try:
        from app.core.config import settings
        from app.core.redis import redis_service

        # Test connection first
        if not redis_service.ping_sync():
            raise Exception("Redis server is not responding")

        # Get keys matching pattern
        keys = redis_service.keys_sync(pattern)

        # Limit the number of keys returned
        limited_keys = keys[:limit] if len(keys) > limit else keys

        # Get key types and TTL for each key
        key_info = []
        for key in limited_keys:
            key_type = redis_service.sync_client.type(key).decode("utf-8")
            ttl = redis_service.ttl_sync(key)

            key_info.append(
                {
                    "key": key,
                    "type": key_type,
                    "ttl": ttl if ttl > 0 else None,  # None means no expiration
                    "ttl_human": f"{ttl}s" if ttl > 0 else "no expiration",
                }
            )

        response_data = {
            "redis_url": settings.redis_url,
            "pattern": pattern,
            "total_keys": len(keys),
            "returned_keys": len(limited_keys),
            "limit": limit,
            "keys": key_info,
            "status": "healthy",
        }

        logger.info(
            f"Retrieved {len(limited_keys)} Redis keys out of {len(keys)} total"
        )

        return APIResponse.create_with_trace_id(
            data=response_data,
            message=f"Retrieved {len(limited_keys)} Redis keys",
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
        logger.error(f"Failed to get Redis keys: {str(e)}")

        error_data = {
            "redis_url": settings.redis_url,
            "pattern": pattern,
            "error": str(e),
            "status": "unhealthy",
        }

        return APIResponse.create_with_trace_id(
            data=error_data,
            message="Failed to get Redis keys",
            status_code=503,
            success=False,
            error=str(e),
            trace_id=trace_id,
        )
