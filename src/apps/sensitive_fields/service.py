"""
Service layer for sensitive field configuration operations.
"""

from typing import List, Optional

from src.apps.sensitive_fields.repository import SensitiveFieldRepository
from src.apps.sensitive_fields.schemas import SensitiveFieldCreate, SensitiveFieldUpdate


class SensitiveFieldService:
    """Service for sensitive field configuration operations."""

    def __init__(self, repository: SensitiveFieldRepository):
        self.repository = repository

    async def create_sensitive_field(
        self, sensitive_field: SensitiveFieldCreate
    ) -> dict:
        """Create a new sensitive field pattern."""
        # Check if field name already exists
        existing = await self.repository.get_by_field_name(sensitive_field.field_name)
        if existing:
            return {
                "success": False,
                "message": f"Sensitive field pattern '{sensitive_field.field_name}' already exists",
                "data": None,
            }

        db_sensitive_field = await self.repository.create(sensitive_field)
        return {
            "success": True,
            "message": "Sensitive field pattern created successfully",
            "data": {
                "id": db_sensitive_field.id,
                "field_name": db_sensitive_field.field_name,
                "is_exact_match": db_sensitive_field.is_exact_match,
                "is_active": db_sensitive_field.is_active,
                "description": db_sensitive_field.description,
                "created_at": db_sensitive_field.created_at,
                "updated_at": db_sensitive_field.updated_at,
            },
        }

    async def get_sensitive_field(self, sensitive_field_id: int) -> dict:
        """Get a sensitive field pattern by ID."""
        db_sensitive_field = await self.repository.get_by_id(sensitive_field_id)
        if not db_sensitive_field:
            return {
                "success": False,
                "message": "Sensitive field pattern not found",
                "data": None,
            }

        return {
            "success": True,
            "message": "Sensitive field pattern retrieved successfully",
            "data": {
                "id": db_sensitive_field.id,
                "field_name": db_sensitive_field.field_name,
                "is_exact_match": db_sensitive_field.is_exact_match,
                "is_active": db_sensitive_field.is_active,
                "description": db_sensitive_field.description,
                "created_at": db_sensitive_field.created_at,
                "updated_at": db_sensitive_field.updated_at
            },
        }

    async def get_all_sensitive_fields(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> dict:
        """Get all sensitive field patterns with pagination and filtering."""
        items, total = await self.repository.get_all(skip, limit, search, is_active)

        pages = (total + limit - 1) // limit if limit > 0 else 1

        # Convert SQLAlchemy models to dict format
        items_data = [
            {
                "id": item.id,
                "field_name": item.field_name,
                "is_exact_match": item.is_exact_match,
                "is_active": item.is_active,
                "description": item.description,
                "created_at": item.created_at,
                "updated_at": item.updated_at,
            }
            for item in items
        ]

        return {
            "success": True,
            "message": "Sensitive field patterns retrieved successfully",
            "data": {
                "items": items_data,
                "total": total,
                "page": (skip // limit) + 1 if limit > 0 else 1,
                "size": limit,
                "pages": pages,
            },
        }

    async def get_active_sensitive_fields(self) -> List[dict]:
        """Get all active sensitive field patterns for masking logic."""
        db_sensitive_fields = await self.repository.get_all_active()
        return [
            {
                "field_name": field.field_name,
                "is_exact_match": field.is_exact_match,
                "description": field.description,
            }
            for field in db_sensitive_fields
        ]

    async def update_sensitive_field(
        self, sensitive_field_id: int, sensitive_field: SensitiveFieldUpdate
    ) -> dict:
        """Update a sensitive field pattern."""
        # Check if field name already exists (if being updated)
        if sensitive_field.field_name:
            existing = await self.repository.get_by_field_name(
                sensitive_field.field_name
            )
            if existing and existing.id != sensitive_field_id:
                return {
                    "success": False,
                    "message": f"Sensitive field pattern '{sensitive_field.field_name}' already exists",
                    "data": None,
                }

        db_sensitive_field = await self.repository.update(
            sensitive_field_id, sensitive_field
        )
        if not db_sensitive_field:
            return {
                "success": False,
                "message": "Sensitive field pattern not found",
                "data": None,
            }

        return {
            "success": True,
            "message": "Sensitive field pattern updated successfully",
            "data": db_sensitive_field,
        }

    async def delete_sensitive_field(self, sensitive_field_id: int) -> dict:
        """Delete a sensitive field pattern."""
        success = await self.repository.delete(sensitive_field_id)
        if not success:
            return {
                "success": False,
                "message": "Sensitive field pattern not found",
                "data": None,
            }

        return {
            "success": True,
            "message": "Sensitive field pattern deleted successfully",
            "data": None,
        }

    async def deactivate_sensitive_field(self, sensitive_field_id: int) -> dict:
        """Deactivate a sensitive field pattern (soft delete)."""
        db_sensitive_field = await self.repository.deactivate(sensitive_field_id)
        if not db_sensitive_field:
            return {
                "success": False,
                "message": "Sensitive field pattern not found",
                "data": None,
            }

        return {
            "success": True,
            "message": "Sensitive field pattern deactivated successfully",
            "data": db_sensitive_field,
        }

    async def activate_sensitive_field(self, sensitive_field_id: int) -> dict:
        """Activate a sensitive field pattern."""
        db_sensitive_field = await self.repository.activate(sensitive_field_id)
        if not db_sensitive_field:
            return {
                "success": False,
                "message": "Sensitive field pattern not found",
                "data": None,
            }

        return {
            "success": True,
            "message": "Sensitive field pattern activated successfully",
            "data": db_sensitive_field,
        }
