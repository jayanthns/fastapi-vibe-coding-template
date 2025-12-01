"""
Repository layer for Animal database operations.
"""

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.animals.models import Animal
from src.apps.animals.schemas import AnimalCreate, AnimalUpdate


class AnimalRepository:
    """Repository for Animal database operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, animal_data: AnimalCreate) -> Animal:
        """Create a new animal."""
        animal = Animal(**animal_data.model_dump())
        self.db.add(animal)
        await self.db.commit()
        await self.db.refresh(animal)
        return animal

    async def get_by_id(self, animal_id: UUID) -> Animal | None:
        """Get an animal by ID."""
        result = await self.db.execute(select(Animal).where(Animal.id == animal_id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[Sequence[Animal], int]:
        """List all animals with pagination."""
        # Get total count
        from sqlalchemy import func

        count_result = await self.db.execute(select(func.count(Animal.id)))
        total = count_result.scalar()

        # Get paginated results
        result = await self.db.execute(select(Animal).offset(skip).limit(limit))
        animals = result.scalars().all()

        return animals, total

    async def update(self, animal_id: UUID, animal_data: AnimalUpdate) -> Animal | None:
        """Update an animal."""
        animal = await self.get_by_id(animal_id)
        if not animal:
            return None

        update_data = animal_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(animal, field, value)

        await self.db.commit()
        await self.db.refresh(animal)
        return animal

    async def delete(self, animal_id: UUID) -> bool:
        """Delete an animal."""
        animal = await self.get_by_id(animal_id)
        if not animal:
            return False

        await self.db.delete(animal)
        await self.db.commit()
        return True
