"""
Repository for sensitive field configuration operations.
"""

from typing import List, Optional
from uuid import UUID

from sqlalchemy import and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.apps.sensitive_fields.models import SensitiveField
from src.apps.sensitive_fields.schemas import SensitiveFieldCreate, SensitiveFieldUpdate


class SensitiveFieldRepository:
    """Repository for sensitive field configuration operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sensitive_field: SensitiveFieldCreate) -> SensitiveField:
        """Create a new sensitive field pattern."""
        db_sensitive_field = SensitiveField(**sensitive_field.model_dump())
        self.db.add(db_sensitive_field)
        await self.db.commit()
        await self.db.refresh(db_sensitive_field)
        return db_sensitive_field

    async def get_by_id(self, sensitive_field_id: UUID) -> Optional[SensitiveField]:
        """Get a sensitive field pattern by ID."""
        result = await self.db.execute(
            select(SensitiveField).where(SensitiveField.id == sensitive_field_id)
        )
        return result.scalar_one_or_none()

    async def get_by_field_name(self, field_name: str) -> Optional[SensitiveField]:
        """Get a sensitive field pattern by field name."""
        result = await self.db.execute(
            select(SensitiveField).where(
                and_(
                    SensitiveField.field_name == field_name,
                    SensitiveField.is_active == True,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> List[SensitiveField]:
        """Get all active sensitive field patterns."""
        result = await self.db.execute(
            select(SensitiveField)
            .where(SensitiveField.is_active == True)
            .order_by(SensitiveField.field_name)
        )
        return result.scalars().all()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[SensitiveField], int]:
        """Get all sensitive field patterns with pagination and filtering."""
        query = select(SensitiveField)
        count_query = select(func.count(SensitiveField.id))

        # Apply filters
        filters = []
        if search:
            filters.append(
                or_(
                    SensitiveField.field_name.ilike(f"%{search}%"),
                    SensitiveField.description.ilike(f"%{search}%"),
                )
            )
        if is_active is not None:
            filters.append(SensitiveField.is_active == is_active)

        if filters:
            query = query.where(and_(*filters))
            count_query = count_query.where(and_(*filters))

        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()

        # Get paginated results
        result = await self.db.execute(
            query.order_by(SensitiveField.field_name).offset(skip).limit(limit)
        )
        items = result.scalars().all()

        return items, total

    async def update(
        self, sensitive_field_id: UUID, sensitive_field: SensitiveFieldUpdate
    ) -> Optional[SensitiveField]:
        """Update a sensitive field pattern."""
        db_sensitive_field = await self.get_by_id(sensitive_field_id)
        if not db_sensitive_field:
            return None

        update_data = sensitive_field.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_sensitive_field, field, value)

        await self.db.commit()
        await self.db.refresh(db_sensitive_field)
        return db_sensitive_field

    async def delete(self, sensitive_field_id: UUID) -> bool:
        """Delete a sensitive field pattern."""
        db_sensitive_field = await self.get_by_id(sensitive_field_id)
        if not db_sensitive_field:
            return False

        await self.db.delete(db_sensitive_field)
        await self.db.commit()
        return True

    async def deactivate(self, sensitive_field_id: UUID) -> Optional[SensitiveField]:
        """Deactivate a sensitive field pattern (soft delete)."""
        db_sensitive_field = await self.get_by_id(sensitive_field_id)
        if not db_sensitive_field:
            return None

        db_sensitive_field.is_active = False
        await self.db.commit()
        await self.db.refresh(db_sensitive_field)
        return db_sensitive_field

    async def activate(self, sensitive_field_id: UUID) -> Optional[SensitiveField]:
        """Activate a sensitive field pattern."""
        db_sensitive_field = await self.get_by_id(sensitive_field_id)
        if not db_sensitive_field:
            return None

        db_sensitive_field.is_active = True
        await self.db.commit()
        await self.db.refresh(db_sensitive_field)
        return db_sensitive_field
