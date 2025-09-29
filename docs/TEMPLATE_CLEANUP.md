# Template Cleanup Guide

This guide helps you create a completely clean FastAPI template by removing all demo code (articles CRUD and background jobs) while keeping all the core infrastructure, logging, database setup, and development tools.

## What You'll Remove

- ✅ **Articles CRUD**: Complete article management system
- ✅ **Background Jobs**: Job processing and status tracking
- ✅ **Demo Tests**: All example tests
- ✅ **Demo Documentation**: Template-specific docs

## What You'll Keep

- ✅ **Core FastAPI Setup**: Application structure and configuration
- ✅ **Database Integration**: SQLAlchemy + Alembic setup
- ✅ **Logging System**: Request tracing and logging infrastructure
- ✅ **Development Tools**: Makefile, testing framework, code formatting
- ✅ **Docker Support**: Containerization setup
- ✅ **Environment Config**: Settings and configuration management

## Step-by-Step Cleanup

### 1. Remove Articles CRUD Code

#### Remove Article Model
```bash
rm app/models/article.py
```

#### Remove Article Repository
```bash
rm app/repositories/article.py
```

#### Remove Article Service
```bash
rm app/services/article.py
```

#### Remove Article Schemas
```bash
rm app/schemas/article.py
```

#### Remove Articles API
```bash
rm app/api/v1/articles.py
```

### 2. Remove Background Jobs Code

#### Remove Background Jobs API
```bash
rm app/api/v1/background_jobs.py
```

#### Remove Background Job Service
```bash
rm app/services/background_job_service.py
```

#### Remove Background Task Manager
```bash
rm app/core/background_tasks.py
```

### 3. Update API Router

Edit `app/api/urls.py` and remove all imports and routers:

```python
"""
Centralized URL configuration for the API - Django-style organization.
This file acts as the main URL dispatcher, similar to Django's urls.py.
"""

from fastapi import APIRouter

# Create the main API router
api_router = APIRouter()

# Add your new API routes here
# Example:
# from app.api.v1 import your_module
# api_router.include_router(your_module.router, prefix="/v1/your-module", tags=["your-module"])
```

### 4. Update Main Application

Edit `app/main.py` and remove background task manager:

```python
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.urls import api_router
from app.core.config import settings
from app.db.session import engine
from app.core.logging import setup_logging
from app.middleware.trace import TraceIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Setup logging configuration
    setup_logging()

    # Ensure engine is created during startup for early DB feedback
    async with engine.begin() as conn:  # noqa: F841
        pass
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

# Add trace ID middleware (should be first to capture all requests)
app.add_middleware(TraceIDMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_hosts,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")


@app.get("/healthz")
async def health_check(request: Request):
    """Health check endpoint with trace ID."""
    from app.middleware.trace import get_trace_id

    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "trace_id": get_trace_id(request),
        "timestamp": "2024-01-01T00:00:00Z"
    }
```

### 5. Remove Demo Tests

```bash
rm tests/test_background_jobs.py
```

### 6. Update Test Configuration

Edit `tests/conftest.py` and remove demo-specific fixtures:

```python
"""
Shared test fixtures and configuration.
"""

import pytest
from unittest.mock import AsyncMock, patch


@pytest.fixture
def mock_request():
    """Mock FastAPI Request object."""
    request = AsyncMock()
    request.state.trace_id = "test-trace-id-123"
    request.state.start_time = 1234567890.0
    return request


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch("app.core.logging.get_logger") as mock:
        mock_logger = AsyncMock()
        mock.return_value = mock_logger
        yield mock_logger


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test."""
    # This fixture runs automatically before each test
    # You can add any global test setup here
    pass
```

### 7. Remove Demo Documentation

```bash
rm docs/BACKGROUND_JOBS_API.md
rm docs/BACKGROUND_JOBS_CLEANUP.md
```

### 8. Update README.md

Remove or update these sections in `README.md`:

1. **Remove Section 19**: "Background Jobs API (Template Feature)"
2. **Update Section 20**: Remove background jobs references from documentation
3. **Update Quick Links**: Remove background jobs API references
4. **Update Examples**: Remove article and background job examples

### 9. Update Makefile

Remove background jobs test command from `Makefile`:

```makefile
# Remove this section
test-background:
	@echo "Running background job tests only..."
	@$(VENV_ACTIVATE) && PYTHONPATH=. pytest -m "background"
```

And update the help section to remove the background jobs test command.

### 10. Update pyproject.toml

Remove the background marker from pytest configuration:

```toml
# Remove "background: marks tests as background job tests" from markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "api: marks tests as API tests",
]
```

### 11. Clean Up Database Migrations

Remove article-related migrations:

```bash
# Check what migrations exist
ls alembic/versions/

# Remove article-related migration files
rm alembic/versions/*article*
rm alembic/versions/*init*
```

Create a new initial migration for your own models:

```bash
make makemigrations MSG="initial migration"
```

## Verification Steps

After cleanup, verify everything works:

### 1. Test Application Startup
```bash
make run
```

### 2. Check Health Endpoint
```bash
curl http://localhost:8000/healthz
```

Expected response:
```json
{
  "status": "healthy",
  "app_name": "FastAPI Vibe Coding",
  "trace_id": "some-uuid",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### 3. Check API Documentation
Visit `http://localhost:8000/docs` - you should see only the health endpoint.

### 4. Run Tests
```bash
make test
```

### 5. Check Logs
```bash
tail -f tmp/logs/app-*.log
```

## What You Have After Cleanup

After cleanup, you'll have a clean FastAPI template with:

### ✅ Core Infrastructure
- **FastAPI Application**: Properly configured with middleware
- **Database Setup**: SQLAlchemy + Alembic ready for your models
- **Logging System**: Request tracing and comprehensive logging
- **Environment Config**: Settings management with pydantic-settings
- **Health Check**: Basic health endpoint with trace ID

### ✅ Development Tools
- **Makefile**: Database migrations, testing, and development commands
- **Testing Framework**: pytest with async support and coverage
- **Code Formatting**: ruff for linting and formatting
- **Docker Support**: Ready for containerization

### ✅ Production Features
- **Request Tracing**: Trace ID middleware for request tracking
- **Structured Logging**: File and console logging with rotation
- **CORS Support**: Configurable CORS middleware
- **Environment-based Config**: Development/production settings

## Next Steps: Create Your Own CRUD

Now you can start building your own application:

### 1. Create Your Model
```python
# app/models/your_model.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class YourModel(Base):
    __tablename__ = "your_models"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 2. Create Migration
```bash
make makemigrations MSG="add your_model table"
make migrate
```

### 3. Create Schemas
```python
# app/schemas/your_model.py
from datetime import datetime
from pydantic import BaseModel, Field

class YourModelBase(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None

class YourModelCreate(YourModelBase):
    pass

class YourModelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None

class YourModelInDBBase(YourModelBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True

class YourModel(YourModelInDBBase):
    pass
```

### 4. Create Repository
```python
# app/repositories/your_model.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.your_model import YourModel

class YourModelRepository:
    async def create(self, db: AsyncSession, **kwargs) -> YourModel:
        your_model = YourModel(**kwargs)
        db.add(your_model)
        await db.commit()
        await db.refresh(your_model)
        return your_model

    async def get(self, db: AsyncSession, your_model_id: int) -> YourModel | None:
        result = await db.execute(select(YourModel).where(YourModel.id == your_model_id))
        return result.scalar_one_or_none()

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[YourModel]:
        result = await db.execute(select(YourModel).offset(skip).limit(limit))
        return result.scalars().all()

    async def update(self, db: AsyncSession, your_model_id: int, **kwargs) -> YourModel | None:
        await db.execute(
            update(YourModel).where(YourModel.id == your_model_id).values(**kwargs)
        )
        await db.commit()
        return await self.get(db, your_model_id)

    async def delete(self, db: AsyncSession, your_model_id: int) -> bool:
        result = await db.execute(delete(YourModel).where(YourModel.id == your_model_id))
        await db.commit()
        return result.rowcount > 0
```

### 5. Create Service
```python
# app/services/your_model.py
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.your_model import YourModel
from app.repositories.your_model import YourModelRepository
from app.schemas.your_model import YourModelCreate, YourModelUpdate

class YourModelService:
    def __init__(self):
        self.repository = YourModelRepository()

    async def create(self, db: AsyncSession, your_model_data: YourModelCreate) -> YourModel:
        return await self.repository.create(db, **your_model_data.dict())

    async def get(self, db: AsyncSession, your_model_id: int) -> YourModel | None:
        return await self.repository.get(db, your_model_id)

    async def list(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[YourModel]:
        return await self.repository.list(db, skip, limit)

    async def update(self, db: AsyncSession, your_model_id: int, your_model_data: YourModelUpdate) -> YourModel | None:
        update_data = your_model_data.dict(exclude_unset=True)
        if not update_data:
            return await self.repository.get(db, your_model_id)
        return await self.repository.update(db, your_model_id, **update_data)

    async def delete(self, db: AsyncSession, your_model_id: int) -> bool:
        return await self.repository.delete(db, your_model_id)
```

### 6. Create API Endpoints
```python
# app/api/v1/your_models.py
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.session import get_db_with_trace_id
from app.middleware.trace import get_trace_id
from app.schemas.your_model import YourModel, YourModelCreate, YourModelUpdate
from app.services.your_model import YourModelService

router = APIRouter()
service = YourModelService()

@router.post("/", response_model=YourModel, status_code=status.HTTP_201_CREATED)
async def create_your_model(
    request: Request,
    your_model_data: YourModelCreate,
    db: AsyncSession = Depends(get_db_with_trace_id)
):
    """Create a new your model."""
    logger = get_logger(request)
    logger.info(f"Creating your model: {your_model_data.name}")

    your_model = await service.create(db, your_model_data)
    logger.info(f"Created your model with ID: {your_model.id}")

    return your_model

@router.get("/", response_model=List[YourModel])
async def list_your_models(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_with_trace_id)
):
    """List your models."""
    logger = get_logger(request)
    logger.info(f"Listing your models: skip={skip}, limit={limit}")

    your_models = await service.list(db, skip, limit)
    logger.info(f"Found {len(your_models)} your models")

    return your_models

@router.get("/{your_model_id}", response_model=YourModel)
async def get_your_model(
    request: Request,
    your_model_id: int,
    db: AsyncSession = Depends(get_db_with_trace_id)
):
    """Get a specific your model."""
    logger = get_logger(request)
    logger.info(f"Getting your model: {your_model_id}")

    your_model = await service.get(db, your_model_id)
    if not your_model:
        logger.warning(f"Your model not found: {your_model_id}")
        raise HTTPException(status_code=404, detail="Your model not found")

    return your_model

@router.patch("/{your_model_id}", response_model=YourModel)
async def update_your_model(
    request: Request,
    your_model_id: int,
    your_model_data: YourModelUpdate,
    db: AsyncSession = Depends(get_db_with_trace_id)
):
    """Update a your model."""
    logger = get_logger(request)
    logger.info(f"Updating your model: {your_model_id}")

    your_model = await service.update(db, your_model_id, your_model_data)
    if not your_model:
        logger.warning(f"Your model not found: {your_model_id}")
        raise HTTPException(status_code=404, detail="Your model not found")

    logger.info(f"Updated your model: {your_model_id}")
    return your_model

@router.delete("/{your_model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_your_model(
    request: Request,
    your_model_id: int,
    db: AsyncSession = Depends(get_db_with_trace_id)
):
    """Delete a your model."""
    logger = get_logger(request)
    logger.info(f"Deleting your model: {your_model_id}")

    deleted = await service.delete(db, your_model_id)
    if not deleted:
        logger.warning(f"Your model not found: {your_model_id}")
        raise HTTPException(status_code=404, detail="Your model not found")

    logger.info(f"Deleted your model: {your_model_id}")
```

### 7. Add to API Router
```python
# app/api/urls.py
from app.api.v1 import your_models

api_router.include_router(your_models.router, prefix="/v1/your-models", tags=["your-models"])
```

### 8. Test Your API
```bash
# Start the server
make run

# Test your endpoints
curl -X POST "http://localhost:8000/api/v1/your-models/" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Model", "description": "Test Description"}'

curl "http://localhost:8000/api/v1/your-models/"
```

## Summary

After following this cleanup guide, you'll have:

- ✅ **Clean FastAPI template** without demo code
- ✅ **All infrastructure** (logging, database, testing, Docker)
- ✅ **Development tools** (Makefile, pytest, ruff)
- ✅ **Production features** (tracing, CORS, environment config)
- ✅ **Ready to build** your own CRUD application

You can now focus on building your own application features while having all the best practices and infrastructure already in place!
