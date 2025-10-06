"""
Domain-level applications and base models.

This package contains all the domain-specific applications and provides
base model classes for consistent database patterns across the application.
"""

from src.apps.base_models import (
    AuditModel,
    BaseModel,
    SoftDeleteModel,
    TimestampedModel,
)

__all__ = [
    "BaseModel",
    "TimestampedModel",
    "SoftDeleteModel",
    "AuditModel",
]
