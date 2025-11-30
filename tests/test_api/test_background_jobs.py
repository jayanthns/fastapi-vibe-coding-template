import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.service import JobService
from src.apps.background_jobs.tasks import test_background_task, test_failing_task


@pytest.mark.asyncio
async def test_enqueue_job_calls_create_job():
    """Test that enqueue_job calls create_job and sends message."""
    mock_session = AsyncMock()

    with (
        patch(
            "src.apps.background_jobs.service.JobService.create_job"
        ) as mock_create_job,
        patch("src.apps.background_jobs.tasks.test_background_task.send") as mock_send,
    ):

        # Setup mock return values
        mock_job = MagicMock()
        mock_job.id = "job-123"
        mock_job.status = JobStatus.PENDING
        mock_create_job.return_value = mock_job

        mock_message = MagicMock()
        mock_message.message_id = "msg-123"
        mock_send.return_value = mock_message

        # Call enqueue_job
        job = await JobService.enqueue_job(
            mock_session, test_background_task, duration=0
        )

        # Verify send was called
        mock_send.assert_called_once()

        # Verify create_job was called
        mock_create_job.assert_called_once()
        assert job.id == "job-123"
        assert job.status == JobStatus.PENDING


@pytest.mark.asyncio
async def test_job_status_updates_logic():
    """Test status update logic (mocking DB interactions)."""
    mock_session = AsyncMock()
    job_id = "job-123"
    message_id = "msg-123"

    with patch("src.apps.background_jobs.service.JobRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_by_message_id = AsyncMock()
        mock_repo_instance.update = AsyncMock()

        # Setup mock job
        mock_job = MagicMock()
        mock_job.id = job_id
        mock_job.message_id = message_id
        mock_repo_instance.get_by_message_id.return_value = mock_job
        mock_repo_instance.update.return_value = mock_job

        # Test update to RUNNING
        await JobService.update_status_by_message_id(message_id, JobStatus.RUNNING)

        # Verify update called with correct args
        mock_repo_instance.update.assert_called()
        call_args = mock_repo_instance.update.call_args
        assert call_args[1]["status"] == JobStatus.RUNNING


@pytest.mark.asyncio
async def test_job_failure_updates_logic():
    """Test failure update logic (mocking DB interactions)."""
    message_id = "msg-fail"

    with patch("src.apps.background_jobs.service.JobRepository") as MockRepo:
        mock_repo_instance = MockRepo.return_value
        mock_repo_instance.get_by_message_id = AsyncMock()
        mock_repo_instance.update = AsyncMock()

        mock_job = MagicMock()
        mock_repo_instance.get_by_message_id.return_value = mock_job
        mock_repo_instance.update.return_value = mock_job

        # Test update to FAILED
        await JobService.update_status_by_message_id(
            message_id,
            JobStatus.FAILED,
            error="Something went wrong",
            traceback="Traceback...",
        )

        # Verify update called with correct args
        mock_repo_instance.update.assert_called()
        call_args = mock_repo_instance.update.call_args
        assert call_args[1]["status"] == JobStatus.FAILED
        assert call_args[1]["error"] == "Something went wrong"
        assert call_args[1]["traceback"] == "Traceback..."
