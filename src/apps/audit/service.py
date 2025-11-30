"""
Service layer for Audit logging - Async Version.

This service publishes audit events to a Dramatiq queue for async processing.
The worker persists the audit logs to the database.
"""

from typing import Any, Dict, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.audit.models import AuditLog
from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.schemas import AuditLogFilter
from src.core.enums import AuditAction


class AuditService:
    """
    Service for publishing audit events to background queue.

    This service does NOT write to the database directly.
    Instead, it publishes events to Dramatiq which are processed by workers.

    Usage:
        audit_service = AuditService()
        await audit_service.log_create(
            target_model="Animal",
            target_object_id=str(animal.id),
            actor_id=user.id,
            ...
        )
    """

    def __init__(self):
        """Initialize audit service for publishing to queue."""
        pass

    async def log_event(
        self,
        action: str,
        target_model: str,
        target_object_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """
        Publish audit event to queue for async processing.

        Args:
            action: Audit action (CREATE, UPDATE, DELETE)
            target_model: Model name (e.g., "Animal", "User")
            target_object_id: ID of the object being audited
            actor_id: ID of the user performing the action
            actor_email: Email of the user performing the action
            changes: Dict of changes made
            ip_address: IP address of the request
            user_agent: User agent string
            trace_id: Trace ID for request tracking

        Returns:
            None (publishes to queue, non-blocking)
        """
        from src.apps.audit.tasks import write_audit_log
        from src.apps.background_jobs.service import JobService
        from src.db.session import AsyncSessionLocal

        audit_payload = {
            "action": action,
            "target_model": target_model,
            "target_object_id": target_object_id,
            "actor_id": actor_id,
            "actor_email": actor_email,
            "changes": changes or {},
            "ip_address": ip_address,
            "user_agent": user_agent,
            "trace_id": trace_id,
        }

        # Publish to Dramatiq queue and track as background job
        async with AsyncSessionLocal() as session:
            await JobService.enqueue_job(
                session, write_audit_log, audit_payload, trace_id=trace_id
            )

    async def log_create(
        self,
        target_model: str,
        target_object_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
    ) -> None:
        """Publish CREATE audit event to queue."""
        await self.log_event(
            action=AuditAction.CREATE.value,
            target_model=target_model,
            target_object_id=target_object_id,
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
            trace_id=trace_id,
        )

    async def log_update(
        self,
        target_model: str,
        target_object_id: str,
        changes: Dict[str, Any],
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Publish UPDATE audit event to queue."""
        await self.log_event(
            action=AuditAction.UPDATE.value,
            target_model=target_model,
            target_object_id=target_object_id,
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def log_delete(
        self,
        target_model: str,
        target_object_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """Publish DELETE audit event to queue."""
        await self.log_event(
            action=AuditAction.DELETE.value,
            target_model=target_model,
            target_object_id=target_object_id,
            actor_id=actor_id,
            actor_email=actor_email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    @staticmethod
    def create_for_queries(repository: AuditLogRepository) -> "AuditServiceQuery":
        """
        Factory method to create query-only audit service.

        Use this for read operations (listing, searching audit logs).

        Args:
            repository: AuditLogRepository instance

        Returns:
            AuditServiceQuery instance for querying audit logs
        """
        return AuditServiceQuery(repository)


class AuditServiceQuery:
    """
    Service for querying audit logs.

    Separate from AuditService to maintain clear separation:
    - AuditService: Publishes events (write operations)
    - AuditServiceQuery: Queries database (read operations)
    """

    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

    async def get_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditLogFilter] = None,
    ) -> tuple[Sequence[AuditLog], int]:
        """Get audit logs with filtering and pagination."""
        return await self.repository.list(skip, limit, filters)

    async def get_target_history(
        self, target_model: str, target_object_id: str
    ) -> Sequence[AuditLog]:
        """Get audit history for a specific object."""
        return await self.repository.get_by_target(target_model, target_object_id)

    async def get_actor_history(
        self, actor_id: Optional[str] = None, actor_email: Optional[str] = None
    ) -> Sequence[AuditLog]:
        """Get audit history for a specific actor."""
        return await self.repository.get_by_actor(actor_id, actor_email)
