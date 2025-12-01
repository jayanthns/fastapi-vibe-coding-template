from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID

from src.core.enums import StrEnum
from src.core.models import UUIDModel
from src.db.session import Base


class JobStatus(StrEnum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class BackgroundJob(Base, UUIDModel):
    __tablename__ = "background_jobs"

    message_id = Column(String, nullable=False, index=True)
    task_name = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default=JobStatus.PENDING, index=True)
    trace_id = Column(String, nullable=True, index=True)

    args = Column(JSON, default=list)
    kwargs = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)

    error = Column(String, nullable=True)
    traceback = Column(Text, nullable=True)

    parent_job_id = Column(UUID(as_uuid=True), ForeignKey("background_jobs.id"), nullable=True)
    attempt_count = Column(Integer, default=1)

    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
