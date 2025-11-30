"""
Service layer for Animal business logic with async audit logging.
"""

from typing import Optional, Sequence
from uuid import UUID

from src.apps.animals.models import Animal
from src.apps.animals.repository import AnimalRepository
from src.apps.animals.schemas import AnimalCreate, AnimalUpdate
from src.apps.audit.service import AuditService


class AuditContext:
    """Context object for audit logging metadata."""

    def __init__(
        self,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        trace_id: Optional[str] = None,
    ):
        self.user_id = user_id
        self.user_email = user_email
        self.ip_address = ip_address
        self.user_agent = user_agent
        self.trace_id = trace_id


class AnimalService:
    """Service for Animal business logic with async audit logging."""

    def __init__(self, repository: AnimalRepository):
        self.repository = repository
        self.audit_service = AuditService()

    async def create_animal(
        self, animal_data: AnimalCreate, audit_context: Optional[AuditContext] = None
    ) -> Animal:
        """
        Create a new animal and log audit event.

        Args:
            animal_data: Animal creation data
            audit_context: Optional audit context with user/request metadata

        Returns:
            Created Animal instance
        """
        animal = await self.repository.create(animal_data)

        # Publish audit event to queue (non-blocking)
        if audit_context:
            await self.audit_service.log_create(
                target_model="Animal",
                target_object_id=str(animal.id),
                actor_id=audit_context.user_id,
                actor_email=audit_context.user_email,
                changes=animal_data.model_dump(),
                ip_address=audit_context.ip_address,
                user_agent=audit_context.user_agent,
                trace_id=audit_context.trace_id,
            )

        return animal

    async def get_animal(self, animal_id: UUID) -> Optional[Animal]:
        """Get an animal by ID."""
        return await self.repository.get_by_id(animal_id)

    async def list_animals(
        self, skip: int = 0, limit: int = 100
    ) -> tuple[Sequence[Animal], int]:
        """List all animals with pagination."""
        return await self.repository.list(skip, limit)

    async def update_animal(
        self,
        animal_id: UUID,
        animal_data: AnimalUpdate,
        audit_context: Optional[AuditContext] = None,
    ) -> Optional[Animal]:
        """
        Update an animal and log audit event.

        Args:
            animal_id: ID of animal to update
            animal_data: Update data
            audit_context: Optional audit context with user/request metadata

        Returns:
            Updated Animal instance or None if not found
        """
        # Get original data for changes tracking
        original = await self.repository.get_by_id(animal_id)
        if not original:
            return None

        animal = await self.repository.update(animal_id, animal_data)

        # Publish audit event to queue (non-blocking)
        if audit_context and animal:
            changes = animal_data.model_dump(exclude_unset=True)
            await self.audit_service.log_update(
                target_model="Animal",
                target_object_id=str(animal.id),
                changes=changes,
                actor_id=audit_context.user_id,
                actor_email=audit_context.user_email,
                ip_address=audit_context.ip_address,
                user_agent=audit_context.user_agent,
            )

        return animal

    async def delete_animal(
        self, animal_id: UUID, audit_context: Optional[AuditContext] = None
    ) -> bool:
        """
        Delete an animal and log audit event.

        Args:
            animal_id: ID of animal to delete
            audit_context: Optional audit context with user/request metadata

        Returns:
            True if deleted, False if not found
        """
        # Get animal before deletion for audit
        animal = await self.repository.get_by_id(animal_id)
        if not animal:
            return False

        deleted = await self.repository.delete(animal_id)

        # Publish audit event to queue (non-blocking)
        if deleted and audit_context:
            await self.audit_service.log_delete(
                target_model="Animal",
                target_object_id=str(animal_id),
                actor_id=audit_context.user_id,
                actor_email=audit_context.user_email,
                ip_address=audit_context.ip_address,
                user_agent=audit_context.user_agent,
            )

        return deleted
