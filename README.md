# FastAPI Vibe Coding Template 🚀

A production-ready, high-performance **FastAPI** template designed for scalability, maintainability, and developer experience.

## ✨ Features

- **⚡ FastAPI**: High performance, easy to learn, fast to code, ready for production.
- **🐘 PostgreSQL + AsyncSQLAlchemy**: Robust database with fully async ORM.
- **🔄 Alembic Migrations**: Per-app migration strategy for modular database management.
- **📦 Pydantic v2**: Modern data validation and settings management.
- **🐳 Docker & Docker Compose**: Full stack containerization (App, DB, Redis).
- **⚡ Redis**: Caching and background task support.
- **🔍 Observability**: Structured logging with correlation IDs.
- **🛠️ Developer Tools**: `Makefile` automation, `uv` package management, pre-configured linting/formatting.

## 🚀 Quick Start

### 1. Setup

```bash
# Initialize environment and install dependencies
make init
```

### 2. Configure Environment

```bash
cp env/.env.example env/.env
# Edit env/.env with your settings
```

### 3. Run Locally

```bash
# Start development server
make run-dev
```

Visit **[http://localhost:8000/docs](http://localhost:8000/docs)** for the interactive API documentation.

### 4. Run with Docker

```bash
make d-up
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- **[Setup Guide](docs/SETUP.md)**: Detailed installation and configuration instructions.
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Architecture, patterns, and best practices.
- **[Testing Guide](docs/TESTING.md)**: How to run and write tests.
- **[Deployment Guide](docs/DEPLOYMENT.md)**: Docker and production deployment.
- **[Package Manager Guide](docs/PACKAGE_MANAGER.md)**: Managing dependencies with `uv`.
- **[Pydantic Guide](docs/PYDANTIC_GUIDE.md)**: Data validation and schemas.
- **[Background Jobs Guide](docs/BACKGROUND_JOBS_GUIDE.md)**: Architecture and usage of Dramatiq background tasks.
- **[Audit Log Guide](docs/AUDIT_LOG_GUIDE.md)**: Usage of the asynchronous audit logging system.

## 🛠️ Development Commands

| Command | Description |
|---------|-------------|
| `make run-dev` | Start dev server with reload |
| `make migrate` | Apply database migrations |
| `make makemigrations` | Create new migrations |
| `make pytest` | Run tests with coverage |
| `make static-tests` | Run linting and formatting checks |
| `make d-up` | Start Docker containers |

For a full list of commands, run:
```bash
make help
```

## 🧪 Testing

Run the full test suite:

```bash
make pytest
```

## 🤝 Contributing

Please read the [Developer Guide](docs/DEVELOPER_GUIDE.md) before contributing.

## 📝 License

This project is licensed under the MIT License.
