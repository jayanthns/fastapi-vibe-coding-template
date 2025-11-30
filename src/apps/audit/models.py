"""
Audit Log database models.
"""

from typing import Optional

from sqlalchemy import Index, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models import UUIDModel
from src.db.session import Base


class AuditLog(Base, UUIDModel):
    """
    Generic Audit Log model to track system events.
    """

    __tablename__ = "audit_logs"

    # Actor information
    actor_id: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="ID of the user who performed the action",
    )
    actor_email: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Email of the user who performed the action",
    )

    # Action details
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Action performed (CREATE, UPDATE, DELETE)",
    )
    target_model: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Model path of the modified object (e.g. 'animals.Animal')",
    )
    target_object_id: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="ID of the modified object"
    )

    # Change tracking
    changes: Mapped[dict] = mapped_column(
        JSON, default=dict, comment="JSON diff of changes (before/after)"
    )

    # Request metadata
    ip_address: Mapped[Optional[str]] = mapped_column(
        String(45), nullable=True, comment="IP address of the actor"
    )
    user_agent: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="User Agent string of the actor"
    )

    __table_args__ = (
        Index("ix_audit_logs_target", "target_model", "target_object_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_actor_id", "actor_id"),
        Index("ix_audit_logs_actor_email", "actor_email"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        actor = self.actor_email or self.actor_id or "System"
        return (
            f"<AuditLog(action={self.action}, "
            f"target={self.target_model}({self.target_object_id}), "
            f"actor={actor})>"
        )
