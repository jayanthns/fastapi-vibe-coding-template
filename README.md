# FastAPI Vibe Coding — Local Development

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.116.x-009688?logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-Server-000000?logo=uvicorn&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-Migrations-2C3E50) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791?logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-Local_DB-003B57?logo=sqlite&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white) ![uv](https://img.shields.io/badge/uv-Dependencies-FF6600) ![Ruff](https://img.shields.io/badge/Ruff-Linting-FFD43B) ![pytest](https://img.shields.io/badge/pytest-Tests-0A9EDC?logo=pytest&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-blue)

This project is a production-ready FastAPI skeleton with SQLAlchemy (async), Alembic, and an Article CRUD. This doc covers local setup, environment values, dependency management with uv, database migrations, and how to run the app.

> **📝 Template Options**: This repository includes demo features (articles CRUD and background jobs) that can be removed if you want a completely clean template. See [Template Cleanup](docs/TEMPLATE_CLEANUP.md) for instructions to remove all demo code and start fresh.

## Table of contents

- [FastAPI Vibe Coding — Local Development](#fastapi-vibe-coding--local-development)
  - [Table of contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [1) Create and activate a virtualenv](#1-create-and-activate-a-virtualenv)
  - [2) Environment variables (.env)](#2-environment-variables-env)
  - [3) Dependencies with uv (recommended)](#3-dependencies-with-uv-recommended)
  - [4) Database migrations (Alembic)](#4-database-migrations-alembic)
    - [Using Makefile Commands (Recommended - Django-style)](#using-makefile-commands-recommended---django-style)
      - [**Create Migrations**](#create-migrations)
      - [**Apply Migrations**](#apply-migrations)
      - [**Migration Management**](#migration-management)
      - [**Database Management**](#database-management)
      - [**Development Setup**](#development-setup)
    - [Using Alembic Directly (Alternative)](#using-alembic-directly-alternative)
  - [5) Run the application](#5-run-the-application)
  - [6) Quick project structure](#6-quick-project-structure)
  - [7) Tests (optional)](#7-tests-optional)
    - [Running Tests](#running-tests)
    - [Test Database Configuration](#test-database-configuration)
      - [Environment Variables for Testing](#environment-variables-for-testing)
      - [Test Database Setup](#test-database-setup)
      - [Manual Test Database Setup](#manual-test-database-setup)
      - [Test Isolation](#test-isolation)
  - [8) Makefile commands](#8-makefile-commands)
    - [Local app](#local-app)
    - [Python virtualenv](#python-virtualenv)
    - [Using uv for dependencies (faster)](#using-uv-for-dependencies-faster)
    - [Security auditing](#security-auditing)
    - [Database migrations (Django-style)](#database-migrations-django-style)
    - [Test database management](#test-database-management)
    - [Docker helpers](#docker-helpers)
  - [10) Run with Docker](#10-run-with-docker)
  - [11) Debug/start scripts](#11-debugstart-scripts)
  - [12) Production deployment](#12-production-deployment)
  - [13) VS Code tasks](#13-vs-code-tasks)
  - [14) Testing guidance](#14-testing-guidance)
    - [Test Database Strategy](#test-database-strategy)
    - [Testing Patterns](#testing-patterns)
    - [Test Structure](#test-structure)
    - [Running Tests](#running-tests-1)
  - [15) Alembic tips](#15-alembic-tips)
  - [16) Security notes](#16-security-notes)
  - [17) Architecture overview](#17-architecture-overview)
  - [18) Request tracing and logging](#18-request-tracing-and-logging)
    - [Trace ID System](#trace-id-system)
    - [Request-Level Logging](#request-level-logging)
      - [Log Format](#log-format)
      - [Usage in API Endpoints](#usage-in-api-endpoints)
      - [Usage in Background/Async Tasks](#usage-in-backgroundasync-tasks)
      - [Usage in Services and Repositories](#usage-in-services-and-repositories)
      - [Response Headers](#response-headers)
      - [API Response Format](#api-response-format)
      - [Configuration](#configuration)
      - [Architecture](#architecture)
      - [File Logging](#file-logging)
      - [Environment-Based SQL Logging](#environment-based-sql-logging)
      - [Key Benefits](#key-benefits)
  - [19) Industry-Standard Caching with Automatic Fallback](#19-industry-standard-caching-with-automatic-fallback)
    - [Key Features](#key-features)
    - [Quick Start](#quick-start)
    - [How It Works](#how-it-works)
    - [Basic Usage](#basic-usage)
    - [Health Checks](#health-checks)
    - [Startup Behavior](#startup-behavior)
    - [Documentation](#documentation)
  - [20) Background Jobs API (Template Feature)](#20-background-jobs-api-template-feature)
    - [Features](#features)
    - [API Endpoints](#api-endpoints)
    - [Usage Example](#usage-example)
    - [Testing](#testing)
    - [Background Jobs Code Cleanup](#background-jobs-code-cleanup)
  - [21) Documentation](#21-documentation)
    - [📚 Available Documentation](#-available-documentation)
    - [🔗 Quick Links](#-quick-links)
  - [22) API docs \& versioning](#22-api-docs--versioning)
  - [23) VS Code mandatory extensions](#23-vs-code-mandatory-extensions)
  - [9) How to extend this template (step‑by‑step guide)](#9-how-to-extend-this-template-stepbystep-guide)
    - [1) Define the database model](#1-define-the-database-model)
    - [2) Create Pydantic schemas](#2-create-pydantic-schemas)
    - [3) Repository (data access)](#3-repository-data-access)
    - [4) Service (business logic)](#4-service-business-logic)
    - [5) API router](#5-api-router)
    - [6) Database migration](#6-database-migration)
    - [7) Tests (outline)](#7-tests-outline)
    - [8) Docs and discoverability](#8-docs-and-discoverability)

## Prerequisites

- Python 3.10+
- A virtualenv for isolation
- uv (recommended) for compiling dependency lockfiles
  - Install: `pip install uv` or see uv docs

## 1) Create and activate a virtualenv

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -U pip
```

## 2) Environment variables (.env)

Create a `.env` in the project root. A starter file is provided as `.env_copy`.

Quick start:

```bash
cp .env_copy .env
# then edit .env as needed
```

Minimum useful values for local dev:

```bash
# Database URL (defaults to SQLite async)
DATABASE_URL=sqlite+aiosqlite:///./app.db

# Runtime environment
ENVIRONMENT=development

# Framework debug mode
DEBUG=true

# CORS origins (comma-separated). For local dev you can use *
BACKEND_CORS_ORIGINS=*

# Optional: Uvicorn overrides (the scripts have sane defaults)
# HOST=0.0.0.0
# PORT=8000
# WORKERS=1
# RELOAD=true
```

Notes:

- To use Postgres (async), set `DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/dbname` and install `asyncpg`.
- If you run Postgres via docker-compose, these vars are read by compose for the DB container: `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_NAME`. The app in Docker uses `DATABASE_HOST` from compose (defaults to the DB service name) while local runs can leave `DATABASE_HOST=localhost`.
- Optional Redis (if you enable the service): `REDIS_HOST`, `REDIS_PORT`, `REDIS_HOST_AND_PORT`.

## 3) Dependencies with uv (recommended)

This repo keeps human-authored input files in `requirements_raw/` and expects compiled lockfiles in `requirements/`.

- Compile production requirements:

```bash
uv pip compile requirements_raw/requirements.in -o requirements/requirements.txt
```

- Compile local/dev requirements:

```bash
uv pip compile requirements_raw/local_requirements.in -o requirements/local_requirements.txt
```

- Install local/dev dependencies into your venv:

```bash
pip install -r requirements/local_requirements.txt
```

Alternatively, you can install from the package metadata for editable dev:

```bash
pip install -e '.[dev]'
```

## 4) Database migrations (Alembic)

### Using Makefile Commands (Recommended - Django-style)

The project includes Django-style migration commands via Makefile for easier database management:

#### **Create Migrations**

```bash
# Create a new migration (like Django makemigrations)
make makemigrations MSG='add user table'
make makemigrations MSG='update article schema'
```

#### **Apply Migrations**

```bash
# Apply all pending migrations (like Django migrate)
make migrate
```

#### **Migration Management**

```bash
# Show migration history
make migrate-history

# Show current migration status
make migrate-current

# Show latest migration details
make migrate-show

# Downgrade one migration
make migrate-downgrade

# Reset all migrations (development only!)
make migrate-reset
```

#### **Database Management**

```bash
# Initialize database with all migrations
make db-init

# Reset database completely (development only!)
make db-reset

# Initialize database
make db-init
```

#### **Development Setup**

```bash
# Complete development environment setup
make dev-setup

# Reset development database
make dev-reset

# Get help with all available commands
make help
```

### Using Alembic Directly (Alternative)

If you prefer using Alembic commands directly:

- Create an initial migration (if not present) or a new one after model changes:

```bash
alembic revision --autogenerate -m "init"    # or your message
```

- Apply migrations:

```bash
alembic upgrade head
```

- Downgrade (optional):

```bash
alembic downgrade -1
```

Troubleshooting:

- If you see `ModuleNotFoundError: app`, Alembic might not see the project root. The provided `alembic/env.py` adjusts `sys.path`; ensure you run commands from the repo root.
- If you see an error about `greenlet`, install it: `pip install greenlet`.

## 5) Run the application

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- Health check: GET http://localhost:8000/healthz
- Articles CRUD: `/api/v1/articles`

## 6) Quick project structure

```sh
app/
  api/v1/articles.py
  core/config.py
  db/session.py
  models/{__init__.py, article.py}
  repositories/article.py
  schemas/article.py
  services/article.py
  main.py
alembic/
  env.py
  versions/
requirements_raw/
  requirements.in
  local_requirements.in
requirements/
  requirements.txt                # compiled by uv
  local_requirements.txt          # compiled by uv
```

## 7) Tests (optional)

### Running Tests

```bash
# Run all tests
pytest -q

# Run with coverage
pytest --cov

# Run specific test file
pytest tests/test_api/test_database_pings.py -v
```

### Test Database Configuration

The test suite uses a **separate PostgreSQL test database** to ensure test isolation and prevent data pollution. The test database is automatically configured using environment variables:

- **Test Database Name**: `{DATABASE_NAME}_test` (e.g., `fastapi_vibe_coding_test`)
- **Credentials**: Uses the same database credentials as your main database
- **Auto-setup**: The test database is created automatically when running tests

#### Environment Variables for Testing

The test configuration reads from these environment variables (with defaults):

```bash
DATABASE_HOST=localhost          # Database host
DATABASE_PORT=5432              # Database port
DATABASE_USERNAME=postgres      # Database username
DATABASE_PASSWORD=postgres      # Database password
DATABASE_NAME=fastapi_vibe_coding  # Base database name
```

#### Test Database Setup

Before running tests, ensure your PostgreSQL server is running and accessible. The test suite will:

1. **Create test database** if it doesn't exist
2. **Run migrations** to set up the schema
3. **Execute tests** in isolation
4. **Clean up** after completion

#### Manual Test Database Setup

If you need to manually create the test database:

```bash
# Run the setup script
python scripts/setup_test_db.py

# Or create manually via psql
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE fastapi_vibe_coding_test;"
```

#### Test Isolation

- Each test run uses a fresh test database
- Tests don't interfere with your development database
- No data pollution between test runs
- Fast execution with dedicated test environment


## 8) Makefile commands

Use these shortcuts to manage your environment, dependencies, and Docker. Run from the project root.

### Local app

- **make run**: Start the dev server with reload using your local venv.
  - Example: `make run` then open http://localhost:8000

### Python virtualenv

- **make venv_init**: Create `venv/` and install base tooling (uv, pip-tools, wheel).
  - Example: `make venv_init`
- **make install-deps**: Install from compiled lockfiles `requirements/requirements.txt` and `requirements/local_requirements.txt`.
  - Example: `make install-deps`
- **make update-deps**: Recompile both lockfiles with pip-tools (backtracking resolver), then install.
  - Example: `make update-deps`
- **make update-package**: Alias to run both `update-deps` and `install-deps`.

### Using uv for dependencies (faster)

- **make uv-venv-init**: Install uv and create a uv-managed venv; install base tooling.
  - Example: `make uv-venv-init`
- **make uv-update-deps**: Recompile lockfiles using `uv pip compile`.
  - Example: `make uv-update-deps`
- **make uv-install-deps**: Install dependencies using `uv pip install`.
  - Example: `make uv-install-deps`
- **make uv-update-package**: Alias to run both `uv-update-deps` and `uv-install-deps`.

### Security auditing

- **make pip-audit-prod**: Audit production lockfile only.
- **make pip-audit-all**: Audit both prod and local/dev lockfiles.
- **make uv-pip-audit-prod**: Same as above using `uv pip-audit`.
- **make uv-pip-audit-all**: Audit both lockfiles via `uv pip-audit`.

### Database migrations (Django-style)

- **make makemigrations MSG='message'**: Create new migration (like Django makemigrations).
  - Example: `make makemigrations MSG='add user table'`
- **make migrate**: Apply all pending migrations (like Django migrate).
  - Example: `make migrate`
- **make migrate-history**: Show migration history.
- **make migrate-current**: Show current migration status.
- **make migrate-show**: Show latest migration details.
- **make migrate-downgrade**: Downgrade one migration.
- **make migrate-reset**: Reset all migrations (development only!).

### Test database management

- **make test-db-setup**: Create test database for running tests.
  - Example: `make test-db-setup`
- **make test-db-drop**: Drop test database (cleanup).
  - Example: `make test-db-drop`
- **make db-init**: Initialize database with all migrations.
- **make db-reset**: Reset database completely (development only!).
- **make dev-setup**: Complete development environment setup.
- **make dev-reset**: Reset development database.
- **make help**: Show all available commands with examples.

### Docker helpers

- **make d-up**: `docker compose up -d` (all services).
- **make d-down**: `docker compose down`.
- **make d-db**: Start only the Postgres service.
- **make d-app**: Start only the app service.
- **make d-logs**: Follow logs for all services.
- **make d-logs-app**: Follow logs for just the app service.

Notes:

- Ensure `.env` exists before using Docker targets that rely on env vars.
- If you prefer running the app inside Docker, expose `8000` and hit `http://localhost:8000`.

## 10) Run with Docker

Quick start:

```bash
docker compose build
docker compose up -d
docker compose logs -f
```

- App: http://localhost:8000 (Docs at `/docs`, health at `/healthz`)
- Stop: `docker compose down`

Common issues:
- If you can’t reach the app, ensure Uvicorn binds to `0.0.0.0` (already set in Dockerfile).
- Port in use: another process uses 8000; stop it or change host port mapping in `docker-compose.yaml`.
- Env: ensure `.env` exists; see `.env_copy` for a template.

## 11) Debug/start scripts

Use the helper script to run Uvicorn with sensible defaults from any path:

```bash
# from repo root
./deploy/uvicorn_start.sh

# or
cd deploy
./uvicorn_start.sh
```

Overrides (via env): `HOST`, `PORT`, `WORKERS`, `RELOAD`, `APP_MODULE`.

## 12) Production deployment

- Example command (no reload):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

Notes:
- Behind a reverse proxy (e.g., NGINX) terminate TLS at the proxy and forward to Uvicorn.
- Health endpoints: expose `/healthz` for liveness/readiness.
- Sizing: start with workers = CPU cores or cores*2 for IO‑bound workloads; profile and adjust.

## 13) VS Code tasks

This repo includes `/.vscode/tasks.json` with common tasks (run server, tests, Docker, etc.).
- Open the Command Palette → “Run Task” → pick a task.
- Adjust or add tasks in `.vscode/tasks.json` as needed for your workflow.

## 14) Testing guidance

### Test Database Strategy

- **Separate Test Database**: Uses `{DATABASE_NAME}_test` PostgreSQL database for complete isolation
- **Environment-based Configuration**: Test database credentials read from environment variables
- **Automatic Setup**: Test database created and migrated automatically before test execution
- **No Data Pollution**: Tests never touch your development database

### Testing Patterns

- **API Tests**: Use `pytest` with `httpx.AsyncClient` for async API endpoint testing
- **Database Tests**: Use the provided test database fixture for database operations
- **Unit Tests**: Keep service layer tests separate from API/integration tests
- **Test Isolation**: Each test run gets a fresh database schema

### Test Structure

```
tests/
├── conftest.py              # Test database configuration
├── test_api/                # API endpoint tests
│   ├── test_database_pings.py
│   └── test_articles.py
├── test_utils/              # Utility function tests
│   └── test_security.py
└── test_services/           # Service layer tests
    └── test_article.py
```

### Running Tests

```bash
# All tests with test database
pytest

# Specific test categories
pytest tests/test_api/        # API tests only
pytest tests/test_utils/      # Utility tests only

# With coverage reporting
pytest --cov=app --cov-report=html
```

## 15) Alembic tips

- After model changes: `alembic revision --autogenerate -m "message"` → `alembic upgrade head`.
- Multiple heads: resolve with `alembic merge <rev1> <rev2>`.
- Safe rollback: write clear downgrade steps; avoid destructive downgrades on shared envs.

## 16) Security notes

- Do not commit secrets. Use `.env_copy` as a template and keep your `.env` local.
- Rotate credentials regularly; prefer per‑developer credentials for local DBs/services.
- Restrict CORS in non‑dev envs; don’t leave `*` in production.

## 17) Architecture overview

See `ARCHITECTURE.md` for layering and patterns. High‑level:

- Centralized URL configuration (`app/api/urls.py`) manages all API routing.
- Routers (HTTP) → Services (business rules) → Repositories (data access) → DB models.
- Schemas define request/response contracts and enforce output shapes.

## 18) Request tracing and logging

This application includes a comprehensive request-level tracing and logging system that automatically tracks requests with unique trace IDs and provides structured logging throughout the request lifecycle.

### Trace ID System

Every request receives a unique `trace_id` that is:

- Generated automatically by the `TraceIDMiddleware`
- Available throughout the entire request lifecycle
- Included in all log messages
- Returned in API responses and response headers
- Passable to background/async tasks

### Request-Level Logging

The system provides request-scoped loggers that automatically include the trace_id in all log messages, similar to Django's request-level logging pattern.

#### Log Format

```
2024-01-01 10:00:00,123 | INFO     | 550e8400-e29b-41d4-a716-446655440000 | app.request | Request started: POST /api/v1/articles
2024-01-01 10:00:00,124 | INFO     | 550e8400-e29b-41d4-a716-446655440000 | app.request | Creating article: My New Article
2024-01-01 10:00:00,125 | INFO     | 550e8400-e29b-41d4-a716-446655440000 | app.request | Article created successfully with ID: 1
2024-01-01 10:00:00,126 | INFO     | 550e8400-e29b-41d4-a716-446655440000 | app.request | Request completed: POST /api/v1/articles - Status: 201 - Time: 0.0234s
```

#### Usage in API Endpoints

```python
from fastapi import Request
from app.middleware.trace import get_request_logger, get_trace_id

@router.post("/articles")
async def create_article(payload: ArticleCreate, request: Request, db=Depends(get_db)):
    # Get request-scoped logger with trace_id
    logger = get_request_logger(request)
    logger.info(f"Creating article: {payload.title}")

    # Your business logic here
    article = await article_service.create_article(db, payload)

    logger.info(f"Article created successfully with ID: {article.id}")

    # Return response with trace_id
    return APIResponse.create_with_trace_id(
        data=article,
        message="Article created successfully",
        status_code=201,
        trace_id=get_trace_id(request)
    )
```

#### Usage in Background/Async Tasks

```python
from app.middleware.logging import get_logger_for_trace_id

async def process_article_async(article_id: int, trace_id: str) -> None:
    # Create logger with the request's trace_id
    logger = get_logger_for_trace_id(trace_id, "app.background")

    logger.info(f"Starting background processing for article {article_id}")

    try:
        # Your background work here
        await some_async_operation()
        logger.info(f"Background processing completed for article {article_id}")
    except Exception as e:
        logger.error(f"Background processing failed: {str(e)}")
        raise

# In your endpoint:
@router.post("/articles/{article_id}/process")
async def process_article(article_id: int, request: Request, background_tasks: BackgroundTasks):
    logger = get_request_logger(request)
    trace_id = get_trace_id(request)

    logger.info(f"Starting background processing for article {article_id}")

    # Pass trace_id to background task
    background_tasks.add_task(process_article_async, article_id, trace_id)

    return {"message": "Processing started", "trace_id": trace_id}
```

#### Usage in Services and Repositories

```python
# In services
async def create_article_service(db, payload, trace_id: str):
    logger = get_logger_for_trace_id(trace_id, "app.service")
    logger.info(f"Creating article: {payload.title}")

    # Your business logic here
    article = await article_repository.create(db, **payload.dict())

    logger.info(f"Article created with ID: {article.id}")
    return article

# In repositories
async def create_article_repository(db, title: str, content: str, trace_id: str):
    logger = get_logger_for_trace_id(trace_id, "app.repository")
    logger.info(f"Creating article in database: {title}")

    # Your database operations here
    article = Article(title=title, content=content)
    db.add(article)
    await db.commit()

    logger.info(f"Article saved to database with ID: {article.id}")
    return article
```

#### Response Headers

The system automatically adds these headers to all responses:

- `X-Trace-ID`: The unique trace ID for the request
- `X-Response-Time`: Request processing time in seconds

#### API Response Format

All API responses include the trace_id in the response body:

```json
{
  "success": true,
  "message": "Article created successfully",
  "status_code": 201,
  "data": {
    "id": 1,
    "title": "My Article",
    "content": "Article content...",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
  },
  "error": null,
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2024-01-01T10:00:00Z"
}
```

#### Configuration

Logging is automatically configured during application startup. The system uses:

- **Console output** with structured formatting
- **File output** with daily rotation and different log types
- **INFO level** by default (configurable)
- **Custom formatter** that includes trace_id in all messages
- **Request lifecycle logging** (automatic start/completion/error logging)
- **SQLAlchemy logging** (only enabled in development environment)

#### Architecture

The logging system follows **Single Responsibility Principle (SRP)**:

- **`app/config/logging.py`**: Logging configuration and setup
- **`app/utils/logging.py`**: Logging utilities and helper classes
- **`app/utils/sqlalchemy_logging.py`**: SQLAlchemy logging integration
- **`app/middleware/trace.py`**: Request/response middleware only

#### File Logging

The system automatically creates log files in `tmp/logs/` with a **simplified 2-file structure**:

- **`app-YYYY-MM-DD.log`**: All application logs (requests, business logic, errors, access)
- **`sqlalchemy-YYYY-MM-DD.log`**: Database query logs (development only)

**Why Only 2 Files?**
- **Less confusion**: Everything in one place with trace_id for correlation
- **Easier monitoring**: Only 2 files to watch instead of 4
- **Better context**: Related logs stay together (request + error + business logic)
- **Simpler maintenance**: Fewer files to manage and rotate

**Log File Features:**
- **Daily rotation**: New log file each day
- **Size-based rotation**: 10MB max per file, keeps 5 backup files
- **UTF-8 encoding**: Proper character support
- **Structured format**: Consistent trace_id and timestamp format
- **Clear prefixes**: "ACCESS:", "ERROR:" prefixes for easy filtering

**Log File Location:**
```
tmp/
├── .gitkeep          # Git-tracked file
└── logs/             # Git-ignored directory
    ├── app-2024-09-29.log        # All application logs
    └── sqlalchemy-2024-09-29.log # Database queries (dev only)
```

**Example App Log Content:**
```
2024-09-29 20:06:15,123 | INFO     | 32471740-1d73-4cc7-a437-a85083301776 | app.request | Request started: GET /api/v1/articles/
2024-09-29 20:06:15,124 | INFO     | 32471740-1d73-4cc7-a437-a85083301776 | app.request | Listing articles - skip: 0, limit: 100
2024-09-29 20:06:15,125 | INFO     | 32471740-1d73-4cc7-a437-a85083301776 | app.access | ACCESS: GET /api/v1/articles/ - 200 - 0.0242s
2024-09-29 20:06:15,126 | INFO     | 32471740-1d73-4cc7-a437-a85083301776 | app.request | Request completed: GET /api/v1/articles/ - Status: 200 - Time: 0.0242s
```

#### Environment-Based SQL Logging

SQLAlchemy query logging is automatically enabled/disabled based on the environment:

- **Development** (`ENVIRONMENT=development`): SQL queries are logged with trace_id
- **Production/Staging** (`ENVIRONMENT=production` or other): No SQL logging to avoid performance impact

This is controlled by the `ENVIRONMENT` setting in your `.env` file:

```bash
# .env
ENVIRONMENT=development  # Enables SQL logging
# ENVIRONMENT=production  # Disables SQL logging
```

#### Key Benefits

1. **Request Tracing**: Every log message includes the request's trace_id
2. **Lifecycle Logging**: Automatic request start/completion/error logging
3. **Background Support**: Trace_id can be passed to async tasks
4. **Django-Style**: Familiar request-level logging pattern
5. **Performance Tracking**: Built-in request timing
6. **Error Tracking**: Automatic exception logging with trace_id
7. **Flexible**: Works in endpoints, services, repositories, and background tasks

## 19) Industry-Standard Caching with Automatic Fallback

This application includes an industry-standard caching system with automatic fallback from Redis to memory cache for high availability. The system follows Netflix/Uber patterns for cache resilience.

### Key Features

- **🔄 Automatic Fallback**: Seamlessly switches from Redis to memory cache when Redis is unavailable
- **🔄 Automatic Recovery**: Switches back to Redis when it recovers
- **⚡ Zero Downtime**: Application continues working even when Redis fails
- **📊 Comprehensive Monitoring**: Detailed logging and statistics for operational visibility
- **🏗️ Industry Standard**: Follows best practices for high-availability systems

### Quick Start

Configure caching using environment variables:

```bash
# .env
# Set to 1 to use Redis with fallback, 0 to use memory cache only
USE_REDIS=1

# Redis Configuration (used as primary cache when USE_REDIS=1)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis

# Or use full URL
REDIS_URL=redis://:password@localhost:6379/0
```

### How It Works

1. **Primary Cache**: Tries Redis first for all operations
2. **Health Monitoring**: Checks Redis every 30 seconds when using fallback
3. **Automatic Fallback**: Switches to memory cache when Redis fails
4. **Automatic Recovery**: Switches back to Redis when it recovers
5. **Transparent Operation**: Your code works unchanged

### Basic Usage

```python
from app.core.cache import cache

# Async methods (use in FastAPI endpoints) - works with Redis or fallback automatically
await cache.set("key", "value", expire=300)
value = await cache.get("key")

# Sync methods (use in regular functions)
cache.set_sync("key", "value", expire=300)
value = cache.get_sync("key")

# Cache manager (automatic serialization)
await cache.set("user:123", {"name": "John"}, expire=600)
user_data = await cache.get("user:123")

# Check which cache is currently active
cache_type = cache.service_type  # "redis" or "memory"
is_fallback = cache.is_fallback_active  # True if using fallback
```

### Health Checks

Test cache connectivity and get information:

```bash
# Test cache ping (works with both Redis and fallback)
curl "http://localhost:8000/api/v1/pings/cache"

# Get cache info (shows current cache type and fallback status)
curl "http://localhost:8000/api/v1/pings/cache/info"

# List cache keys (works with both Redis and memory cache)
curl "http://localhost:8000/api/v1/pings/cache/keys"
```

### Startup Behavior

- **With Redis Available**: `✅ Redis cache connection established successfully`
- **With Redis Unavailable**: `✅ Memory cache (fallback) connection established successfully`
- **When Redis Recovers**: `Redis recovered, switched back to primary cache`

### Documentation

For comprehensive caching usage examples, fallback patterns, monitoring, and advanced features, see:

**[📚 Redis Caching Guide](docs/REDIS_CACHING.md)**

## 20) Background Jobs API (Template Feature)

The project includes a complete background jobs system with status tracking and caching.

> **📝 Template Note**: This is a demo/template feature. If you don't need background job functionality, see [Background Jobs Code Cleanup](#background-jobs-code-cleanup) section below for instructions on how to remove it.

### Features
- ✅ Asynchronous job processing
- ✅ Status tracking with in-memory caching
- ✅ Trace ID integration
- ✅ RESTful API endpoints
- ✅ Comprehensive testing

### API Endpoints
- `POST /api/v1/jobs/process-article` - Create article processing job
- `POST /api/v1/jobs/send-email` - Create email sending job
- `POST /api/v1/jobs/generate-report` - Create report generation job
- `GET /api/v1/jobs/{job_id}/status` - Get job status
- `DELETE /api/v1/jobs/{job_id}` - Cancel job
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/all` - List all jobs (dedicated endpoint)

### Usage Example
```bash
# Create a background job
curl -X POST "http://localhost:8000/api/v1/jobs/process-article?article_id=123&processing_time=5"

# Check job status
curl "http://localhost:8000/api/v1/jobs/{job_id}/status"

# List all jobs
curl "http://localhost:8000/api/v1/jobs"
```

### Testing
```bash
# Run background job tests
make test-background

# Run all tests
make test
```

For complete documentation, see [docs/BACKGROUND_JOBS_API.md](docs/BACKGROUND_JOBS_API.md).

### Background Jobs Code Cleanup

If you don't need the background jobs functionality, you can remove it completely. See [docs/BACKGROUND_JOBS_CLEANUP.md](docs/BACKGROUND_JOBS_CLEANUP.md) for detailed step-by-step instructions.

**Quick cleanup summary:**
1. Remove `app/api/v1/background_jobs.py`
2. Remove `app/services/background_job_service.py` and `app/core/background_tasks.py`
3. Update `app/api/urls.py` and `app/main.py`
4. Remove `tests/test_background_jobs.py`
5. Remove `docs/BACKGROUND_JOBS_API.md`

After cleanup, you'll still have a fully functional FastAPI application with articles CRUD, database integration, logging, and all core features.

## 21) Documentation

### 📚 Available Documentation

- **[Architecture Overview](docs/ARCHITECTURE.md)** - System architecture, components, and design patterns
- **[Redis Caching Guide](docs/REDIS_CACHING.md)** - Complete Redis caching system documentation
- **[Background Jobs API](docs/BACKGROUND_JOBS_API.md)** - Complete background jobs system documentation
- **[Background Jobs Cleanup](docs/BACKGROUND_JOBS_CLEANUP.md)** - How to remove background jobs feature
- **[Template Cleanup](docs/TEMPLATE_CLEANUP.md)** - Complete cleanup guide to remove all demo code
- **[Testing Guide](docs/TESTING.md)** - Comprehensive testing setup and best practices

### 🔗 Quick Links

- **API Documentation**: Available at `/docs` and `/openapi.json` when running the server
- **Health Check**: `GET /healthz` - Server status and trace ID
- **Articles API**: `GET /api/v1/articles/` - Article CRUD operations
- **Background Jobs**: `GET /api/v1/jobs/` - Background job management (if enabled)

## 22) API docs & versioning

- The API is namespaced under `/api/v1`. Add new routers under `app/api/v1/` and include them in `app/api/urls.py`.
- Use response models to keep OpenAPI accurate. Docs available at `/docs` and `/openapi.json`.
- URL configuration follows Django-style organization with centralized routing in `app/api/urls.py`.

## 23) VS Code mandatory extensions

This repo recommends the following VS Code extensions (see `.vscode/extensions.json`). Installing them ensures consistent formatting and linting:

- ms-python.python — Python language support
- ms-python.black-formatter — Black code formatter
- ms-python.isort — Import sorting
- ms-python.flake8 — Linting

Install all recommendations in one step:

```bash
code --install-extension ms-python.python \
     --install-extension ms-python.black-formatter \
     --install-extension ms-python.isort \
     --install-extension ms-python.flake8
```

Or in VS Code:

- Open the Command Palette → “Extensions: Show Recommended Extensions” → Install all.

## 9) How to extend this template (step‑by‑step guide)

This section shows how to add a new resource (example: `Category`) end‑to‑end: model ➜ schema ➜ repository ➜ service ➜ API ➜ migration ➜ tests.

Prereqs:

- Virtualenv active and deps installed
- Alembic configured (already in this repo)

### 1) Define the database model

- File: `app/models/category.py`
- Add to `app/models/__init__.py` to export your model (import side‑effect registers metadata).
- Example minimal model:

```python
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
```

### 2) Create Pydantic schemas

- File: `app/schemas/category.py`
- Patterns: `CategoryBase`, `CategoryCreate`, `CategoryUpdate`, `CategoryRead`.

```python
from pydantic import BaseModel

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: str | None = None

class CategoryRead(CategoryBase):
    id: int

    model_config = {"from_attributes": True}
```

### 3) Repository (data access)

- File: `app/repositories/category.py`
- Keep it CRUD‑focused; no business logic.

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category

async def create(session: AsyncSession, *, name: str) -> Category:
    obj = Category(name=name)
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj

async def get_by_id(session: AsyncSession, id_: int) -> Category | None:
    res = await session.execute(select(Category).where(Category.id == id_))
    return res.scalar_one_or_none()

async def get_by_name(session: AsyncSession, name: str) -> Category | None:
    res = await session.execute(select(Category).where(Category.name == name))
    return res.scalar_one_or_none()

async def list_all(session: AsyncSession) -> list[Category]:
    res = await session.execute(select(Category).order_by(Category.id))
    return list(res.scalars())

async def update(session: AsyncSession, obj: Category, *, name: str | None = None) -> Category:
    if name is not None:
        obj.name = name
    await session.commit()
    await session.refresh(obj)
    return obj

async def delete(session: AsyncSession, obj: Category) -> None:
    await session.delete(obj)
    await session.commit()
```

### 4) Service (business logic)

- File: `app/services/category.py`
- Validate rules, orchestrate repository calls, map to schemas.

```python
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import category as repo
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead

async def create_category(session: AsyncSession, data: CategoryCreate) -> CategoryRead:
    exists = await repo.get_by_name(session, data.name)
    if exists:
        raise ValueError("Category already exists")
    obj = await repo.create(session, name=data.name)
    return CategoryRead.model_validate(obj)

async def list_categories(session: AsyncSession) -> list[CategoryRead]:
    return [CategoryRead.model_validate(o) for o in await repo.list_all(session)]

async def update_category(session: AsyncSession, id_: int, data: CategoryUpdate) -> CategoryRead:
    obj = await repo.get_by_id(session, id_)
    if not obj:
        raise LookupError("Not found")
    obj = await repo.update(session, obj, name=data.name)
    return CategoryRead.model_validate(obj)

async def delete_category(session: AsyncSession, id_: int) -> None:
    obj = await repo.get_by_id(session, id_)
    if not obj:
        raise LookupError("Not found")
    await repo.delete(session, obj)
```

### 5) API router

- File: `app/api/v1/categories.py`
- Wire to services and dependency‑inject the session (`app.db.session.get_session`).

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_session
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryRead
from app.services import category as svc

router = APIRouter()  # No prefix - handled by app/api/urls.py

@router.post("/", response_model=CategoryRead, status_code=201)
async def create(payload: CategoryCreate, session: AsyncSession = Depends(get_session)):
    return await svc.create_category(session, payload)

@router.get("/", response_model=list[CategoryRead])
async def list_all(session: AsyncSession = Depends(get_session)):
    return await svc.list_categories(session)

@router.patch("/{id}", response_model=CategoryRead)
async def update(id: int, payload: CategoryUpdate, session: AsyncSession = Depends(get_session)):
    return await svc.update_category(session, id, payload)

@router.delete("/{id}", status_code=204)
async def delete(id: int, session: AsyncSession = Depends(get_session)):
    await svc.delete_category(session, id)
```

Then include the router in `app/api/urls.py`:

```python
from app.api.v1 import categories

api_router.include_router(
    categories.router,
    prefix="/v1/categories",
    tags=["categories"]
)
```

### 6) Database migration

Generate and apply migrations after adding the model.

```bash
alembic revision --autogenerate -m "add categories"
alembic upgrade head
```

### 7) Tests (outline)

- Create `tests/api/test_categories.py` for API tests (use httpx AsyncClient).
- Create `tests/services/test_category.py` for service rules.

### 8) Docs and discoverability

- Your endpoints appear at `/docs` automatically from FastAPI.
- Keep response models in `schemas/` to enforce consistent output contracts.

Tips:

- Keep data logic in repositories, business rules in services, and HTTP wiring in routers.
- Prefer small, focused functions; handle edge cases early.
- Add types everywhere for clarity and safety.
