# FastAPI Vibe Coding — Local Development

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white) ![FastAPI](https://img.shields.io/badge/FastAPI-0.116.x-009688?logo=fastapi&logoColor=white) ![Uvicorn](https://img.shields.io/badge/Uvicorn-Server-000000?logo=uvicorn&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00?logo=sqlalchemy&logoColor=white) ![Alembic](https://img.shields.io/badge/Alembic-Migrations-2C3E50) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-336791?logo=postgresql&logoColor=white) ![SQLite](https://img.shields.io/badge/SQLite-Local_DB-003B57?logo=sqlite&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white) ![uv](https://img.shields.io/badge/uv-Dependencies-FF6600) ![Ruff](https://img.shields.io/badge/Ruff-Linting-FFD43B) ![pytest](https://img.shields.io/badge/pytest-Tests-0A9EDC?logo=pytest&logoColor=white) ![License](https://img.shields.io/badge/License-MIT-blue)

This project is a production-ready FastAPI skeleton with SQLAlchemy (async), Alembic, and an Article CRUD. This doc covers local setup, environment values, dependency management with uv, database migrations, and how to run the app.

## Table of contents

- [FastAPI Vibe Coding — Local Development](#fastapi-vibe-coding--local-development)
  - [Table of contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [1) Create and activate a virtualenv](#1-create-and-activate-a-virtualenv)
  - [2) Environment variables (.env)](#2-environment-variables-env)
  - [3) Dependencies with uv (recommended)](#3-dependencies-with-uv-recommended)
  - [4) Database migrations (Alembic)](#4-database-migrations-alembic)
  - [5) Run the application](#5-run-the-application)
  - [6) Quick project structure](#6-quick-project-structure)
  - [7) Tests (optional)](#7-tests-optional)
  - [8) Makefile commands](#8-makefile-commands)
    - [Local app](#local-app)
    - [Python virtualenv](#python-virtualenv)
    - [Using uv for dependencies (faster)](#using-uv-for-dependencies-faster)
    - [Security auditing](#security-auditing)
    - [Docker helpers](#docker-helpers)
  - [10) Run with Docker](#10-run-with-docker)
  - [11) Debug/start scripts](#11-debugstart-scripts)
  - [12) Production deployment](#12-production-deployment)
  - [13) VS Code tasks](#13-vs-code-tasks)
  - [14) Testing guidance](#14-testing-guidance)
  - [15) Alembic tips](#15-alembic-tips)
  - [16) Security notes](#16-security-notes)
  - [17) Architecture overview](#17-architecture-overview)
  - [18) API docs \& versioning](#18-api-docs--versioning)
  - [19) VS Code mandatory extensions](#19-vs-code-mandatory-extensions)
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

```bash
pytest -q
```

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

- Use `pytest` with `httpx.AsyncClient` for async API tests.
- Provide an async SQLAlchemy test session fixture; roll back between tests or use a test DB.
- Keep unit tests for services (business logic) separate from API/integration tests.

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

## 18) API docs & versioning

- The API is namespaced under `/api/v1`. Add new routers under `app/api/v1/` and include them in `app/api/urls.py`.
- Use response models to keep OpenAPI accurate. Docs available at `/docs` and `/openapi.json`.
- URL configuration follows Django-style organization with centralized routing in `app/api/urls.py`.

## 19) VS Code mandatory extensions

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
