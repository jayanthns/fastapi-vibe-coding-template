from unittest.mock import AsyncMock, MagicMock

import pytest

from src.apps.audit.repository import AuditLogRepository
from src.apps.audit.schemas import AuditLogCreate
from src.apps.audit.service import AuditService
from src.core.enums import AuditAction


@pytest.mark.asyncio
class TestAuditService:
    async def test_log_event_generic(self):
        """Test generic event logging with mock repository."""
        mock_repo = MagicMock(spec=AuditLogRepository)
        mock_repo.create = AsyncMock()

        service = AuditService(repository=mock_repo)

        # Setup mock return value
        mock_log = MagicMock()
        mock_log.action = AuditAction.LOGIN.value
        mock_log.ip_address = "127.0.0.1"
        mock_log.actor_id = "123"
        mock_log.actor_email = "test@example.com"
        mock_repo.create.return_value = mock_log

        log = await service.log_event(
            action=AuditAction.LOGIN.value,
            target_model="auth.User",
            target_object_id="1",
            ip_address="127.0.0.1",
            actor_id="123",
            actor_email="test@example.com",
        )

        # Verify repository call
        mock_repo.create.assert_called_once()
        call_args = mock_repo.create.call_args[0][0]
        assert isinstance(call_args, AuditLogCreate)
        assert call_args.action == AuditAction.LOGIN.value
        assert call_args.target_model == "auth.User"
        assert call_args.target_object_id == "1"
        assert call_args.ip_address == "127.0.0.1"
        assert call_args.actor_id == "123"
        assert call_args.actor_email == "test@example.com"

        # Verify return value
        assert log.action == AuditAction.LOGIN.value
        assert log.ip_address == "127.0.0.1"
        assert log.actor_id == "123"
        assert log.actor_email == "test@example.com"

    async def test_log_create_helper(self):
        """Test log_create helper."""
        mock_repo = MagicMock(spec=AuditLogRepository)
        mock_repo.create = AsyncMock()
        service = AuditService(repository=mock_repo)

        mock_log = MagicMock()
        mock_log.action = AuditAction.CREATE.value
        mock_repo.create.return_value = mock_log

        await service.log_create(
            target_model="animals.Animal",
            target_object_id="1",
            actor_id="999",
            changes={"name": "AuditDog"},
        )

        mock_repo.create.assert_called_once()
        call_args = mock_repo.create.call_args[0][0]
        assert call_args.action == AuditAction.CREATE.value
        assert call_args.target_model == "animals.Animal"
        assert call_args.target_object_id == "1"
        assert call_args.changes == {"name": "AuditDog"}

    async def test_log_update_helper(self):
        """Test log_update helper."""
        mock_repo = MagicMock(spec=AuditLogRepository)
        mock_repo.create = AsyncMock()
        service = AuditService(repository=mock_repo)

        mock_log = MagicMock()
        mock_log.action = AuditAction.UPDATE.value
        mock_repo.create.return_value = mock_log

        await service.log_update(
            target_model="animals.Animal",
            target_object_id="2",
            changes={"age": {"before": 2, "after": 3}},
        )

        mock_repo.create.assert_called_once()
        call_args = mock_repo.create.call_args[0][0]
        assert call_args.action == AuditAction.UPDATE.value
        assert call_args.target_model == "animals.Animal"
        assert call_args.target_object_id == "2"
        assert call_args.changes == {"age": {"before": 2, "after": 3}}

    async def test_log_delete_helper(self):
        """Test log_delete helper."""
        mock_repo = MagicMock(spec=AuditLogRepository)
        mock_repo.create = AsyncMock()
        service = AuditService(repository=mock_repo)

        mock_log = MagicMock()
        mock_log.action = AuditAction.DELETE.value
        mock_repo.create.return_value = mock_log

        await service.log_delete(target_model="animals.Animal", target_object_id="3")

        mock_repo.create.assert_called_once()
        call_args = mock_repo.create.call_args[0][0]
        assert call_args.action == AuditAction.DELETE.value
        assert call_args.target_model == "animals.Animal"
        assert call_args.target_object_id == "3"
