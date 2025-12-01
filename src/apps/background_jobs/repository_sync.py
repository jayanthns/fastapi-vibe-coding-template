from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from src.apps.background_jobs.models import BackgroundJob, JobStatus


class JobRepositorySync:
    def __init__(self, session: Session):
        self.session = session

    def get_by_message_id(self, message_id: str) -> BackgroundJob | None:
        result = self.session.execute(
            select(BackgroundJob).where(BackgroundJob.message_id == message_id)
        )
        return result.scalars().first()

    def update(self, job_id: UUID, **kwargs) -> BackgroundJob | None:
        # If updating status to RUNNING, set started_at if not present
        if kwargs.get("status") == JobStatus.RUNNING and "started_at" not in kwargs:
            kwargs["started_at"] = datetime.utcnow()

        # If updating status to COMPLETED or FAILED, set completed_at if not present
        if (
            kwargs.get("status") in [JobStatus.COMPLETED, JobStatus.FAILED]
            and "completed_at" not in kwargs
        ):
            kwargs["completed_at"] = datetime.utcnow()

        self.session.execute(
            update(BackgroundJob).where(BackgroundJob.id == job_id).values(**kwargs)
        )
        self.session.commit()

        # Re-fetch to return updated object
        result = self.session.execute(select(BackgroundJob).where(BackgroundJob.id == job_id))
        return result.scalars().first()
