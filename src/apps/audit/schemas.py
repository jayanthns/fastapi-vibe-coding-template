"""
Pydantic schemas for Audit API.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    """Base schema for AuditLog."""

    actor_id: str | None = Field(None, description="ID of the user")
    actor_email: str | None = Field(None, description="Email of the user")
    action: str = Field(..., max_length=50, description="Action performed")
    target_model: str = Field(..., description="Model path of modified object")
    target_object_id: str = Field(..., description="ID of the modified object")
    changes: dict[str, Any] = Field(default_factory=dict, description="JSON diff of changes")
    ip_address: str | None = Field(None, description="IP address")
    user_agent: str | None = Field(None, description="User Agent string")
    trace_id: str | None = None


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""

    pass


class AuditLog(AuditLogBase):
    """Schema for AuditLog response."""

    id: UUID
    created_at: datetime
    trace_id: str | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""

    actor_id: str | None = None
    actor_email: str | None = None
    action: str | None = None
    target_model: str | None = None
    target_object_id: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
