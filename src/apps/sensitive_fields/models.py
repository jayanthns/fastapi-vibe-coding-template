"""
Sensitive field configuration model.

This model allows dynamic configuration of which fields should be masked
and how they should be matched (exact match vs regex pattern).
"""

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.apps.base_models import BaseModel


class SensitiveField(BaseModel):
    """
    Model for configuring sensitive field patterns for data masking.

    Extends BaseModel to inherit:
    - UUID primary key (id)
    - Created and updated timestamps (created_at, updated_at)
    - Automatic table naming (sensitive_fields)
    - Common utility methods
    """

    # Field configuration
    field_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Field name or pattern to match",
    )
    is_exact_match: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        comment="True for exact match, False for regex pattern",
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False, comment="Whether this pattern is active"
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Description of what this field contains"
    )

    def __repr__(self):
        return (
            f"<SensitiveField(id={self.id}, field_name='{self.field_name}', "
            f"is_exact_match={self.is_exact_match}, is_active={self.is_active})>"
        )
