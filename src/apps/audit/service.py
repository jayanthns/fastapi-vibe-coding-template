"""
Service layer for Audit logging.
"""

from typing import Any, Dict, Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.audit.models import AuditLog
from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.schemas import AuditLogCreate, AuditLogFilter
from src.core.enums import AuditAction


class AuditService:
    """
    Service for creating audit logs.
    Designed to be injected into other services.
    """

    def __init__(self, repository: AuditLogRepository):
        self.repository = repository

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
    ) -> AuditLog:
        """
        Generic method to log an event.
        Accepts actor_id and actor_email directly.
        """
        audit_data = AuditLogCreate(
            actor_id=actor_id,
            actor_email=actor_email,
            action=action,
            target_model=target_model,
            target_object_id=target_object_id,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent,
        )
        return await self.repository.create(audit_data)

    async def log_create(
        self,
        target_model: str,
        target_object_id: str,
        actor_id: Optional[str] = None,
        actor_email: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Log a creation event."""
        return await self.log_event(
            action=AuditAction.CREATE.value,
            target_model=target_model,
            target_object_id=target_object_id,
            actor_id=actor_id,
            actor_email=actor_email,
            changes=changes,
            ip_address=ip_address,
            user_agent=user_agent,
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
    ) -> AuditLog:
        """Log an update event."""
        return await self.log_event(
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
    ) -> AuditLog:
        """Log a deletion event."""
        return await self.log_event(
            action=AuditAction.DELETE.value,
            target_model=target_model,
            target_object_id=target_object_id,
            actor_id=actor_id,
            actor_email=actor_email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

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
