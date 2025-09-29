"""
Tests for background jobs functionality.
Demonstrates pytest configuration and test organization.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from app.services.background_job_service import (
    BackgroundJobService,
    JobResult,
    JobStatus,
)


class TestJobResult:
    """Test JobResult data structure."""

    def test_job_result_creation(self):
        """Test JobResult initialization."""
        job_id = "test-job-123"
        trace_id = "test-trace-456"

        job_result = JobResult(job_id, trace_id)

        assert job_result.job_id == job_id
        assert job_result.trace_id == trace_id
        assert job_result.status == JobStatus.PENDING
        assert job_result.progress == 0
        assert job_result.result is None
        assert job_result.error is None
        assert isinstance(job_result.created_at, datetime)
        assert job_result.started_at is None
        assert job_result.completed_at is None

    def test_job_result_uses_utc_timezone(self):
        """Test that JobResult uses UTC timezone."""
        job_result = JobResult("test-job", "test-trace")

        # Check that created_at is timezone-aware and in UTC
        assert job_result.created_at.tzinfo is not None
        assert job_result.created_at.tzinfo.utcoffset(None).total_seconds() == 0


class TestBackgroundJobService:
    """Test BackgroundJobService functionality."""

    @pytest.fixture
    def job_service(self):
        """Create a fresh BackgroundJobService instance for each test."""
        return BackgroundJobService()

    @pytest.fixture
    def mock_logger(self):
        """Mock logger for testing."""
        with patch(
            "app.services.background_job_service.get_logger_for_trace_id"
        ) as mock:
            mock_logger = AsyncMock()
            mock.return_value = mock_logger
            yield mock_logger

    @pytest.mark.asyncio
    async def test_create_job(self, job_service, mock_logger):
        """Test job creation."""
        job_id = await job_service.create_job(
            job_type="test_job", parameters={"test": "value"}, trace_id="test-trace"
        )

        assert job_id is not None
        assert len(job_id) > 0

        # Check that job was stored
        job_result = await job_service.get_job_status(job_id)
        assert job_result is not None
        assert job_result.job_id == job_id
        assert job_result.status == JobStatus.PENDING
        assert job_result.metadata["job_type"] == "test_job"
        assert job_result.metadata["parameters"] == {"test": "value"}

    @pytest.mark.asyncio
    async def test_get_job_status_not_found(self, job_service):
        """Test getting status of non-existent job."""
        result = await job_service.get_job_status("non-existent-job")
        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_job_not_found(self, job_service, mock_logger):
        """Test cancelling non-existent job."""
        result = await job_service.cancel_job("non-existent-job", "test-trace")
        assert result is False

    @pytest.mark.asyncio
    async def test_cancel_job_already_completed(self, job_service, mock_logger):
        """Test cancelling already completed job."""
        # Create and complete a job
        job_id = await job_service.create_job(
            job_type="test_job", parameters={}, trace_id="test-trace"
        )

        # Manually set job as completed
        job = await job_service.get_job_status(job_id)
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc)

        # Try to cancel
        result = await job_service.cancel_job(job_id, "test-trace")
        assert result is False

    @pytest.mark.asyncio
    async def test_cleanup_old_jobs(self, job_service, mock_logger):
        """Test cleanup of old jobs."""
        # Create a job
        job_id = await job_service.create_job(
            job_type="test_job", parameters={}, trace_id="test-trace"
        )

        # Manually set job as completed with old timestamp
        job = await job_service.get_job_status(job_id)
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.now(timezone.utc).replace(year=2020)  # Very old

        # Cleanup old jobs (keep jobs newer than 1 hour)
        await job_service.cleanup_old_jobs(hours=1)

        # Job should be removed
        result = await job_service.get_job_status(job_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_process_article_job(self, job_service, mock_logger):
        """Test article processing job execution."""
        job_id = await job_service.create_job(
            job_type="process_article",
            parameters={"article_id": 123, "processing_time": 1},
            trace_id="test-trace",
        )

        # Wait for job to complete
        import asyncio

        await asyncio.sleep(2)

        job_result = await job_service.get_job_status(job_id)
        assert job_result.status == JobStatus.COMPLETED
        assert job_result.progress == 100
        assert job_result.result is not None
        assert job_result.result["article_id"] == 123
        assert job_result.result["status"] == "processed"

    @pytest.mark.asyncio
    async def test_send_email_job(self, job_service, mock_logger):
        """Test email sending job execution."""
        job_id = await job_service.create_job(
            job_type="send_email",
            parameters={"recipient": "test@example.com", "subject": "Test"},
            trace_id="test-trace",
        )

        # Wait for job to complete
        import asyncio

        await asyncio.sleep(4)

        job_result = await job_service.get_job_status(job_id)
        assert job_result.status == JobStatus.COMPLETED
        assert job_result.progress == 100
        assert job_result.result is not None
        assert job_result.result["recipient"] == "test@example.com"
        assert job_result.result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_generate_report_job(self, job_service, mock_logger):
        """Test report generation job execution."""
        job_id = await job_service.create_job(
            job_type="generate_report",
            parameters={"report_type": "test_report", "date_range": "2024-01"},
            trace_id="test-trace",
        )

        # Wait for job to complete
        import asyncio

        await asyncio.sleep(6)

        job_result = await job_service.get_job_status(job_id)
        assert job_result.status == JobStatus.COMPLETED
        assert job_result.progress == 100
        assert job_result.result is not None
        assert job_result.result["report_type"] == "test_report"
        assert job_result.result["status"] == "generated"

    @pytest.mark.asyncio
    async def test_unknown_job_type(self, job_service, mock_logger):
        """Test handling of unknown job type."""
        job_id = await job_service.create_job(
            job_type="unknown_job", parameters={}, trace_id="test-trace"
        )

        # Wait for job to fail
        import asyncio

        await asyncio.sleep(1)

        job_result = await job_service.get_job_status(job_id)
        assert job_result.status == JobStatus.FAILED
        assert job_result.error is not None
        assert "Unknown job type" in job_result.error


# Test markers demonstration
@pytest.mark.slow
class TestSlowBackgroundJobs:
    """Tests marked as slow - can be skipped with -m 'not slow'."""

    @pytest.mark.asyncio
    async def test_long_running_job(self):
        """Test a long-running background job."""
        job_service = BackgroundJobService()

        job_id = await job_service.create_job(
            job_type="process_article",
            parameters={"article_id": 999, "processing_time": 10},
            trace_id="test-trace",
        )

        # This test would take 10+ seconds to complete
        # Marked as slow to allow skipping in fast test runs
        assert job_id is not None


@pytest.mark.integration
class TestBackgroundJobIntegration:
    """Integration tests for background jobs."""

    @pytest.mark.asyncio
    async def test_multiple_jobs_concurrent(self):
        """Test multiple jobs running concurrently."""
        job_service = BackgroundJobService()

        # Create multiple jobs
        job_ids = []
        for i in range(3):
            job_id = await job_service.create_job(
                job_type="process_article",
                parameters={"article_id": i, "processing_time": 1},
                trace_id=f"test-trace-{i}",
            )
            job_ids.append(job_id)

        # Wait for all jobs to complete
        import asyncio

        await asyncio.sleep(3)

        # Check all jobs completed
        for job_id in job_ids:
            job_result = await job_service.get_job_status(job_id)
            assert job_result.status == JobStatus.COMPLETED
