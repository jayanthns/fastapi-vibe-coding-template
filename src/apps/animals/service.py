"""
Service layer for Animal business logic.
"""

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.animals.models import Animal
from src.apps.animals.repository import AnimalRepository
from src.apps.animals.schemas import AnimalCreate, AnimalUpdate


class AnimalService:
    """Service for Animal business logic."""

    def __init__(self, repository: AnimalRepository):
        self.repository = repository

    async def create_animal(self, animal_data: AnimalCreate) -> Animal:
        """Create a new animal."""
        return await self.repository.create(animal_data)

    async def get_animal(self, animal_id: UUID) -> Optional[Animal]:
        """Get an animal by ID."""
        return await self.repository.get_by_id(animal_id)

    async def list_animals(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Animal], int]:
        """List all animals with pagination."""
        return await self.repository.list(skip, limit)

    async def update_animal(
        self, animal_id: UUID, animal_data: AnimalUpdate
    ) -> Optional[Animal]:
        """Update an animal."""
        return await self.repository.update(animal_id, animal_data)

    async def delete_animal(self, animal_id: UUID) -> bool:
        """Delete an animal."""
        return await self.repository.delete(animal_id)
