"""
Background jobs API endpoints.
Demonstrates background task management with status tracking and trace_id logging.
"""

from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request, status

from app.core.logging import get_logger
from app.middleware.trace import get_trace_id
from app.schemas.article import APIResponse
from app.services.background_job_service import JobStatus, background_job_service

router = APIRouter()


@router.post(
    "/jobs/process-article",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_process_article_job(
    request: Request, article_id: int, processing_time: int = 5
):
    """
    Create a background job to process an article.

    Args:
        article_id: ID of the article to process
        processing_time: Time in seconds to simulate processing

    Returns:
        Job ID and status information
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Creating article processing job for article {article_id}")

    try:
        job_id = await background_job_service.create_job(
            job_type="process_article",
            parameters={"article_id": article_id, "processing_time": processing_time},
            trace_id=trace_id,
        )

        logger.info(f"Article processing job {job_id} created successfully")

        return APIResponse.create_with_trace_id(
            data={
                "job_id": job_id,
                "status": "created",
                "message": f"Article processing job created for article {article_id}",
            },
            message="Background job created successfully",
            status_code=202,
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Failed to create article processing job: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create background job: {str(e)}"
        )


@router.post(
    "/jobs/send-email",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_send_email_job(
    request: Request, recipient: str, subject: str, body: str = "Hello from FastAPI!"
):
    """
    Create a background job to send an email.

    Args:
        recipient: Email recipient
        subject: Email subject
        body: Email body

    Returns:
        Job ID and status information
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Creating email job for {recipient}: {subject}")

    try:
        job_id = await background_job_service.create_job(
            job_type="send_email",
            parameters={"recipient": recipient, "subject": subject, "body": body},
            trace_id=trace_id,
        )

        logger.info(f"Email job {job_id} created successfully")

        return APIResponse.create_with_trace_id(
            data={
                "job_id": job_id,
                "status": "created",
                "message": f"Email job created for {recipient}",
            },
            message="Background job created successfully",
            status_code=202,
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Failed to create email job: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create background job: {str(e)}"
        )


@router.post(
    "/jobs/generate-report",
    response_model=APIResponse[Dict[str, str]],
    status_code=status.HTTP_202_ACCEPTED,
)
async def create_generate_report_job(
    request: Request, report_type: str, date_range: str = "last_30_days"
):
    """
    Create a background job to generate a report.

    Args:
        report_type: Type of report to generate
        date_range: Date range for the report

    Returns:
        Job ID and status information
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Creating report generation job: {report_type} for {date_range}")

    try:
        job_id = await background_job_service.create_job(
            job_type="generate_report",
            parameters={"report_type": report_type, "date_range": date_range},
            trace_id=trace_id,
        )

        logger.info(f"Report generation job {job_id} created successfully")

        return APIResponse.create_with_trace_id(
            data={
                "job_id": job_id,
                "status": "created",
                "message": f"Report generation job created for {report_type}",
            },
            message="Background job created successfully",
            status_code=202,
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Failed to create report generation job: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to create background job: {str(e)}"
        )


@router.get("/jobs/{job_id}/status", response_model=APIResponse[Dict[str, Any]])
async def get_job_status(request: Request, job_id: str):
    """
    Get the status of a background job.

    Args:
        job_id: Job ID to check

    Returns:
        Job status and details
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Checking status for job {job_id}")

    try:
        job_result = await background_job_service.get_job_status(job_id)

        if not job_result:
            logger.warning(f"Job {job_id} not found")
            raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

        # Convert job result to dictionary
        job_data = {
            "job_id": job_result.job_id,
            "status": job_result.status,
            "progress": job_result.progress,
            "created_at": job_result.created_at.isoformat(),
            "started_at": (
                job_result.started_at.isoformat() if job_result.started_at else None
            ),
            "completed_at": (
                job_result.completed_at.isoformat() if job_result.completed_at else None
            ),
            "result": job_result.result,
            "error": job_result.error,
            "metadata": job_result.metadata,
        }

        logger.info(
            f"Job {job_id} status: {job_result.status} ({job_result.progress}%)"
        )

        return APIResponse.create_with_trace_id(
            data=job_data, message=f"Job {job_id} status retrieved", trace_id=trace_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to get job status: {str(e)}"
        )


@router.delete("/jobs/{job_id}", response_model=APIResponse[Dict[str, str]])
async def cancel_job(request: Request, job_id: str):
    """
    Cancel a running background job.

    Args:
        job_id: Job ID to cancel

    Returns:
        Cancellation status
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Cancelling job {job_id}")

    try:
        cancelled = await background_job_service.cancel_job(job_id, trace_id)

        if not cancelled:
            logger.warning(
                f"Job {job_id} could not be cancelled (not found or already completed)"
            )
            raise HTTPException(
                status_code=400, detail=f"Job {job_id} could not be cancelled"
            )

        logger.info(f"Job {job_id} cancelled successfully")

        return APIResponse.create_with_trace_id(
            data={
                "job_id": job_id,
                "status": "cancelled",
                "message": f"Job {job_id} has been cancelled",
            },
            message="Job cancelled successfully",
            trace_id=trace_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")


@router.get("/jobs", response_model=APIResponse[Dict[str, Any]])
async def list_jobs(request: Request, status_filter: JobStatus | None = None):
    """
    List all background jobs with optional status filter.

    Args:
        status_filter: Optional status filter. Use 'all' to explicitly show all jobs,
                      or specify a specific status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Listing jobs with filter: {status_filter}")

    try:
        # Get all jobs from the service
        all_jobs = background_job_service._jobs

        # Filter by status if provided
        if status_filter:
            filtered_jobs = {
                job_id: job
                for job_id, job in all_jobs.items()
                if job.status == status_filter
            }
        else:
            filtered_jobs = all_jobs

        # Convert to list of dictionaries
        jobs_data = []
        for job_id, job_result in filtered_jobs.items():
            job_data = {
                "job_id": job_result.job_id,
                "status": job_result.status,
                "progress": job_result.progress,
                "created_at": job_result.created_at.isoformat(),
                "started_at": (
                    job_result.started_at.isoformat() if job_result.started_at else None
                ),
                "completed_at": (
                    job_result.completed_at.isoformat()
                    if job_result.completed_at
                    else None
                ),
                "job_type": job_result.metadata.get("job_type"),
                "error": job_result.error,
            }
            jobs_data.append(job_data)

        logger.info(f"Found {len(jobs_data)} jobs")

        return APIResponse.create_with_trace_id(
            data={"jobs": jobs_data, "total": len(jobs_data), "filter": status_filter},
            message=f"Retrieved {len(jobs_data)} jobs",
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Failed to list jobs: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")


@router.get("/jobs/all", response_model=APIResponse[Dict[str, Any]])
async def list_all_jobs(request: Request):
    """
    List all background jobs without any filtering.

    Returns:
        List of all jobs regardless of status
    """
    logger = get_logger(request)
    trace_id = get_trace_id(request)

    logger.info("Listing all jobs (no filter)")

    try:
        # Get all jobs from the service
        all_jobs = background_job_service._jobs

        # Convert to list of dictionaries
        jobs_data = []
        for job_id, job_result in all_jobs.items():
            job_data = {
                "job_id": job_result.job_id,
                "status": job_result.status,
                "progress": job_result.progress,
                "created_at": job_result.created_at.isoformat(),
                "started_at": (
                    job_result.started_at.isoformat() if job_result.started_at else None
                ),
                "completed_at": (
                    job_result.completed_at.isoformat()
                    if job_result.completed_at
                    else None
                ),
                "job_type": job_result.metadata.get("job_type"),
                "error": job_result.error,
            }
            jobs_data.append(job_data)

        logger.info(f"Found {len(jobs_data)} total jobs")

        return APIResponse.create_with_trace_id(
            data={"jobs": jobs_data, "total": len(jobs_data), "filter": "all"},
            message=f"Retrieved all {len(jobs_data)} jobs",
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Failed to list all jobs: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to list all jobs: {str(e)}"
        )
