from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from src.apps.background_jobs.models import JobStatus


class BackgroundJobBase(BaseModel):
    task_name: str
    status: JobStatus
    args: list[Any] = []
    kwargs: dict[str, Any] = {}
    attempt_count: int


class BackgroundJobResponse(BackgroundJobBase):
    id: UUID
    message_id: str
    result: Any | None = None
    error: str | None = None
    traceback: str | None = None
    parent_job_id: UUID | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class JobFilter(BaseModel):
    status: JobStatus | None = None
    task_name: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
