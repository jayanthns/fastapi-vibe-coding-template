# Developer Guide

## Welcome to the Team! 👋

If you are a new developer (fresher or junior) joining this project, this guide is specifically designed for you. Our goal is to help you understand not just _how_ to write code here, but _why_ we do things the way we do.

This project is built on **FastAPI**, a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints.

### A Brief History of FastAPI

FastAPI was created by **Sebastián Ramírez** (tiangolo) and first released in **December 2018**. It was designed to solve common pain points in Python web development:

- **Speed**: It is one of the fastest Python frameworks available, on par with NodeJS and Go (thanks to Starlette and Pydantic).
- **Developer Experience**: It heavily utilizes Python type hints to provide great editor support (autocompletion, error checks).
- **Standards-based**: It is based on (and fully compatible with) open standards for APIs: OpenAPI (formerly Swagger) and JSON Schema.

Since its release, it has gained massive popularity due to its ease of use, performance, and robust documentation.

## Project Structure

The project follows a modular "Vertical Slice" architecture within `src/apps/`. Each app contains its own models, schemas, services, and routers.

```text
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

1. **Define a Task**: Create a `tasks.py` in your app.

    ```python
    import dramatiq
    import asyncio
    from src.apps.my_app.service import MyService

    @dramatiq.actor
    def my_background_task(arg1, arg2):
        asyncio.run(MyService.do_work(arg1, arg2))
    ```

2. **Enqueue a Task**: Call `.send()` on the actor.

    ```python
    my_background_task.send("value1", "value2")
    ```

3. **Run the Worker**:

    ```bash
    dramatiq src.worker --processes 1 --threads 1
    ```

For detailed architecture, monitoring, and best practices, see the [Background Jobs Guide](BACKGROUND_JOBS_GUIDE.md).

## Contributing

We welcome contributions from everyone! Here is how you can contribute effectively:

### 1. Getting Started

- **Fork the repository**: Create your own copy of the project.
- **Clone the repository**: Download it to your local machine.
- **Set up the environment**: Follow the [Setup Guide](SETUP.md).

### 2. Development Workflow

1. **Create a Branch**: Always create a new branch for your feature or bugfix.

    ```bash
    git checkout -b feature/my-new-feature
    ```

2. **Write Code**: Follow the patterns described in this guide.
3. **Write Tests**: Ensure your code is covered by tests. Run `make pytest` to verify.
4. **Lint & Format**: Run `make static-tests` to ensure code quality.

### 3. Submitting Changes

1. **Commit**: Write clear, descriptive commit messages.
2. **Push**: Push your branch to your fork.
3. **Pull Request (PR)**: Open a PR against the `main` branch.
    - Describe your changes in detail.
    - Link to any relevant issues.
    - Wait for code review and address feedback.

### Code Review Process

- A senior developer will review your code.
- Be open to feedback and suggestions.
- Once approved, your code will be merged!
