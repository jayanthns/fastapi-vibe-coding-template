from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.background_jobs.models import BackgroundJob, JobStatus
from src.apps.background_jobs.schemas import JobFilter


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> BackgroundJob:
        job = BackgroundJob(**kwargs)
        self.session.add(job)
        await self.session.commit()
        await self.session.refresh(job)
        return job

    async def get_by_id(self, job_id: UUID) -> BackgroundJob | None:
        result = await self.session.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
        return result.scalars().first()

    async def get_by_message_id(self, message_id: str) -> BackgroundJob | None:
        result = await self.session.execute(
            select(BackgroundJob).where(BackgroundJob.message_id == message_id)
        )
        return result.scalars().first()

    async def update(self, job_id: UUID, **kwargs) -> BackgroundJob | None:
        # If updating status to RUNNING, set started_at if not present
        if kwargs.get("status") == JobStatus.RUNNING and "started_at" not in kwargs:
            kwargs["started_at"] = datetime.utcnow()

        # If updating status to COMPLETED or FAILED, set completed_at if not present
        if (
            kwargs.get("status") in [JobStatus.COMPLETED, JobStatus.FAILED]
            and "completed_at" not in kwargs
        ):
            kwargs["completed_at"] = datetime.utcnow()

        await self.session.execute(
            update(BackgroundJob).where(BackgroundJob.id == job_id).values(**kwargs)
        )
        await self.session.commit()
        return await self.get_by_id(job_id)

    async def list_jobs(
        self, filters: JobFilter, limit: int = 50, offset: int = 0
    ) -> list[BackgroundJob]:
        query = (
            select(BackgroundJob)
            .order_by(BackgroundJob.created_at.desc())
            .limit(limit)
            .offset(offset)
        )

        if filters.status:
            query = query.where(BackgroundJob.status == filters.status)
        if filters.task_name:
            query = query.where(BackgroundJob.task_name.contains(filters.task_name))
        if filters.date_from:
            query = query.where(BackgroundJob.created_at >= filters.date_from)
        if filters.date_to:
            query = query.where(BackgroundJob.created_at <= filters.date_to)

        result = await self.session.execute(query)
        return result.scalars().all()
