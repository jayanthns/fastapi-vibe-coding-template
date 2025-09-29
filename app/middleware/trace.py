"""
Trace ID Middleware - Django-style request-level trace ID generation
Creates a unique trace_id for each request and makes it available throughout the request lifecycle.
"""

import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class TraceIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware that generates a unique trace_id for each request and stores it in request state.
    Similar to Django's request-level middleware pattern.
    """

    def __init__(self, app, trace_id_header: str = "X-Trace-ID"):
        super().__init__(app)
        self.trace_id_header = trace_id_header

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Generate unique trace_id for this request
        trace_id = str(uuid4())

        # Store trace_id in request state (similar to Django's request.META)
        request.state.trace_id = trace_id

        # Add request start time for performance tracking
        request.state.start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Add trace_id to response headers
        response.headers[self.trace_id_header] = trace_id

        # Add request processing time header
        if hasattr(request.state, "start_time"):
            processing_time = time.time() - request.state.start_time
            response.headers["X-Response-Time"] = f"{processing_time:.4f}s"

        return response


def get_trace_id(request: Request) -> str:
    """
    Utility function to get the trace_id from request state.
    Similar to Django's request.META.get('TRACE_ID').

    Usage:
        from fastapi import Depends, Request
        from app.middleware.trace import get_trace_id

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
        from app.middleware.trace import get_request_processing_time

        processing_time = get_request_processing_time(request)
    """
    if hasattr(request.state, "start_time"):
        return time.time() - request.state.start_time
    return 0.0
