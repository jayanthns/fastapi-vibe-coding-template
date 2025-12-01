"""
Pydantic schemas for Animal API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AnimalBase(BaseModel):
    """Base schema for Animal."""

    name: str = Field(..., max_length=100, description="Name of the animal")
    species: str = Field(..., max_length=50, description="Species of the animal")
    age: int = Field(..., ge=0, description="Age of the animal in years")


class AnimalCreate(AnimalBase):
    """Schema for creating a new animal."""

    pass


class AnimalUpdate(BaseModel):
    """Schema for updating an animal."""

    name: str | None = Field(None, max_length=100)
    species: str | None = Field(None, max_length=50)
    age: int | None = Field(None, ge=0)


class Animal(AnimalBase):
    """Schema for Animal response."""

    id: UUID
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
