# Project Setup Guide

## Prerequisites

- **Python 3.12+**
- **Docker & Docker Compose** (for full stack)
- **Make** (optional, but recommended)
- **uv** (Python package manager)

## 1. Installation

### Option A: Using Make (Recommended)

The project includes a `Makefile` to automate setup.

```bash
# Initialize virtual environment and install dependencies
make init
```

### Option B: Manual Setup

If you don't have `make` or prefer manual steps:

1. **Install uv**:
   ```bash
   pip install uv
   ```

2. **Create Virtual Environment**:
   ```bash
   uv venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   .\venv\Scripts\activate   # Windows
   ```

3. **Install Dependencies**:
   ```bash
   uv sync
   ```

## 2. Environment Configuration

1. Copy the example environment file:
   ```bash
   cp env/.env.example env/.env
   ```

2. Edit `env/.env` with your local settings.
   - **Database**: Defaults to SQLite for local dev (`sqlite+aiosqlite:///./app.db`).
   - **Redis**: Defaults to `redis://localhost:6379/0`.

## 3. Database Setup

This project uses **Alembic** for database migrations.

1. **Apply Migrations**:
   ```bash
   make migrate
   # or
   alembic upgrade head
   ```

2. **Create New Migrations** (after changing models):
   ```bash
   make makemigrations MSG="description of changes"
   # or
   alembic revision --autogenerate -m "description of changes"
   ```

## 4. Running the Application

### Local Development

Start the development server with auto-reload:

```bash
make run-dev
# or
uvicorn src.main:app --reload
```

The API will be available at:
- **API Root**: http://localhost:8000/api/v1
- **Docs (Swagger)**: http://localhost:8000/docs
- **Docs (ReDoc)**: http://localhost:8000/redoc

### Docker Development

Run the full stack (App + Postgres + Redis) in Docker:

```bash
make d-up
# or
docker compose up -d
```

View logs:
```bash
make d-logs
```

## 5. Development Tools

### Code Quality

Run linting and formatting checks:

```bash
make static-tests
```

This runs:
- **isort**: Import sorting
- **black**: Code formatting
- **flake8**: Style enforcement
- **ruff**: Fast linting

### Testing

Run the test suite:

```bash
make pytest
```

For more testing options, see [TESTING.md](TESTING.md).
