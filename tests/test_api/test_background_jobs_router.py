from uuid import uuid4

import pytest

from src.apps.background_jobs.models import JobStatus
from src.apps.background_jobs.repository import JobRepository


@pytest.mark.asyncio
class TestBackgroundJobsRouter:
    async def test_list_jobs_endpoint(self, async_client, async_session):
        repo = JobRepository(async_session)
        job1 = await repo.create(task_name="task_1", message_id="msg_1", status=JobStatus.COMPLETED)
        job2 = await repo.create(task_name="task_2", message_id="msg_2", status=JobStatus.FAILED)

        response = await async_client.get("/api/v1/jobs/")
        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) >= 2

        # Test filters
        response = await async_client.get("/api/v1/jobs/", params={"status": "COMPLETED"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert any(j["id"] == str(job1.id) for j in data)
        assert not any(j["id"] == str(job2.id) for j in data)

        response = await async_client.get("/api/v1/jobs/", params={"task_name": "task_2"})
        assert response.status_code == 200
        data = response.json()["data"]
        assert any(j["id"] == str(job2.id) for j in data)

    async def test_get_job_endpoint(self, async_client, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(task_name="task_get", message_id="msg_get")

        response = await async_client.get(f"/api/v1/jobs/{job.id}")
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == str(job.id)
        assert data["task_name"] == "task_get"

    async def test_get_job_not_found(self, async_client):
        response = await async_client.get(f"/api/v1/jobs/{uuid4()}")
        assert response.status_code == 404

    async def test_retry_job_endpoint(self, async_client, async_session):
        repo = JobRepository(async_session)
        job = await repo.create(task_name="task_retry", message_id="msg_retry")

        response = await async_client.post(f"/api/v1/jobs/{job.id}/retry")
        assert response.status_code == 501
        assert response.json()["message"] == "Retry functionality not yet implemented"
