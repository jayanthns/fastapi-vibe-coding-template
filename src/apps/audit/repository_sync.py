"""
Synchronous Repository layer for AuditLog database operations.
Used inside Dramatiq workers (sync environment).
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from src.apps.audit.models import AuditLog
from src.apps.audit.schemas import AuditLogCreate, AuditLogFilter


class AuditLogRepositorySync:
    """Synchronous repository for AuditLog database operations."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, audit_data: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry (sync)."""
        audit_log = AuditLog(**audit_data.model_dump())
        self.db.add(audit_log)
        self.db.commit()
        self.db.refresh(audit_log)
        return audit_log

    def get_by_id(self, audit_id: UUID) -> AuditLog | None:
        """Get an audit log by ID (sync)."""
        result = self.db.execute(select(AuditLog).where(AuditLog.id == audit_id))
        return result.scalar_one_or_none()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: AuditLogFilter | None = None,
    ) -> tuple[Sequence[AuditLog], int]:
        """List audit logs with optional filtering and pagination (sync)."""
        from sqlalchemy import func

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

        query = select(AuditLog)
        if conditions:
            query = query.where(and_(*conditions))

        # Total count
        count_query = select(func.count(AuditLog.id))
        if conditions:
            count_query = count_query.where(and_(*conditions))

        total = self.db.execute(count_query).scalar()

        # Paginated results
        query = query.order_by(AuditLog.created_at.desc())
        query = query.offset(skip).limit(limit)
        result = self.db.execute(query)
        logs = result.scalars().all()

        return logs, total

    def get_by_target(self, target_model: str, target_object_id: str) -> Sequence[AuditLog]:
        """Get all audit logs for a specific target (sync)."""
        result = self.db.execute(
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

    def get_by_actor(
        self, actor_id: str | None = None, actor_email: str | None = None
    ) -> Sequence[AuditLog]:
        """Get all audit logs for a specific actor (sync)."""
        conditions = []
        if actor_id:
            conditions.append(AuditLog.actor_id == actor_id)
        if actor_email:
            conditions.append(AuditLog.actor_email == actor_email)

        if not conditions:
            return []

        result = self.db.execute(
            select(AuditLog).where(and_(*conditions)).order_by(AuditLog.created_at.desc())
        )
        return result.scalars().all()
