"""
FastAPI router for Audit API endpoints.
"""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.schemas import AuditLog, AuditLogFilter
from src.apps.audit.service import AuditService, AuditServiceQuery
from src.core.logging import get_logger
from src.core.pagination import PageParams, PaginatedResponse
from src.core.schemas import APIResponse
from src.db.session import get_db_with_trace_id
from src.middleware.trace import get_trace_id

router = APIRouter()


def get_audit_query_service(
    db: AsyncSession = Depends(get_db_with_trace_id),
) -> AuditServiceQuery:
    """Get audit query service instance for read operations."""
    repository = AuditLogRepository(db)
    return AuditService.create_for_queries(repository)


# POST endpoint removed - audit logs are created via background workers
# Services call AuditService.log_create/update/delete which publishes to queue


@router.get("/", response_model=APIResponse[PaginatedResponse[AuditLog]])
async def list_audit_logs(
    request: Request,
    params: PageParams = Depends(),
    actor_id: Optional[str] = Query(None, description="Filter by actor ID"),
    actor_email: Optional[str] = Query(None, description="Filter by actor email"),
    action: Optional[str] = Query(None, description="Filter by action"),
    target_model: Optional[str] = Query(None, description="Filter by target model"),
    target_object_id: Optional[str] = Query(
        None, description="Filter by target object ID"
    ),
    service: AuditServiceQuery = Depends(get_audit_query_service),
):
    """List audit logs with optional filtering and pagination."""
    logger = get_logger(request)
    logger.info(f"Listing audit logs - skip: {params.skip}, limit: {params.limit}")

    # Build filters
    filters = AuditLogFilter(
        actor_id=actor_id,
        actor_email=actor_email,
        action=action,
        target_model=target_model,
        target_object_id=target_object_id,
    )

    audit_logs, total = await service.get_audit_logs(params.skip, params.limit, filters)

    paginated_response = PaginatedResponse.create(
        items=audit_logs,
        total=total,
        params=params,
    )

    logger.info(f"Retrieved {len(audit_logs)} audit logs out of {total}")
    return APIResponse.create_with_trace_id(
        data=paginated_response,
        message=f"Retrieved {len(audit_logs)} audit logs",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/{audit_id}", response_model=APIResponse[AuditLog])
async def get_audit_log(
    request: Request,
    audit_id: UUID,
    service: AuditServiceQuery = Depends(get_audit_query_service),
):
    """Retrieve a single audit log by ID."""
    logger = get_logger(request)
    logger.info(f"Retrieving audit log with ID: {audit_id}")

    audit_log = await service.repository.get_by_id(audit_id)
    if not audit_log:
        logger.warning(f"Audit log not found with ID: {audit_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    logger.info(f"Audit log retrieved successfully: {audit_log.action}")
    return APIResponse.create_with_trace_id(
        data=audit_log,
        message="Audit log retrieved successfully",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get(
    "/target/{target_model}/{target_object_id}",
    response_model=APIResponse[list[AuditLog]],
)
async def get_target_history(
    request: Request,
    target_model: str,
    target_object_id: str,
    service: AuditServiceQuery = Depends(get_audit_query_service),
):
    """Get audit history for a specific target object."""
    logger = get_logger(request)
    logger.info(f"Retrieving audit history for {target_model}({target_object_id})")

    audit_logs = await service.get_target_history(target_model, target_object_id)

    logger.info(f"Retrieved {len(audit_logs)} audit logs for target")
    return APIResponse.create_with_trace_id(
        data=list(audit_logs),
        message=f"Retrieved {len(audit_logs)} audit logs",
        status_code=200,
        trace_id=get_trace_id(request),
    )


@router.get("/actor/history", response_model=APIResponse[list[AuditLog]])
async def get_actor_history(
    request: Request,
    actor_id: Optional[str] = Query(None, description="Actor ID"),
    actor_email: Optional[str] = Query(None, description="Actor email"),
    service: AuditServiceQuery = Depends(get_audit_query_service),
):
    """Get audit history for a specific actor."""
    logger = get_logger(request)
    logger.info(f"Retrieving audit history for actor: {actor_id or actor_email}")

    if not actor_id and not actor_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either actor_id or actor_email must be provided",
        )

    audit_logs = await service.get_actor_history(actor_id, actor_email)

    logger.info(f"Retrieved {len(audit_logs)} audit logs for actor")
    return APIResponse.create_with_trace_id(
        data=list(audit_logs),
        message=f"Retrieved {len(audit_logs)} audit logs",
        status_code=200,
        trace_id=get_trace_id(request),
    )
