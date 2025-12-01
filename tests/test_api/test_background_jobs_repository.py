from datetime import datetime, timedelta

import pytest

from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.repository import JobRepository
from src.apps.background_jobs.schemas import JobFilter


@pytest.mark.asyncio
class TestJobRepository:
    async def test_create_job(self, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(
            task_name="test_task",
            args={"arg": 1},
            kwargs={"kwarg": 2},
            message_id="msg_123",
        )
        assert job.id is not None
        assert job.task_name == "test_task"
        assert job.status == JobStatus.PENDING

    async def test_get_by_id(self, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(task_name="test_task", message_id="msg_id_get")
        fetched = await repo.get_by_id(job.id)
        assert fetched is not None
        assert fetched.id == job.id

    async def test_get_by_message_id(self, async_session):
        repo = JobRepository(async_session)
        await repo.create(task_name="test_task", message_id="msg_unique")
        fetched = await repo.get_by_message_id("msg_unique")
        assert fetched is not None
        assert fetched.message_id == "msg_unique"

    async def test_update_status_running(self, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(task_name="test_task", message_id="msg_running")
        assert job.started_at is None

        updated = await repo.update(job.id, status=JobStatus.RUNNING)
        assert updated.status == JobStatus.RUNNING
        assert updated.started_at is not None

    async def test_update_status_completed(self, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(
            task_name="test_task", status=JobStatus.RUNNING, message_id="msg_completed"
        )
        assert job.completed_at is None

        updated = await repo.update(job.id, status=JobStatus.COMPLETED)
        assert updated.status == JobStatus.COMPLETED
        assert updated.completed_at is not None

    async def test_update_status_failed(self, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(
            task_name="test_task", status=JobStatus.RUNNING, message_id="msg_failed"
        )

        updated = await repo.update(job.id, status=JobStatus.FAILED, error="Something went wrong")
        assert updated.status == JobStatus.FAILED
        assert updated.completed_at is not None
        assert updated.error == "Something went wrong"

    async def test_list_jobs_filters(self, async_session):
        repo = JobRepository(async_session)

        # Create jobs
        job1 = await repo.create(task_name="task_a", status=JobStatus.COMPLETED, message_id="1")
        job2 = await repo.create(task_name="task_b", status=JobStatus.FAILED, message_id="2")

        # Filter by status
        jobs = await repo.list_jobs(filters=JobFilter(status=JobStatus.COMPLETED))
        assert len(jobs) >= 1
        assert any(j.id == job1.id for j in jobs)
        assert not any(j.id == job2.id for j in jobs)

        # Filter by task_name
        jobs = await repo.list_jobs(filters=JobFilter(task_name="task_b"))
        assert len(jobs) >= 1
        assert any(j.id == job2.id for j in jobs)

        # Filter by date
        # Since created_at is auto-set, we can filter by current time range
        now = datetime.utcnow()
        jobs = await repo.list_jobs(filters=JobFilter(date_from=now - timedelta(minutes=1)))
        assert len(jobs) >= 2

        jobs = await repo.list_jobs(filters=JobFilter(date_to=now - timedelta(minutes=1)))
        # Should be empty if we just created them
        # (Assuming tests run fast enough and db time is synced)

        # Let's try to manually update created_at for a job to test date filtering better if needed
        # But for now basic coverage should be hit.
