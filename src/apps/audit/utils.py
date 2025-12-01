"""Helper utilities for audit logging."""

from fastapi import Request

from src.apps.animals.service import AuditContext


def get_audit_context_from_request(request: Request) -> AuditContext:
    """
    Extract audit context from FastAPI request.

    Args:
        request: FastAPI Request object

    Returns:
        AuditContext with user and request metadata
    """
    # Extract user info from request state (set by auth middleware)
    from src.middleware.trace import get_trace_id

    user = getattr(request.state, "user", None)
    user_id = str(user.id) if user else None
    user_email = user.email if user else None

    return AuditContext(
        user_id=user_id,
        user_email=user_email,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        trace_id=get_trace_id(request),
    )
