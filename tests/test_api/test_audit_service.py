from unittest.mock import AsyncMock, patch

import pytest

from src.apps.audit.service import AuditService
from src.core.enums import AuditAction


@pytest.mark.asyncio
class TestAuditService:
    @patch("src.apps.background_jobs.service.JobService.enqueue_job")
    @patch("src.db.session.AsyncSessionLocal")
    async def test_log_event_generic(self, mock_session_local, mock_enqueue_job):
        """Test generic event logging with mocked JobService."""
        # Setup mock session
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        service = AuditService()

        await service.log_event(
            action=AuditAction.LOGIN.value,
            target_model="auth.User",
            target_object_id="1",
            ip_address="127.0.0.1",
            actor_id="123",
            actor_email="test@example.com",
            trace_id="trace-123",
        )

        # Verify JobService.enqueue_job call
        mock_enqueue_job.assert_called_once()
        call_args = mock_enqueue_job.call_args

        # Check arguments passed to enqueue_job
        # args[0] is session, args[1] is task, args[2] is payload
        assert call_args[0][0] == mock_session

        payload = call_args[0][2]
        assert payload["action"] == AuditAction.LOGIN.value
        assert payload["target_model"] == "auth.User"
        assert payload["target_object_id"] == "1"
        assert payload["ip_address"] == "127.0.0.1"
        assert payload["actor_id"] == "123"
        assert payload["actor_email"] == "test@example.com"
        assert payload["trace_id"] == "trace-123"

    @patch("src.apps.background_jobs.service.JobService.enqueue_job")
    @patch("src.db.session.AsyncSessionLocal")
    async def test_log_create_helper(self, mock_session_local, mock_enqueue_job):
        """Test log_create helper."""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        service = AuditService()

        await service.log_create(
            target_model="animals.Animal",
            target_object_id="1",
            actor_id="999",
            changes={"name": "AuditDog"},
        )

        mock_enqueue_job.assert_called_once()
        payload = mock_enqueue_job.call_args[0][2]
        assert payload["action"] == AuditAction.CREATE.value
        assert payload["target_model"] == "animals.Animal"
        assert payload["target_object_id"] == "1"
        assert payload["changes"] == {"name": "AuditDog"}

    @patch("src.apps.background_jobs.service.JobService.enqueue_job")
    @patch("src.db.session.AsyncSessionLocal")
    async def test_log_update_helper(self, mock_session_local, mock_enqueue_job):
        """Test log_update helper."""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        service = AuditService()

        await service.log_update(
            target_model="animals.Animal",
            target_object_id="2",
            changes={"age": {"before": 2, "after": 3}},
        )

        mock_enqueue_job.assert_called_once()
        payload = mock_enqueue_job.call_args[0][2]
        assert payload["action"] == AuditAction.UPDATE.value
        assert payload["target_model"] == "animals.Animal"
        assert payload["target_object_id"] == "2"
        assert payload["changes"] == {"age": {"before": 2, "after": 3}}

    @patch("src.apps.background_jobs.service.JobService.enqueue_job")
    @patch("src.db.session.AsyncSessionLocal")
    async def test_log_delete_helper(self, mock_session_local, mock_enqueue_job):
        """Test log_delete helper."""
        mock_session = AsyncMock()
        mock_session_local.return_value.__aenter__.return_value = mock_session

        service = AuditService()

        await service.log_delete(target_model="animals.Animal", target_object_id="3")

        mock_enqueue_job.assert_called_once()
        payload = mock_enqueue_job.call_args[0][2]
        assert payload["action"] == AuditAction.DELETE.value
        assert payload["target_model"] == "animals.Animal"
        assert payload["target_object_id"] == "3"
