# Background Jobs API

This document describes the Background Jobs API that demonstrates how to use FastAPI's background tasks with status tracking, caching, and trace_id-aware logging.

## Overview

The Background Jobs API provides:

- **Asynchronous job execution** with status tracking
- **In-memory caching** for job status (production-ready for Redis)
- **Trace ID integration** for request tracking across background tasks
- **Progress monitoring** with real-time updates
- **Job cancellation** and management
- **Automatic cleanup** of old jobs

## API Endpoints

### 1. Create Article Processing Job

**POST** `/api/v1/jobs/process-article`

Creates a background job to process an article.

**Parameters:**

- `article_id` (int): ID of the article to process
- `processing_time` (int, optional): Time in seconds to simulate processing (default: 5)

**Response:**

```json
{
  "success": true,
  "message": "Background job created successfully",
  "status_code": 202,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "created",
    "message": "Article processing job created for article 123"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 2. Create Email Sending Job

**POST** `/api/v1/jobs/send-email`

Creates a background job to send an email.

**Parameters:**

- `recipient` (str): Email recipient
- `subject` (str): Email subject
- `body` (str, optional): Email body (default: "Hello from FastAPI!")

**Response:**

```json
{
  "success": true,
  "message": "Background job created successfully",
  "status_code": 202,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "created",
    "message": "Email job created for test@example.com"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 3. Create Report Generation Job

**POST** `/api/v1/jobs/generate-report`

Creates a background job to generate a report.

**Parameters:**

- `report_type` (str): Type of report to generate
- `date_range` (str, optional): Date range for the report (default: "last_30_days")

**Response:**

```json
{
  "success": true,
  "message": "Background job created successfully",
  "status_code": 202,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "created",
    "message": "Report generation job created for monthly_sales"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 4. Get Job Status

**GET** `/api/v1/jobs/{job_id}/status`

Gets the current status of a background job.

**Response:**

```json
{
  "success": true,
  "message": "Job 550e8400-e29b-41d4-a716-446655440000 status retrieved",
  "status_code": 200,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "running",
    "progress": 60,
    "created_at": "2024-01-01T10:00:00Z",
    "started_at": "2024-01-01T10:00:01Z",
    "completed_at": null,
    "result": null,
    "error": null,
    "metadata": {
      "job_type": "process_article",
      "parameters": {
        "article_id": 123,
        "processing_time": 5
      },
      "created_by": "550e8400-e29b-41d4-a716-446655440000"
    }
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 5. Cancel Job

**DELETE** `/api/v1/jobs/{job_id}`

Cancels a running background job.

**Response:**

```json
{
  "success": true,
  "message": "Job cancelled successfully",
  "status_code": 200,
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "cancelled",
    "message": "Job 550e8400-e29b-41d4-a716-446655440000 has been cancelled"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 6. List Jobs

**GET** `/api/v1/jobs`

Lists all background jobs with optional status filter.

**Parameters:**

- `status_filter` (str, optional): Filter by job status (pending, running, completed, failed, cancelled)

**Response:**

```json
{
  "success": true,
  "message": "Retrieved 3 jobs",
  "status_code": 200,
  "data": {
    "jobs": [
      {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "progress": 100,
        "created_at": "2024-01-01T10:00:00Z",
        "started_at": "2024-01-01T10:00:01Z",
        "completed_at": "2024-01-01T10:00:05Z",
        "job_type": "process_article",
        "error": null
      }
    ],
    "total": 3,
    "filter": null
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

### 7. List All Jobs (Dedicated Endpoint)

**GET** `/api/v1/jobs/all`

Lists all background jobs without any filtering. This is a dedicated endpoint that explicitly shows all jobs regardless of status.

**Response:**

```json
{
  "success": true,
  "message": "Retrieved all 3 jobs",
  "status_code": 200,
  "data": {
    "jobs": [
      {
        "job_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "completed",
        "progress": 100,
        "created_at": "2024-01-01T10:00:00Z",
        "started_at": "2024-01-01T10:00:01Z",
        "completed_at": "2024-01-01T10:00:05Z",
        "job_type": "process_article",
        "error": null
      },
      {
        "job_id": "550e8400-e29b-41d4-a716-446655440001",
        "status": "running",
        "progress": 60,
        "created_at": "2024-01-01T10:01:00Z",
        "started_at": "2024-01-01T10:01:01Z",
        "completed_at": null,
        "job_type": "send_email",
        "error": null
      }
    ],
    "total": 3,
    "filter": "all"
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## Job Status Values

- **`pending`**: Job created but not yet started
- **`running`**: Job is currently executing
- **`completed`**: Job finished successfully
- **`failed`**: Job failed with an error
- **`cancelled`**: Job was cancelled before completion

## Usage Examples

### Python Client Example

```python
import httpx
import asyncio

async def create_and_monitor_job():
    async with httpx.AsyncClient() as client:
        # Create a job
        response = await client.post(
            "http://localhost:8000/api/v1/jobs/process-article",
            params={"article_id": 123, "processing_time": 5}
        )
        job_id = response.json()["data"]["job_id"]

        # Monitor job status
        while True:
            status_response = await client.get(
                f"http://localhost:8000/api/v1/jobs/{job_id}/status"
            )
            status = status_response.json()["data"]

            print(f"Job {job_id}: {status['status']} ({status['progress']}%)")

            if status["status"] in ["completed", "failed", "cancelled"]:
                break

            await asyncio.sleep(1)

        # List all jobs using the dedicated endpoint
        all_jobs_response = await client.get("http://localhost:8000/api/v1/jobs/all")
        all_jobs = all_jobs_response.json()["data"]
        print(f"Total jobs: {all_jobs['total']}")

asyncio.run(create_and_monitor_job())
```

### cURL Examples

```bash
# Create an article processing job
curl -X POST "http://localhost:8000/api/v1/jobs/process-article?article_id=123&processing_time=3"

# Check job status
curl "http://localhost:8000/api/v1/jobs/{job_id}/status"

# Cancel a job
curl -X DELETE "http://localhost:8000/api/v1/jobs/{job_id}"

# List all jobs (with optional filter)
curl "http://localhost:8000/api/v1/jobs"

# List only completed jobs
curl "http://localhost:8000/api/v1/jobs?status_filter=completed"

# List all jobs using dedicated endpoint
curl "http://localhost:8000/api/v1/jobs/all"
```

## Testing

Run the test script to see the API in action:

```bash
# Start the FastAPI server
make run

# In another terminal, run the test script
python test_background_jobs.py
```

## Architecture

### Components

1. **`BackgroundJobService`**: Core service managing job execution and status
2. **`BackgroundTaskManager`**: Manages periodic cleanup and system tasks
3. **API Endpoints**: RESTful interface for job management
4. **In-Memory Cache**: Stores job status (easily replaceable with Redis)

### Key Features

- **Trace ID Integration**: All background jobs inherit the request's trace_id
- **Progress Tracking**: Real-time progress updates during job execution
- **Automatic Cleanup**: Old jobs are automatically cleaned up after 24 hours
- **Error Handling**: Comprehensive error handling and logging
- **Cancellation Support**: Jobs can be cancelled while running

### Logging

All background jobs are logged with trace_id for complete request tracking:

```log
2024-01-01 10:00:00,123 | INFO | 550e8400-e29b-41d4-a716-446655440000 | app.background_jobs | Created background job 123e4567-e89b-12d3-a456-426614174000 of type process_article
2024-01-01 10:00:01,124 | INFO | 550e8400-e29b-41d4-a716-446655440000 | app.background_jobs | Started background job 123e4567-e89b-12d3-a456-426614174000 of type process_article
2024-01-01 10:00:05,125 | INFO | 550e8400-e29b-41d4-a716-446655440000 | app.background_jobs | Completed background job 123e4567-e89b-12d3-a456-426614174000 successfully
```

## Production Considerations

### Scaling

- **Replace in-memory cache** with Redis for multi-instance deployments
- **Use database** for persistent job storage
- **Implement job queues** (Celery, RQ) for high-volume scenarios
- **Add job retry logic** for failed jobs

### Monitoring

- **Add metrics** for job success/failure rates
- **Implement health checks** for background task manager
- **Add alerting** for stuck or failed jobs
- **Monitor memory usage** of job cache

### Security

- **Add authentication** to job endpoints
- **Implement rate limiting** for job creation
- **Validate job parameters** thoroughly
- **Add audit logging** for job operations
