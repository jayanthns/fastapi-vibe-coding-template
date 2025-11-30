# Background Jobs System Guide

This guide details the architecture and usage of the Background Jobs system in our FastAPI application. We use **Dramatiq** with **Redis** for reliable background task processing, coupled with a custom tracking system to monitor job status in the database.

## Architecture

The system consists of three main components:

1.  **Background Jobs App (`src/apps/background_jobs`)**: A standalone app that manages the `BackgroundJob` database table and provides APIs for monitoring and control.
2.  **Job Tracking Middleware**: A Dramatiq middleware that automatically intercepts task events (enqueue, start, success, failure) and updates the database.
3.  **Wrapper Pattern**: A design pattern where business logic resides in Service classes, and Dramatiq actors act as thin wrappers to offload execution to the background.

### Database Schema (`BackgroundJob`)

We store job details in a dedicated table with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique Job ID (PK) |
| `message_id` | String | Dramatiq Message ID |
| `task_name` | String | Full python path of the task (e.g., `src.apps.emails.tasks.send_email`) |
| `status` | Enum | `PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `RETRYING` |
| `args` | JSON | Positional arguments passed to the task |
| `kwargs` | JSON | Keyword arguments passed to the task |
| `result` | JSON | Return value of the task (if successful) |
| `error` | String | Error message (if failed) |
| `traceback` | Text | Full stack trace (if failed) |
| `parent_job_id` | UUID | ID of the original job (if this is a retry) |
| `attempt_count` | Int | Number of times this job has been attempted |
| `created_at` | DateTime | When the job was enqueued |
| `started_at` | DateTime | When execution began |
| `completed_at` | DateTime | When execution finished |
| `trace_id` | String | Trace ID for request tracking |

## Developer Guide: How to Add a Background Task

Follow these steps to implement a new background task using the Wrapper Pattern.

### 1. Define Business Logic in Service

Always implement the actual logic in your domain Service. This keeps the code testable and reusable.

```python
# src/apps/animals/service.py

class AnimalService:
    @staticmethod
    async def process_csv_upload(file_id: str, user_id: str):
        # ... complex logic to read file, validate, and save animals ...
        pass
```

### 2. Create the Dramatiq Actor (Wrapper)

Create a `tasks.py` in your app. Define an actor that wraps the service call.

```python
# src/apps/animals/tasks.py
import dramatiq
from src.db.session_sync import SessionLocalSync
from src.apps.animals.repository_sync import AnimalRepositorySync

@dramatiq.actor(max_retries=3)
def process_animal_upload_task(file_id: str, user_id: str):
    # Dramatiq workers run in a synchronous environment.
    # DO NOT use AsyncSession or asyncio.run() if possible.
    # Instead, use the synchronous session and repository.
    
    with SessionLocalSync() as session:
        repo = AnimalRepositorySync(session)
        # Perform synchronous operations
        repo.process_upload(file_id, user_id)
```

> [!IMPORTANT]
> **Synchronous vs Asynchronous**: Dramatiq workers are synchronous by default. While you *can* use `asyncio.run()` to call async code, it is **highly recommended** to use synchronous database sessions (`SessionLocalSync`) and synchronous repositories for background tasks to avoid event loop issues and connection pool exhaustion.
>
> If you must reuse async service logic, ensure it is properly isolated and handles the event loop correctly. However, the preferred pattern is to have a synchronous path for background workers.

### 3. Trigger the Task

Call `.send()` on the actor to enqueue the task.

```python
# src/apps/animals/router.py

@router.post("/upload")
async def upload_animals(file: UploadFile):
    # ... save file ...
    
    # Trigger background task
    process_animal_upload_task.send(file_id, user_id)
    
    return {"message": "Upload processing started"}
```

## API Reference

The `background_jobs` app provides the following APIs:

### List Jobs
`GET /api/v1/jobs/`
- Filter by `status`, `task_name`, `date_range`.
- Returns a paginated list of jobs.

### Get Job Details
`GET /api/v1/jobs/{id}/`
- Returns full details including status, result, and error traceback.

### Retry Job
`POST /api/v1/jobs/{id}/retry/`
- Creates a **new** job record with the same `task_name`, `args`, and `kwargs`.
- Links the new job to the old one via `parent_job_id`.
- Enqueues the task again.

## Monitoring & Debugging

1.  **Check Status**: Use the `GET /jobs/{id}/` API to poll for completion.
2.  **View Errors**: If a job fails, the `error` and `traceback` fields will contain detailed information.
3.  **Logs**: Check the `dramatiq` container logs for real-time execution logs.

## Best Practices

- **No Foreign Keys**: The `BackgroundJob` table does NOT have FKs to other tables (like `User` or `Animal`). This ensures the background system remains loosely coupled. Store IDs (e.g., `user_id`) in `args`/`kwargs` instead.
- **Idempotency**: Ensure your tasks are idempotent (can be run multiple times without side effects), as retries may occur.
- **Serialization**: Arguments passed to tasks must be JSON-serializable (strings, numbers, dicts, lists). Do not pass complex objects like SQLAlchemy models.
