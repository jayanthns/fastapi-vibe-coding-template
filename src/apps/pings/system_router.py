"""
System health check endpoints.
"""

from fastapi import APIRouter, Request

from src.core.logging import get_logger
from src.core.schemas import APIResponse
from src.middleware.trace import get_trace_id

router = APIRouter()


@router.get("/", response_model=APIResponse[dict[str, str]])
async def ping(request: Request):
    """Basic ping endpoint to test API connectivity."""
    logger = get_logger(request)
    logger.info("Basic ping endpoint accessed")

    return APIResponse.create_with_trace_id(
        data={"message": "pong", "status": "healthy"},
        message="System is healthy",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/health/", response_model=APIResponse[dict[str, str]])
async def get_system_health(request: Request):
    """Get overall system health status."""
    logger = get_logger(request)
    logger.info("Performing system health check")

    # TODO: Implement comprehensive system health check
    # This should aggregate cache, database, and other service health

    health_data = {
        "overall_status": "healthy",
        "message": "All systems operational",
    }

    logger.info(f"System health check completed - Status: {health_data['overall_status']}")

    return APIResponse.create_with_trace_id(
        data=health_data,
        message="System health check completed",
        status_code=200,
        trace_id=get_trace_id(request),
    )
