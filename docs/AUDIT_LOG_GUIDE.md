# Audit Logging System Guide

This guide details the architecture and usage of the Audit Logging system in our FastAPI application. The system provides asynchronous, traceable logging of all critical business actions.

## Architecture

The audit system is designed to be **non-blocking** and **reliable**:

1.  **Service Layer**: The `AuditService` is used by domain services to log events.
2.  **Asynchronous Processing**: Events are published to a **Dramatiq** background queue (`write_audit_log` task).
3.  **Job Tracking**: Each audit log creation is tracked as a `BackgroundJob`.
4.  **Traceability**: A `trace_id` is propagated from the API request -> AuditService -> Background Job -> Audit Log, ensuring end-to-end traceability.

## Database Schema (`AuditLog`)

We store audit records in the `audit_logs` table:

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Unique Audit ID (PK) |
| `action` | String | Action performed (e.g., `CREATE`, `UPDATE`, `DELETE`) |
| `target_model` | String | Name of the model being modified (e.g., `Animal`) |
| `target_object_id` | String | ID of the object being modified |
| `actor_id` | String | ID of the user performing the action |
| `actor_email` | String | Email of the user performing the action |
| `changes` | JSON | Dictionary of changes (e.g., `{"field": "new_value"}`) |
| `ip_address` | String | IP address of the requester |
| `user_agent` | String | User Agent string of the requester |
| `trace_id` | String | **[NEW]** Trace ID for request tracking |
| `created_at` | DateTime | When the action occurred |

## Usage Guide

### 1. Inject AuditService

In your domain service, initialize the `AuditService`.

```python
from src.apps.audit.service import AuditService

class AnimalService:
    def __init__(self, repository: AnimalRepository):
        self.repository = repository
        self.audit_service = AuditService()
```

### 2. Capture Audit Context

In your router, use the helper to extract context from the request.

```python
# src/apps/animals/router.py
from src.apps.audit.utils import get_audit_context_from_request

@router.post("/")
async def create_animal(request: Request, payload: AnimalCreate, service: AnimalService = Depends(get_animal_service)):
    # Extract context (user_id, ip, user_agent, trace_id)
    audit_context = get_audit_context_from_request(request)
    
    return await service.create_animal(payload, audit_context)
```

### 3. Log Events

In your service method, call the appropriate log method.

```python
# src/apps/animals/service.py

async def create_animal(self, data: AnimalCreate, audit_context: AuditContext = None):
    animal = await self.repository.create(data)
    
    if audit_context:
        await self.audit_service.log_create(
            target_model="Animal",
            target_object_id=str(animal.id),
            changes=data.model_dump(),
            actor_id=audit_context.user_id,
            actor_email=audit_context.user_email,
            ip_address=audit_context.ip_address,
            user_agent=audit_context.user_agent,
            trace_id=audit_context.trace_id  # Pass trace_id!
        )
    
    return animal
```

## Traceability

The `trace_id` is the key to linking all parts of the system.

1.  **Request**: `X-Trace-ID` header or generated UUID.
2.  **Logs**: Application logs include `| <trace_id> |`.
3.  **Audit Log**: `audit_logs.trace_id` column.
4.  **Background Job**: `background_jobs.trace_id` column.

You can query all activities related to a single request using this ID:

```sql
-- Find the audit log
SELECT * FROM audit_logs WHERE trace_id = '123e4567-e89b-12d3-a456-426614174000';

-- Find the background job that created it
SELECT * FROM background_jobs WHERE trace_id = '123e4567-e89b-12d3-a456-426614174000';
```
