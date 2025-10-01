# Architecture and Module Walkthrough

This document explains how the project is structured, how a request flows through the system, and the comprehensive logging and tracing infrastructure. It also provides guidance on extending the codebase with new modules.

## High-level layout

```txt
app/
  api/
    urls.py              # Centralized URL configuration (Django-style)
    v1/
      articles.py         # API routes (FastAPI routers)
  core/
    config.py            # App configuration (pydantic-settings)
    logging.py           # Comprehensive logging system (config + utilities)
    sqlalchemy_logging.py # SQLAlchemy logging integration
  db/
    session.py           # SQLAlchemy async engine + session dependency
  middleware/
    trace.py             # Trace ID middleware (request/response)
  models/
    __init__.py
    article.py           # SQLAlchemy ORM models
  repositories/
    article.py           # Data-access layer (CRUD SQLAlchemy ops)
  schemas/
    article.py           # Pydantic v2 schemas + APIResponse wrapper
  services/
    article.py           # Business/domain logic
    background_tasks.py  # Background task examples
  main.py               # FastAPI app, middleware, centralized URL routing
alembic/
  env.py                 # Migration runtime config
  versions/              # Versioned migration scripts
tmp/
  logs/                  # Application log files (git-ignored)
    app-YYYY-MM-DD.log   # Main application logs
    sqlalchemy-YYYY-MM-DD.log # Database query logs (dev only)
```

## Module-by-module

### `app/main.py`

- Creates the FastAPI app and lifecycle (`lifespan`) hook.
- Registers middleware (CORS, TraceID) and includes centralized API router.
- Provides a simple `/healthz` endpoint with trace_id.
- On startup, initializes logging system and opens DB connection.

Key points:

- Uses `settings` to configure app title and debug.
- Mounts the centralized `api_router` under `/api` prefix.
- All API routing is managed through `app/api/urls.py`.
- **Trace ID middleware** generates unique trace_id for each request.
- **Logging system** is initialized during app startup.

### `app/core/config.py`

- Centralized configuration using `pydantic-settings`.
- Loads environment variables from `.env` (via `Config.env_file`).
- Exposes `settings` with fields such as:
  - `database_url`: e.g. `sqlite+aiosqlite:///./app.db`
  - `environment`: `development` by default
  - `debug`: boolean
  - `backend_cors_origins`: list of allowed origins

Why: Encapsulates all configuration for consistent access across layers.

### `app/core/logging.py`

- **Comprehensive logging system** with configuration, utilities, and formatters.
- `LoggingConfig` class handles all logging setup and configuration.
- `TraceIDFormatter`: Custom formatter that includes trace_id in all messages.
- `RequestLogger`: Request-scoped logger with automatic trace_id injection.
- Configures both console and file logging with rotation.
- Sets up different log files: `app-*.log` and `sqlalchemy-*.log`.
- Handles log rotation (10MB max, 5 backup files).
- Helper functions: `get_logger()`, `get_logger_for_trace_id()`, `log_request_access()`, `log_error()`.

Why: Single, comprehensive logging module that handles all logging concerns in one place.

### `app/core/sqlalchemy_logging.py`

- **SQLAlchemy logging integration** with trace_id system.
- `SQLAlchemyTraceIDHandler`: Custom handler for database logs.
- Environment-based SQL logging (only enabled in development).
- Event-based logging for SQL statements and execution.

Why: SQLAlchemy-specific logging integration, part of the core logging system.

### `app/middleware/trace.py`

- **Trace ID middleware** for request-level tracing.
- Generates unique UUID for each request and stores in `request.state`.
- Adds trace_id to response headers (`X-Trace-ID`).
- Tracks request processing time (`X-Response-Time`).
- Logs request lifecycle (start, completion, errors).
- Provides utility functions: `get_trace_id()`, `get_request_logger()`.

Why: Django-style request-level middleware for comprehensive request tracking.

### `app/db/session.py`

- Defines the SQLAlchemy 2.0 async engine and async session factory.
- Exposes `Base` (Declarative Base) used by all models.
- Provides `get_db()` FastAPI dependency for basic database sessions.
- **Provides `get_db_with_trace_id()`** dependency that:
  - Sets up trace_id-aware SQLAlchemy logging (development only)
  - Manages logging handler lifecycle per request
  - Ensures proper cleanup of logging handlers

Why: Single source of truth for DB connectivity with integrated logging.

### `app/models/*`

- SQLAlchemy ORM models that map to database tables.
- Example: `Article` with `id`, `title`, `content`, `created_at`, `updated_at`.

Why: Encapsulate schema of persisted entities and ORM mapping details.

### `app/schemas/*`

- Pydantic v2 models that define request/response payload shapes.
- **`APIResponse[T]`**: Generic wrapper for all API responses with:
  - `success`, `message`, `status_code`, `data`, `error`, `trace_id`, `timestamp`
  - `create_with_trace_id()` class method for easy response creation
- Separated into `Create`, `Update`, and outward-facing `Article` forms.

Why: Strong typing, clear contracts, and consistent API response format.

### `app/repositories/*`

- Data-access layer. Performs DB operations using SQLAlchemy `AsyncSession`.
- Offers methods like `create`, `get`, `list`, `update`, `delete` per entity.
- Uses keyword-only arguments (`*`) for update methods for clarity and safety.

Why: Keeps SQL queries and persistence logic out of business logic and APIs.

### `app/services/*`

- Business/domain logic orchestrating repositories and enforcing rules.
- Example: `ArticleService` calls `article_repository` and shapes behavior.
- **`background_tasks.py`**: Examples of background tasks with trace_id-aware logging.

Why: Keeps API layer thin and enables reuse and testing of domain logic.

### `app/api/urls.py`

- Centralized URL configuration following Django's `urls.py` pattern.
- Manages all API routes and their prefixes in one place.
- Includes versioned routers (v1, v2, etc.) with appropriate prefixes and tags.

Why: Single source of truth for API routing, easy to maintain and extend.

### `app/api/v1/*`

- FastAPI routers that define HTTP endpoints and wire dependencies.
- Validates input using `schemas`, calls `services`, returns `APIResponse` wrappers.
- Individual routers without prefixes (handled by main `urls.py`).
- **Uses trace_id-aware logging** throughout request lifecycle.
- **Uses `get_db_with_trace_id()`** for database sessions with logging.

Why: Clean separation between HTTP transport concerns and domain logic with comprehensive logging.

### `alembic/*`

- Database migrations. `env.py` configures metadata and async engine usage.
- `versions/` contains generated migration scripts from `alembic revision --autogenerate`.

Why: Version control for database schema, safe upgrades/downgrades.

## Request flow (Article example with logging)

1. **HTTP request** hits `app/api/v1/articles.py` route.
2. **TraceIDMiddleware** generates unique trace_id and stores in `request.state`.
3. **RequestLogger** is created and attached to request with trace_id.
4. **Request start** is logged with trace_id.
5. FastAPI parses/validates payload into `ArticleCreate`/`ArticleUpdate` schema.
6. Router injects an `AsyncSession` via `get_db_with_trace_id()` dependency.
7. **SQLAlchemy logging** is set up with trace_id (development only).
8. Router calls `article_service` which executes domain logic.
9. Service calls `article_repository` to interact with the DB.
10. **SQL queries** are logged with trace_id (development only).
11. Repository uses SQLAlchemy ORM to query/mutate the `Article` model.
12. Result models are returned and wrapped in `APIResponse` with trace_id.
13. **Request completion** is logged with processing time and trace_id.
14. **Access log** entry is created with method, path, status, timing, and trace_id.
15. Response includes trace_id in headers and response body.

## Logging Architecture

### File Structure

```sh
tmp/logs/
├── app-YYYY-MM-DD.log        # All application logs
└── sqlalchemy-YYYY-MM-DD.log # Database queries (dev only)
```

### Log Format

```sh
2024-09-29 20:06:15,123 | INFO | 32471740-1d73-4cc7-a437-a85083301776 | app.request | Request started: GET /api/v1/articles/
2024-09-29 20:06:15,124 | INFO | 32471740-1d73-4cc7-a437-a85083301776 | app.request | Listing articles - skip: 0, limit: 100
2024-09-29 20:06:15,125 | INFO | 32471740-1d73-4cc7-a437-a85083301776 | app.access | ACCESS: GET /api/v1/articles/ - 200 - 0.0242s
```

### Key Features

- **Trace ID**: Every log entry includes the request's trace_id
- **Dual output**: Console + file logging simultaneously
- **Daily rotation**: New log file each day
- **Size-based rotation**: 10MB max per file, keeps 5 backup files
- **Environment-aware**: SQL logging only in development
- **Structured format**: Consistent format across all log types

## Architecture Principles

### Single Responsibility Principle (SRP) Compliance

The logging system follows SRP with clear separation:

- **`app/core/logging.py`**: Comprehensive logging system (config + utilities + formatters)
- **`app/core/sqlalchemy_logging.py`**: SQLAlchemy logging integration only
- **`app/middleware/trace.py`**: Request/response middleware only

### Clean Directory Structure

The project follows a clean, logical directory structure:

- **`app/core/`**: Core application functionality (config, logging)
- **`app/middleware/`**: Request/response middleware only
- **`app/api/`**: API routes and URL configuration
- **`app/models/`**: Database ORM models
- **`app/schemas/`**: Pydantic request/response schemas
- **`app/repositories/`**: Data access layer
- **`app/services/`**: Business logic layer
- **`app/db/`**: Database session management

### No Confusing Duplicates

- **No duplicate directories**: Removed empty `config/` and `utils/` directories
- **Consistent naming**: All core functionality in `app/core/`
- **Clear imports**: All imports follow consistent patterns

## Adding a new module (e.g., Comment)

- **Models**: create `app/models/comment.py` and add `Comment` ORM model. Import in `app/models/__init__.py`.
- **Schemas**: add `app/schemas/comment.py` with `CommentCreate`, `CommentUpdate`, `Comment`.
- **Repository**: add `app/repositories/comment.py` with CRUD methods.
- **Service**: add `app/services/comment.py` orchestrating repository operations.
- **API**: add `app/api/v1/comments.py` with routes; include router in `app/api/urls.py` under `/v1/comments`.
- **Migration**: run `alembic revision --autogenerate -m "add comment"` then `alembic upgrade head`.
- **Tests**: create tests under `app/tests/` for repository/service/router as needed.

## Environment and configuration

- `.env` drives runtime configuration; see `README.md` for example values.
- **Logging**: Automatically configured based on environment
- **SQL Logging**: Only enabled in development environment
- To switch DB:
  - Postgres (async): `postgresql+asyncpg://user:pass@host:5432/db` and install `asyncpg`.
  - Ensure Alembic sees models in `alembic/env.py` (already handled by importing `app.models`).

## Conventions

- Keep APIs thin; push logic into services and repositories.
- Prefer explicit names: `create_article`, `update_article` over generic names.
- Use Pydantic schemas for I/O contracts; avoid leaking ORM models to the API layer.
- Keep migrations small and focused with descriptive messages.
- **Always use `APIResponse` wrapper** for consistent API responses.
- **Always use `get_db_with_trace_id()`** for database sessions with logging.
- **Always use `get_logger(request)`** for request-scoped logging.

## Where to start reading

### Core Application

- `app/main.py` to see app bootstrapping, middleware, and centralized URL routing.
- `app/core/config.py` to understand application configuration and settings.
- `app/core/logging.py` to see comprehensive logging system.

### Request Flow

- `app/middleware/trace.py` to understand request tracing and logging setup.
- `app/api/urls.py` to see how API routes are organized and configured.
- `app/api/v1/articles.py` to see individual router implementation with logging.

### Business Logic

- `app/services/article.py` and `app/repositories/article.py` for domain + data layers.
- `app/models/article.py` and `app/schemas/article.py` for persisted and transport shapes.

### Database Integration

- `app/db/session.py` for database session management with trace_id integration.
- `app/core/sqlalchemy_logging.py` for database logging integration.

## Key Benefits

- **Comprehensive tracing**: Every request has a unique trace_id for end-to-end tracking
- **Structured logging**: Consistent format with trace_id in all log entries
- **Environment-aware**: SQL logging only in development, production-ready
- **SRP compliance**: Clear separation of concerns across modules
- **Django-style patterns**: Familiar middleware and logging patterns
- **Easy debugging**: Trace_id allows following requests across all logs
- **Production ready**: Proper log rotation, file management, and error handling
