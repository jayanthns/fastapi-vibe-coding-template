"""
Base model classes for common database patterns.

This module provides abstract base classes that define common fields and patterns
used across all models in the application, reducing code duplication and ensuring
consistency.
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from src.db.session import Base


class BaseModel(Base):
    """
    Abstract base model with common fields for all database models.

    This class provides:
    - UUID primary key with auto-generation
    - Created and updated timestamps with timezone support
    - Automatic indexing on common fields
    - Consistent field naming and types
    """

    __abstract__ = True

    # UUID primary key with auto-generation and indexing
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        comment="Unique identifier for this record",
    )

    # Created timestamp - set once when record is created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When this record was created",
    )

    # Updated timestamp - automatically updated on every save
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="When this record was last updated",
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """
        Generate table name from class name.

        Converts CamelCase class names to snake_case table names.
        Example: UserProfile -> user_profiles
        """
        # Convert CamelCase to snake_case
        import re

        name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", cls.__name__)
        name = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()

        # Better pluralization logic
        if name.endswith("y"):
            name = name[:-1] + "ies"
        elif name.endswith(("s", "sh", "ch", "x", "z")):
            name += "es"
        elif not name.endswith("s"):
            name += "s"

        return name

    def __repr__(self) -> str:
        """Generate a string representation of the model instance."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model instance to dictionary.

        Returns:
            Dictionary representation of the model instance
        """
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseModel":
        """
        Create model instance from dictionary.

        Args:
            data: Dictionary containing field values

        Returns:
            New model instance
        """
        # Filter out fields that don't exist on the model
        valid_fields = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}

        return cls(**filtered_data)


class TimestampedModel(Base):
    """
    Abstract base model with only timestamp fields.

    Use this when you need timestamps but want to define your own primary key.
    """

    __abstract__ = True

    # Created timestamp - set once when record is created
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="When this record was created",
    )

    # Updated timestamp - automatically updated on every save
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        index=True,
        comment="When this record was last updated",
    )

    def __repr__(self) -> str:
        """Generate a string representation of the model instance."""
        return f"<{self.__class__.__name__}(created_at={self.created_at})>"


class SoftDeleteModel(BaseModel):
    """
    Abstract base model with soft delete functionality.

    This extends BaseModel to add soft delete capabilities:
    - deleted_at field to track when record was soft deleted
    - is_deleted boolean flag for quick filtering
    - Methods to soft delete and restore records
    """

    __abstract__ = True

    # Soft delete fields
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        index=True,
        comment="Whether this record has been soft deleted",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="When this record was soft deleted",
    )

    def soft_delete(self) -> None:
        """Mark this record as soft deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """Restore this soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None

    @classmethod
    def active_records(cls):
        """Query for non-deleted records."""
        return cls.query.filter(cls.is_deleted.is_(False))

    @classmethod
    def deleted_records(cls):
        """Query for soft deleted records."""
        return cls.query.filter(cls.is_deleted.is_(True))


class AuditModel(BaseModel):
    """
    Abstract base model with audit trail functionality.

    This extends BaseModel to add audit capabilities:
    - created_by and updated_by fields to track who made changes
    - version field for optimistic locking
    """

    __abstract__ = True

    # Audit fields
    created_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the user who created this record",
    )

    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID of the user who last updated this record",
    )

    # Version for optimistic locking
    version: Mapped[int] = mapped_column(
        default=1, nullable=False, comment="Version number for optimistic locking"
    )

    def increment_version(self) -> None:
        """Increment the version number."""
        if self.version is None:
            self.version = 1
        else:
            self.version += 1

    def set_audit_fields(self, user_id: uuid.UUID, is_update: bool = False) -> None:
        """
        Set audit fields for create or update operations.

        Args:
            user_id: ID of the user performing the operation
            is_update: Whether this is an update operation
        """
        if is_update:
            self.updated_by = user_id
            self.increment_version()
        else:
            self.created_by = user_id
            self.updated_by = user_id
            # Initialize version to 1 for new records
            if self.version is None:
                self.version = 1
