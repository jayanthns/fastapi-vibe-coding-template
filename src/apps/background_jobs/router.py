from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.background_jobs.schemas import BackgroundJobResponse, JobFilter, JobStatus
from src.apps.background_jobs.service import JobService
from src.core.schemas import APIResponse
from src.db.session import get_db

router = APIRouter()


@router.get("/", response_model=APIResponse[list[BackgroundJobResponse]])
async def list_jobs(
    status: JobStatus | None = None,
    task_name: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(50, le=100),
    offset: int = 0,
    session: AsyncSession = Depends(get_db),
):
    filters = JobFilter(status=status, task_name=task_name, date_from=date_from, date_to=date_to)
    jobs = await JobService.list_jobs(session, filters, limit, offset)
    return APIResponse(data=jobs)


@router.get("/{job_id}", response_model=APIResponse[BackgroundJobResponse])
async def get_job(job_id: UUID, session: AsyncSession = Depends(get_db)):
    job = await JobService.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return APIResponse(data=job)


@router.post("/{job_id}/retry", response_model=APIResponse[BackgroundJobResponse])
async def retry_job(job_id: UUID, session: AsyncSession = Depends(get_db)):
    # TODO: Implement retry logic
    # This requires importing the actor by name, which is tricky.
    # For now, we'll return 501 Not Implemented or just a placeholder.
    # The requirement was "later we can re trigger a job".
    # I'll implement a basic placeholder or try to dynamically import.
    raise HTTPException(status_code=501, detail="Retry functionality not yet implemented")
