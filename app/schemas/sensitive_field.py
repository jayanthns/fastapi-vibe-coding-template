"""
Pydantic schemas for sensitive field configuration.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SensitiveFieldBase(BaseModel):
    """Base schema for sensitive field configuration."""

    field_name: str = Field(
        ..., description="Field name or pattern to match", max_length=255
    )
    is_exact_match: bool = Field(
        True, description="True for exact match, False for regex pattern"
    )
    is_active: bool = Field(True, description="Whether this pattern is active")
    description: Optional[str] = Field(
        None, description="Description of what this field contains"
    )


class SensitiveFieldCreate(SensitiveFieldBase):
    """Schema for creating a new sensitive field pattern."""

    pass


class SensitiveFieldUpdate(BaseModel):
    """Schema for updating a sensitive field pattern."""

    field_name: Optional[str] = Field(
        None, description="Field name or pattern to match", max_length=255
    )
    is_exact_match: Optional[bool] = Field(
        None, description="True for exact match, False for regex pattern"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether this pattern is active"
    )
    description: Optional[str] = Field(
        None, description="Description of what this field contains"
    )


class SensitiveFieldResponse(SensitiveFieldBase):
    """Schema for sensitive field response."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SensitiveFieldList(BaseModel):
    """Schema for listing sensitive fields."""

    items: list[SensitiveFieldResponse]
    total: int
    page: int
    size: int
    pages: int
