"""
Trace ID Middleware - Django-style request-level trace ID generation
Creates a unique trace_id for each request and makes it available throughout the request lifecycle.
"""

import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from src.core.logging import RequestLogger, log_error, log_request_access


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates a unique trace_id for each request and stores it in request state.
    Similar to Django's request-level middleware pattern.
    """

    def __init__(self, app, trace_id_header: str = "X-Trace-ID"):
        super().__init__(app)
        self.trace_id_header = trace_id_header

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Generate unique trace_id for this request
        trace_id = str(uuid4())

        # Get correlation_id from headers or generate new one if needed
        correlation_id = request.headers.get("X-Correlation-ID")

        # Store trace_id and correlation_id in request state
        request.state.trace_id = trace_id
        request.state.correlation_id = correlation_id

        # Create and attach request-scoped logger
        request_logger = RequestLogger(trace_id, "src.request", correlation_id)
        request.state.logger = request_logger

        # Add request start time for performance tracking
        request.state.start_time = time.time()

        # Log request start
        request_logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"method": request.method, "path": request.url.path},
        )

        try:
            # Process the request
            response = await call_next(request)

            # Add trace_id to response headers
            response.headers[self.trace_id_header] = trace_id

            # Add request processing time header
            if hasattr(request.state, "start_time"):
                processing_time = time.time() - request.state.start_time
                response.headers["X-Response-Time"] = f"{processing_time:.4f}s"

            # Log request completion
            request_logger.info(
                f"Request completed: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Time: {processing_time:.4f}s",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "processing_time": processing_time,
                },
            )

            # Log to access log
            log_request_access(
                trace_id,
                request.method,
                request.url.path,
                response.status_code,
                processing_time,
            )

            return response

        except Exception as e:
            # Log request error
            request_logger.error(
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(e),
                },
            )

            # Log to error log
            log_error(
                trace_id,
                f"Request failed: {request.method} {request.url.path} - Error: {str(e)}",
                e,
            )

            raise


def get_trace_id(request: Request) -> str:
    """
    Utility function to get the trace_id from request state.
    Similar to Django's request.META.get('TRACE_ID').

    Usage:
        from fastapi import Depends, Request
        from src.middleware.trace import get_trace_id

        @router.get("/")
        async def endpoint(request: Request):
            trace_id = get_trace_id(request)
            return {"trace_id": trace_id}
    """
    return getattr(request.state, "trace_id", str(uuid4()))


def get_request_processing_time(request: Request) -> float:
    """
    Get the request processing time so far.

    Usage:
        from src.middleware.trace import get_request_processing_time

        processing_time = get_request_processing_time(request)
    """
    if hasattr(request.state, "start_time"):
        return time.time() - request.state.start_time
    return 0.0


def get_request_logger(request: Request) -> RequestLogger:
    """
    Get the request-scoped logger with trace_id.

    Usage:
        from src.middleware.trace import get_request_logger

        @router.get("/")
        async def endpoint(request: Request):
            logger = get_request_logger(request)
            logger.info("Processing request")
    """
    return getattr(request.state, "logger", RequestLogger(get_trace_id(request)))
