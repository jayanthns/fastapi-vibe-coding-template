"""
Pydantic schemas for Audit API.
"""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    """Base schema for AuditLog."""

    actor_id: Optional[str] = Field(None, description="ID of the user")
    actor_email: Optional[str] = Field(None, description="Email of the user")
    action: str = Field(..., max_length=50, description="Action performed")
    target_model: str = Field(..., description="Model path of modified object")
    target_object_id: str = Field(..., description="ID of the modified object")
    changes: Dict[str, Any] = Field(
        default_factory=dict, description="JSON diff of changes"
    )
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User Agent string")


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log entry."""

    pass


class AuditLog(AuditLogBase):
    """Schema for AuditLog response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditLogFilter(BaseModel):
    """Schema for filtering audit logs."""

    actor_id: Optional[str] = None
    actor_email: Optional[str] = None
    action: Optional[str] = None
    target_model: Optional[str] = None
    target_object_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
