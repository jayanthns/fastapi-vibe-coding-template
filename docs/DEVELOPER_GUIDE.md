# Developer Guide

## Project Structure

The project follows a modular "Vertical Slice" architecture within `src/apps/`. Each app contains its own models, schemas, services, and routers.

```
src/
├── apps/               # Domain-specific applications
│   ├── animals/        # Example app
│   │   ├── migrations/ # App-specific migrations
│   │   ├── models.py   # SQLAlchemy models
│   │   ├── schemas.py  # Pydantic schemas (Input/Output)
│   │   ├── service.py  # Business logic
│   │   ├── router.py   # API endpoints
│   │   └── repository.py # Database access
│   └── users/          # User management
├── core/               # Core functionality (Config, Logging, Auth)
├── db/                 # Database session & base classes
├── middleware/         # Custom middleware
└── main.py             # Application entry point
```

## Core Concepts

### 1. Models (SQLAlchemy)

Models are defined in `models.py` and inherit from `UUIDModel` (providing `id`, `created_at`, `updated_at`).

```python
from src.core.models import UUIDModel
from sqlalchemy import Column, String

class Animal(UUIDModel):
    __tablename__ = "animals"
    
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
```

### 2. Schemas (Pydantic)

Schemas define the API contract (Input and Output). Defined in `schemas.py`.

```python
from pydantic import BaseModel, ConfigDict
from uuid import UUID

class AnimalBase(BaseModel):
    name: str
    species: str

class AnimalCreate(AnimalBase):
    pass

class AnimalResponse(AnimalBase):
    id: UUID
    
    model_config = ConfigDict(from_attributes=True)
```

### 3. Services

Business logic resides in `service.py`. Services should be stateless and handle data manipulation.

```python
class AnimalService:
    @staticmethod
    async def create_animal(session: AsyncSession, data: AnimalCreate) -> Animal:
        animal = Animal(**data.model_dump())
        session.add(animal)
        await session.commit()
        return animal
```

### 4. Routers (API Endpoints)

Routers are defined in `router.py` and use `APIRouter`.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.session import get_db

router = APIRouter()

@router.post("/", response_model=APIResponse[AnimalResponse])
async def create_animal(
    payload: AnimalCreate,
    session: AsyncSession = Depends(get_db)
):
    animal = await AnimalService.create_animal(session, payload)
    return APIResponse(data=animal)
```

## Database Migrations (Alembic)

We use **Alembic** for migrations, with a **per-app migration strategy**.

### Creating Migrations

When you modify a model in an app (e.g., `src/apps/animals/models.py`), generate a migration for that app:

```bash
# Auto-generate migration for 'animals' app
alembic revision --autogenerate -m "add_age_field" --version-path src/apps/animals/migrations
```

**Note**: You must specify `--version-path` to save the migration in the correct app directory.

### Applying Migrations

```bash
make migrate
# or
alembic upgrade head
```

## Dependency Injection

FastAPI's dependency injection system is used for:
- **Database Sessions**: `session: AsyncSession = Depends(get_db)`
- **Authentication**: `user: User = Depends(get_current_user)`
- **Services**: Can be injected if they have dependencies.

## Error Handling

Use `src.core.exceptions` for consistent error responses.

```python
from src.core.exceptions import NotFoundException

if not animal:
    raise NotFoundException("Animal not found")
```

This will automatically return a 404 JSON response with the standard error format.

## Logging

Use the configured logger:

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Creating animal", extra={"animal_name": name})
```

Logs are structured (JSON in production) and include correlation IDs for tracing.

## Background Jobs (Dramatiq)

We use **Dramatiq** with **Redis** for reliable background task processing.

### Quick Start

1.  **Define a Task**: Create a `tasks.py` in your app.
    ```python
    import dramatiq
    import asyncio
    from src.apps.my_app.service import MyService

    @dramatiq.actor
    def my_background_task(arg1, arg2):
        asyncio.run(MyService.do_work(arg1, arg2))
    ```

2.  **Enqueue a Task**: Call `.send()` on the actor.
    ```python
    my_background_task.send("value1", "value2")
    ```

3.  **Run the Worker**:
    ```bash
    dramatiq src.worker --processes 1 --threads 1
    ```

For detailed architecture, monitoring, and best practices, see the [Background Jobs Guide](BACKGROUND_JOBS_GUIDE.md).
