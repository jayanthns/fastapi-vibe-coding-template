from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.logging import get_logger
from src.core.schemas import APIResponse


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Global handler for HTTP exceptions.
    """
    logger = get_logger(request)
    logger.warning(f"HTTP error: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content=APIResponse(
            success=False,
            message=str(exc.detail),
            status_code=exc.status_code,
            error=str(exc.detail),
            trace_id=getattr(request.state, "trace_id", "no-trace-id"),
        ).model_dump(mode="json"),
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Global handler for validation errors (Pydantic).
    """
    logger = get_logger(request)
    logger.warning(f"Validation error: {exc.errors()}")

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=APIResponse(
            success=False,
            message="Validation error",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error=str(exc.errors()),
            trace_id=getattr(request.state, "trace_id", "no-trace-id"),
        ).model_dump(mode="json"),
    )


async def general_exception_handler(request: Request, exc: Exception):
    """
    Global handler for unhandled exceptions.
    """
    logger = get_logger(request)
    logger.error(f"Unhandled exception: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=APIResponse(
            success=False,
            message="Internal server error",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="An unexpected error occurred",
            trace_id=getattr(request.state, "trace_id", "no-trace-id"),
        ).model_dump(mode="json"),
    )
