"""
Repository layer for AuditLog database operations.
"""

from datetime import datetime
from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.audit.models import AuditLog
from src.apps.audit.schemas import AuditLogCreate, AuditLogFilter


class AuditLogRepository:
    """Repository for AuditLog database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, audit_data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry."""
        audit_log = AuditLog(**audit_data.model_dump())
        self.db.add(audit_log)
        await self.db.commit()
        await self.db.refresh(audit_log)
        return audit_log

    async def get_by_id(self, audit_id: UUID) -> Optional[AuditLog]:
        """Get an audit log by ID."""
        result = await self.db.execute(select(AuditLog).where(AuditLog.id == audit_id))
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditLogFilter] = None,
    ) -> tuple[Sequence[AuditLog], int]:
        """List audit logs with optional filtering and pagination."""
        from sqlalchemy import func

        # Build filter conditions
        conditions = []
        if filters:
            if filters.actor_id:
                conditions.append(AuditLog.actor_id == filters.actor_id)
            if filters.actor_email:
                conditions.append(AuditLog.actor_email == filters.actor_email)
            if filters.action:
                conditions.append(AuditLog.action == filters.action)
            if filters.target_model:
                conditions.append(AuditLog.target_model == filters.target_model)
            if filters.target_object_id:
                conditions.append(AuditLog.target_object_id == filters.target_object_id)
            if filters.start_date:
                conditions.append(AuditLog.created_at >= filters.start_date)
            if filters.end_date:
                conditions.append(AuditLog.created_at <= filters.end_date)

        # Build query
        query = select(AuditLog)
        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count(AuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()

        # Get paginated results (ordered by created_at desc)
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        audit_logs = result.scalars().all()

        return audit_logs, total

    async def get_by_target(
        self, target_model: str, target_object_id: str
    ) -> Sequence[AuditLog]:
        """Get all audit logs for a specific target object."""
        result = await self.db.execute(
            select(AuditLog)
            .where(
                and_(
                    AuditLog.target_model == target_model,
                    AuditLog.target_object_id == target_object_id,
                )
            )
            .order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_actor(
        self, actor_id: Optional[str] = None, actor_email: Optional[str] = None
    ) -> Sequence[AuditLog]:
        """Get all audit logs for a specific actor."""
        conditions = []
        if actor_id:
            conditions.append(AuditLog.actor_id == actor_id)
        if actor_email:
            conditions.append(AuditLog.actor_email == actor_email)

        if not conditions:
            return []

        result = await self.db.execute(
            select(AuditLog)
            .where(and_(*conditions))
            .order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()
