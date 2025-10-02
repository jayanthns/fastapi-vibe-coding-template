"""
Background job service with status tracking and caching.
Demonstrates trace_id-aware logging in background tasks.
"""

import asyncio
import time
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict
from uuid import uuid4

from src.core.logging import get_logger_for_trace_id


class JobStatus(str, Enum):
    """Job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobResult:
    """Job result data structure."""

    def __init__(self, job_id: str, trace_id: str):
        self.job_id = job_id
        self.trace_id = trace_id
        self.status = JobStatus.PENDING
        self.created_at = datetime.now(timezone.utc)
        self.started_at: datetime | None = None
        self.completed_at: datetime | None = None
        self.progress = 0
        self.result: Any = None
        self.error: str | None = None
        self.metadata: Dict[str, Any] = {}


class BackgroundJobService:
    """Service for managing background jobs with status tracking."""

    def __init__(self):
        # In-memory cache for job status (in production, use Redis or database)
        self._jobs: Dict[str, JobResult] = {}
        self._running_jobs: Dict[str, asyncio.Task] = {}

    async def create_job(
        self, job_type: str, parameters: Dict[str, Any], trace_id: str
    ) -> str:
        """
        Create a new background job.

        Args:
            job_type: Type of job to execute
            parameters: Job parameters
            trace_id: Request trace ID for logging

        Returns:
            Job ID
        """
        job_id = str(uuid4())
        job_result = JobResult(job_id, trace_id)
        job_result.metadata = {
            "job_type": job_type,
            "parameters": parameters,
            "created_by": trace_id,
        }

        self._jobs[job_id] = job_result

        # Start the job asynchronously
        task = asyncio.create_task(
            self._execute_job(job_id, job_type, parameters, trace_id)
        )
        self._running_jobs[job_id] = task

        logger = get_logger_for_trace_id(trace_id, "app.background_jobs")
        logger.info(f"Created background job {job_id} of type {job_type}")

        return job_id

    async def get_job_status(self, job_id: str) -> JobResult | None:
        """
        Get the status of a background job.

        Args:
            job_id: Job ID to check

        Returns:
            Job result or None if not found
        """
        return self._jobs.get(job_id)

    async def cancel_job(self, job_id: str, trace_id: str) -> bool:
        """
        Cancel a running job.

        Args:
            job_id: Job ID to cancel
            trace_id: Request trace ID for logging

        Returns:
            True if job was cancelled, False if not found or already completed
        """
        if job_id not in self._jobs:
            return False

        job = self._jobs[job_id]
        if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            return False

        # Cancel the running task
        if job_id in self._running_jobs:
            task = self._running_jobs[job_id]
            task.cancel()
            del self._running_jobs[job_id]

        job.status = JobStatus.CANCELLED
        job.completed_at = datetime.now(timezone.utc)

        logger = get_logger_for_trace_id(trace_id, "app.background_jobs")
        logger.info(f"Cancelled background job {job_id}")

        return True

    async def cleanup_old_jobs(self, hours: int = 24):
        """
        Clean up old completed jobs.

        Args:
            hours: Number of hours to keep completed jobs
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

        jobs_to_remove = []
        for job_id, job in self._jobs.items():
            if (
                job.status
                in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]
                and job.completed_at
                and job.completed_at < cutoff_time
            ):
                jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self._jobs[job_id]
            if job_id in self._running_jobs:
                del self._running_jobs[job_id]

        logger = get_logger_for_trace_id("system", "app.background_jobs")
        logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")

    async def _execute_job(
        self, job_id: str, job_type: str, parameters: Dict[str, Any], trace_id: str
    ):
        """
        Execute a background job.

        Args:
            job_id: Job ID
            job_type: Type of job
            parameters: Job parameters
            trace_id: Request trace ID
        """
        job = self._jobs[job_id]
        logger = get_logger_for_trace_id(trace_id, "app.background_jobs")

        try:
            # Update job status to running
            job.status = JobStatus.RUNNING
            job.started_at = datetime.now(timezone.utc)
            logger.info(f"Started background job {job_id} of type {job_type}")

            # Execute the specific job type
            if job_type == "process_article":
                result = await self._process_article_job(job, parameters, logger)
            elif job_type == "send_email":
                result = await self._send_email_job(job, parameters, logger)
            elif job_type == "generate_report":
                result = await self._generate_report_job(job, parameters, logger)
            else:
                raise ValueError(f"Unknown job type: {job_type}")

            # Mark job as completed
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            job.result = result
            job.progress = 100

            logger.info(f"Completed background job {job_id} successfully")

        except asyncio.CancelledError:
            job.status = JobStatus.CANCELLED
            job.completed_at = datetime.now(timezone.utc)
            logger.warning(f"Background job {job_id} was cancelled")
            raise

        except Exception as e:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now(timezone.utc)
            job.error = str(e)
            logger.error(f"Background job {job_id} failed: {str(e)}")

        finally:
            # Clean up running job reference
            if job_id in self._running_jobs:
                del self._running_jobs[job_id]

    async def _process_article_job(
        self, job: JobResult, parameters: Dict[str, Any], logger
    ) -> Dict[str, Any]:
        """Simulate article processing job."""
        article_id = parameters.get("article_id")
        processing_time = parameters.get("processing_time", 5)

        logger.info(f"Processing article {article_id}")

        # Simulate processing with progress updates
        for i in range(processing_time):
            await asyncio.sleep(1)
            job.progress = int((i + 1) / processing_time * 100)
            logger.debug(f"Article {article_id} processing progress: {job.progress}%")

        result = {
            "article_id": article_id,
            "processed_at": datetime.now(timezone.utc).isoformat(),
            "processing_time": processing_time,
            "status": "processed",
        }

        logger.info(f"Article {article_id} processing completed")
        return result

    async def _send_email_job(
        self, job: JobResult, parameters: Dict[str, Any], logger
    ) -> Dict[str, Any]:
        """Simulate email sending job."""
        recipient = parameters.get("recipient")
        subject = parameters.get("subject")

        logger.info(f"Sending email to {recipient}: {subject}")

        # Simulate email sending
        await asyncio.sleep(2)
        job.progress = 50

        # Simulate SMTP delay
        await asyncio.sleep(1)
        job.progress = 100

        result = {
            "recipient": recipient,
            "subject": subject,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
        }

        logger.info(f"Email sent successfully to {recipient}")
        return result

    async def _generate_report_job(
        self, job: JobResult, parameters: Dict[str, Any], logger
    ) -> Dict[str, Any]:
        """Simulate report generation job."""
        report_type = parameters.get("report_type")
        date_range = parameters.get("date_range")

        logger.info(f"Generating {report_type} report for {date_range}")

        # Simulate report generation
        for i in range(10):
            await asyncio.sleep(0.5)
            job.progress = (i + 1) * 10
            logger.debug(f"Report generation progress: {job.progress}%")

        result = {
            "report_type": report_type,
            "date_range": date_range,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "file_path": f"/reports/{report_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.pdf",
            "status": "generated",
        }

        logger.info(f"Report {report_type} generated successfully")
        return result


# Global instance
background_job_service = BackgroundJobService()
