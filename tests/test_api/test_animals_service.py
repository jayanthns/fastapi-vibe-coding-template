import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from src.apps.animals.service import AnimalService, AuditContext
from src.apps.animals.schemas import AnimalCreate, AnimalUpdate
from src.apps.animals.repository import AnimalRepository


@pytest.mark.asyncio
class TestAnimalService:
    async def test_create_animal_with_audit(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        mock_animal = MagicMock()
        mock_animal.id = uuid4()
        mock_repo.create = AsyncMock(return_value=mock_animal)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_create = AsyncMock()

            service = AnimalService(repository=mock_repo)

            animal_data = AnimalCreate(name="Dog", species="Canine", age=5)
            audit_context = AuditContext(user_id="123", trace_id="trace-1")

            result = await service.create_animal(animal_data, audit_context)

            assert result == mock_animal
            mock_repo.create.assert_called_once()
            mock_audit_instance.log_create.assert_called_once()
            call_args = mock_audit_instance.log_create.call_args[1]
            assert call_args["target_object_id"] == str(mock_animal.id)
            assert call_args["trace_id"] == "trace-1"

    async def test_create_animal_no_audit(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        mock_animal = MagicMock()
        mock_repo.create = AsyncMock(return_value=mock_animal)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_create = AsyncMock()

            service = AnimalService(repository=mock_repo)

            animal_data = AnimalCreate(name="Cat", species="Feline", age=3)

            result = await service.create_animal(animal_data, audit_context=None)

            assert result == mock_animal
            mock_audit_instance.log_create.assert_not_called()

    async def test_update_animal_success(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        animal_id = uuid4()
        mock_animal = MagicMock()
        mock_animal.id = animal_id

        mock_repo.get_by_id = AsyncMock(return_value=mock_animal)
        mock_repo.update = AsyncMock(return_value=mock_animal)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_update = AsyncMock()

            service = AnimalService(repository=mock_repo)

            update_data = AnimalUpdate(name="Updated Dog")
            audit_context = AuditContext(user_id="123")

            result = await service.update_animal(animal_id, update_data, audit_context)

            assert result == mock_animal
            mock_repo.update.assert_called_once()
            mock_audit_instance.log_update.assert_called_once()

    async def test_update_animal_not_found(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = AnimalService(repository=mock_repo)

        result = await service.update_animal(uuid4(), AnimalUpdate(name="Ghost"))
        assert result is None
        mock_repo.update.assert_not_called()

    async def test_delete_animal_success(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        animal_id = uuid4()
        mock_animal = MagicMock()

        mock_repo.get_by_id = AsyncMock(return_value=mock_animal)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_delete = AsyncMock()

            service = AnimalService(repository=mock_repo)

            audit_context = AuditContext(user_id="123")
            result = await service.delete_animal(animal_id, audit_context)

            assert result is True
            mock_audit_instance.log_delete.assert_called_once()

    async def test_delete_animal_not_found(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        mock_repo.get_by_id = AsyncMock(return_value=None)

        service = AnimalService(repository=mock_repo)

        result = await service.delete_animal(uuid4())
        assert result is False
        mock_repo.delete.assert_not_called()

    async def test_update_animal_no_audit(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        animal_id = uuid4()
        mock_animal = MagicMock()
        mock_animal.id = animal_id

        mock_repo.get_by_id = AsyncMock(return_value=mock_animal)
        mock_repo.update = AsyncMock(return_value=mock_animal)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_update = AsyncMock()

            service = AnimalService(repository=mock_repo)

            update_data = AnimalUpdate(name="Updated Dog No Audit")

            result = await service.update_animal(
                animal_id, update_data, audit_context=None
            )

            assert result == mock_animal
            mock_repo.update.assert_called_once()
            mock_audit_instance.log_update.assert_not_called()

    async def test_delete_animal_no_audit(self):
        mock_repo = MagicMock(spec=AnimalRepository)
        animal_id = uuid4()
        mock_animal = MagicMock()

        mock_repo.get_by_id = AsyncMock(return_value=mock_animal)
        mock_repo.delete = AsyncMock(return_value=True)

        with patch("src.apps.animals.service.AuditService") as MockAuditService:
            mock_audit_instance = MockAuditService.return_value
            mock_audit_instance.log_delete = AsyncMock()

            service = AnimalService(repository=mock_repo)

            result = await service.delete_animal(animal_id, audit_context=None)

            assert result is True
            mock_audit_instance.log_delete.assert_not_called()
