# Architecture and Module Walkthrough

This document explains how the project is structured and how a request flows through the system. It also provides guidance on extending the codebase with new modules.

## High-level layout

```txt
app/
  api/
    urls.py              # Centralized URL configuration (Django-style)
    v1/
      articles.py         # API routes (FastAPI routers)
  core/
    config.py            # App configuration (env-driven)
  db/
    session.py           # SQLAlchemy async engine + session dependency
  models/
    __init__.py
    article.py           # SQLAlchemy ORM models
  repositories/
    article.py           # Data-access layer (CRUD SQLAlchemy ops)
  schemas/
    article.py           # Pydantic v2 schemas
  services/
    article.py           # Business/domain logic
  main.py               # FastAPI app, middleware, centralized URL routing
alembic/
  env.py                 # Migration runtime config
  versions/              # Versioned migration scripts
```

## Module-by-module

### `app/main.py`

- Creates the FastAPI app and lifecycle (`lifespan`) hook.
- Registers middleware (CORS) and includes centralized API router.
- Provides a simple `/healthz` endpoint.
- On startup, opens a connection to surface DB issues early.

Key points:

- Uses `settings` to configure app title and debug.
- Mounts the centralized `api_router` under `/api` prefix.
- All API routing is managed through `app/api/urls.py`.

### `app/core/config.py`

- Centralized configuration using `pydantic-settings`.
- Loads environment variables from `.env` (via `Config.env_file`).
- Exposes `settings` with fields such as:
  - `database_url`: e.g. `sqlite+aiosqlite:///./app.db`
  - `environment`: `development` by default
  - `debug`: boolean
  - `backend_cors_origins`: list of allowed origins

Why: Encapsulates all configuration for consistent access across layers.

### `app/db/session.py`

- Defines the SQLAlchemy 2.0 async engine and async session factory.
- Exposes `Base` (Declarative Base) used by all models.
- Provides `get_db()` FastAPI dependency to yield an `AsyncSession` per-request.

Why: Single source of truth for DB connectivity and session scoping.

### `app/models/*`

- SQLAlchemy ORM models that map to database tables.
- Example: `Article` with `id`, `title`, `content`, `created_at`, `updated_at`.

Why: Encapsulate schema of persisted entities and ORM mapping details.

### `app/schemas/*`

- Pydantic v2 models that define request/response payload shapes.
- Separated into `Create`, `Update`, and outward-facing `Article`/`InDB` forms.

Why: Strong typing and clear contracts for FastAPI endpoints and services.

### `app/repositories/*`

- Data-access layer. Performs DB operations using SQLAlchemy `AsyncSession`.
- Offers methods like `create`, `get`, `list`, `update`, `delete` per entity.

Why: Keeps SQL queries and persistence logic out of business logic and APIs.

### `app/services/*`

- Business/domain logic orchestrating repositories and enforcing rules.
- Example: `ArticleService` calls `article_repository` and shapes behavior.

Why: Keeps API layer thin and enables reuse and testing of domain logic.

### `app/api/urls.py`

- Centralized URL configuration following Django's `urls.py` pattern.
- Manages all API routes and their prefixes in one place.
- Includes versioned routers (v1, v2, etc.) with appropriate prefixes and tags.

Why: Single source of truth for API routing, easy to maintain and extend.

### `app/api/v1/*`

- FastAPI routers that define HTTP endpoints and wire dependencies.
- Validates input using `schemas`, calls `services`, returns `schemas`.
- Individual routers without prefixes (handled by main `urls.py`).

Why: Clean separation between HTTP transport concerns and domain logic.

### `alembic/*`

- Database migrations. `env.py` configures metadata and async engine usage.
- `versions/` contains generated migration scripts from `alembic revision --autogenerate`.

Why: Version control for database schema, safe upgrades/downgrades.

## Request flow (Article example)

1. HTTP request hits `app/api/v1/articles.py` route.
2. FastAPI parses/validates payload into `ArticleCreate`/`ArticleUpdate` schema.
3. Router injects an `AsyncSession` via `get_db()` dependency.
4. Router calls `article_service` which executes domain logic.
5. Service calls `article_repository` to interact with the DB.
6. Repository uses SQLAlchemy ORM to query/mutate the `Article` model.
7. Result models are returned and serialized through Pydantic schemas to JSON.

## Adding a new module (e.g., Comment)

- Models: create `app/models/comment.py` and add `Comment` ORM model. Import in `app/models/__init__.py`.
- Schemas: add `app/schemas/comment.py` with `CommentCreate`, `CommentUpdate`, `Comment`.
- Repository: add `app/repositories/comment.py` with CRUD methods.
- Service: add `app/services/comment.py` orchestrating repository operations.
- API: add `app/api/v1/comments.py` with routes; include router in `app/api/urls.py` under `/v1/comments`.
- Migration: run `alembic revision --autogenerate -m "add comment"` then `alembic upgrade head`.
- Tests: create tests under `app/tests/` for repository/service/router as needed.

## Environment and configuration

- `.env` drives runtime configuration; see `README.md` for example values.
- To switch DB:
  - Postgres (async): `postgresql+asyncpg://user:pass@host:5432/db` and install `asyncpg`.
  - Ensure Alembic sees models in `alembic/env.py` (already handled by importing `app.models`).

## Conventions

- Keep APIs thin; push logic into services and repositories.
- Prefer explicit names: `create_article`, `update_article` over generic names.
- Use Pydantic schemas for I/O contracts; avoid leaking ORM models to the API layer.
- Keep migrations small and focused with descriptive messages.

## Where to start reading

- `app/main.py` to see app bootstrapping and centralized URL routing.
- `app/api/urls.py` to see how API routes are organized and configured.
- `app/api/v1/articles.py` to see individual router implementation and request handling.
- `app/services/article.py` and `app/repositories/article.py` for domain + data layers.
- `app/models/article.py` and `app/schemas/article.py` for persisted and transport shapes.
