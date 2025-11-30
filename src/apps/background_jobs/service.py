from uuid import UUID

import dramatiq
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.background_jobs.models import BackgroundJob, JobStatus
from src.apps.background_jobs.repository import JobRepository
from src.apps.background_jobs.schemas import JobFilter
from src.db.session import AsyncSessionLocal


class JobService:
    @staticmethod
    async def create_job(
        session: AsyncSession, message_id: str, task_name: str, args: list, kwargs: dict
    ) -> BackgroundJob:
        repo = JobRepository(session)
        return await repo.create(
            message_id=message_id,
            task_name=task_name,
            args=args,
            kwargs=kwargs,
            status=JobStatus.PENDING,
        )

    @staticmethod
    async def get_job(session: AsyncSession, job_id: UUID) -> BackgroundJob | None:
        repo = JobRepository(session)
        return await repo.get_by_id(job_id)

    @staticmethod
    async def list_jobs(
        session: AsyncSession, filters: JobFilter, limit: int = 50, offset: int = 0
    ) -> list[BackgroundJob]:
        repo = JobRepository(session)
        return await repo.list_jobs(filters, limit, offset)

    @staticmethod
    async def update_status_by_message_id(
        message_id: str,
        status: JobStatus,
        result: any = None,
        error: str = None,
        traceback: str = None,
    ):
        """
        Used by Middleware to update job status.
        Creates a new session since middleware runs in a separate context.
        """
        async with AsyncSessionLocal() as session:
            repo = JobRepository(session)
            job = await repo.get_by_message_id(message_id)
            if job:
                update_data = {"status": status}
                if result is not None:
                    update_data["result"] = result
                if error is not None:
                    update_data["error"] = error
                if traceback is not None:
                    update_data["traceback"] = traceback

                await repo.update(job.id, **update_data)

    @staticmethod
    async def enqueue_job(
        session: AsyncSession, actor: dramatiq.Actor, *args, **kwargs
    ) -> BackgroundJob:
        """
        Helper to enqueue a job and create the DB record in one go.
        """
        message = actor.send(*args, **kwargs)
        return await JobService.create_job(
            session,
            message_id=message.message_id,
            task_name=actor.actor_name,
            args=list(args),
            kwargs=kwargs,
        )
