"""
Sensitive field configuration model.

This model allows dynamic configuration of which fields should be masked
and how they should be matched (exact match vs regex pattern).
"""

import uuid

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.session import Base


class SensitiveField(Base):
    """Model for configuring sensitive field patterns for data masking."""

    __tablename__ = "sensitive_fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    field_name = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Field name or pattern to match",
    )
    is_exact_match = Column(
        Boolean, default=True, comment="True for exact match, False for regex pattern"
    )
    is_active = Column(Boolean, default=True, comment="Whether this pattern is active")
    description = Column(Text, comment="Description of what this field contains")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        comment="When this pattern was created",
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="When this pattern was last updated",
    )

    def __repr__(self):
        return (
            f"<SensitiveField(id={self.id}, field_name='{self.field_name}', "
            f"is_exact_match={self.is_exact_match}, is_active={self.is_active})>"
        )
