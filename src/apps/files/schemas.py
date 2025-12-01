"""
Pydantic schemas for Files API.
"""

from typing import Any

from pydantic import BaseModel, Field


class FileSuccessSchema(BaseModel):
    """Schema for successful file upload response."""

    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Name of the uploaded file")
    size: int = Field(..., description="File size in bytes")
    human_readable_size: str = Field(..., description="Human-readable file size")


class LinearDataResponseSchema(BaseModel):
    """Schema for linear data file upload response."""

    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Name of the uploaded file")
    total_rows: int = Field(..., description="Total number of rows in the file")
    preview_rows: list[dict[str, Any]] = Field(..., description="Preview of first 10 rows")
    human_readable_size: str = Field(..., description="Human-readable file size")
