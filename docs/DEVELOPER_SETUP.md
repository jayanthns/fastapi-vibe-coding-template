# Developer Setup Guide

This comprehensive guide will help you set up your development environment for the FastAPI Vibe Coding project from scratch.

## Table of Contents

- [System Requirements](#system-requirements)
- [Python Version](#python-version)
- [Virtual Environment Setup](#virtual-environment-setup)
- [Package Management](#package-management)
  - [Option 1: Using uv (Recommended)](#option-1-using-uv-recommended)
  - [Option 2: Using pip-tools](#option-2-using-pip-tools)
  - [Option 3: Direct pip](#option-3-direct-pip)
- [Environment Variables](#environment-variables)
- [Database Setup](#database-setup)
  - [Option 1: Docker Database Only](#option-1-docker-database-only)
  - [Option 2: Full Docker Setup](#option-2-full-docker-setup)
- [Database Migrations](#database-migrations)
- [Running the Application](#running-the-application)
- [Development Workflow](#development-workflow)
- [Testing Setup](#testing-setup)
- [Troubleshooting](#troubleshooting)

## System Requirements

- **Python**: 3.12+ (recommended: Python 3.12.7)
- **Operating System**: macOS, Linux, or Windows
- **Docker**: For database services (PostgreSQL + Redis)
- **Git**: For version control

## Python Version

### Recommended: Python 3.12

```bash
# Check your Python version
python3 --version
# Should output: Python 3.12.x

# If you need to install Python 3.12:
# macOS (using Homebrew)
brew install python@3.12

# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

# Windows (using Chocolatey)
choco install python --version=3.12.7

# Or download from python.org
```

## Virtual Environment Setup

### Create and Activate Virtual Environment

```bash
# Navigate to project directory
cd /path/to/fastapi-vibe-coding

# Create virtual environment
python3.12 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python
# Should output: /path/to/fastapi-vibe-coding/venv/bin/python
```

## Package Management

### Option 1: Using uv (Recommended)

`uv` is a fast Python package installer and resolver, written in Rust. It's significantly faster than pip.

#### Install uv

```bash
# Install uv globally
pip install uv

# Or using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pipx
pipx install uv
```

#### Setup with uv

```bash
# Activate your virtual environment first
source venv/bin/activate

# Initialize uv in the project
make uv-venv-init

# Update and install dependencies
make uv-update-package

# Or manually:
uv pip install -r requirements/requirements.txt -r requirements/local_requirements.txt
```

#### uv Commands

```bash
# Update dependency files
make uv-update-deps

# Install dependencies
make uv-install-deps

# Update and install in one command
make uv-update-package

# Security audit
make uv-pip-audit-prod    # Production dependencies only
make uv-pip-audit-all     # All dependencies
```

### Option 2: Using pip-tools

pip-tools provides dependency management with lock files.

#### Setup with pip-tools

```bash
# Activate your virtual environment
source venv/bin/activate

# Update and install dependencies
make update-package

# Or manually:
pip install --upgrade pip-tools pip wheel
pip-compile --upgrade --resolver backtracking -o requirements/requirements.txt requirements_raw/requirements.in
pip-compile --upgrade --resolver backtracking -o requirements/local_requirements.txt requirements_raw/local_requirements.in
pip install -r requirements/requirements.txt -r requirements/local_requirements.txt
```

#### pip-tools Commands

```bash
# Update dependency files
make update-deps

# Install dependencies
make install-deps

# Update and install in one command
make update-package

# Security audit
make pip-audit-prod    # Production dependencies only
make pip-audit-all     # All dependencies
```

### Option 3: Direct pip

For simple setups without dependency locking.

```bash
# Activate your virtual environment
source venv/bin/activate

# Install dependencies directly from pyproject.toml
pip install -e ".[dev]"

# Or install specific requirements
pip install -r requirements/requirements.txt
pip install -r requirements/local_requirements.txt
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example environment file
cp .env.example .env  # If you have one
# Or create manually:
touch .env
```

### Required Environment Variables

```env
# Database Configuration
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=fastapi_vibe_coding
DATABASE_DRIVER=postgresql+asyncpg

# For Docker database
DATABASE_DOCKER_HOST=localhost

# Redis Configuration
USE_REDIS=1
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=redis
REDIS_HOST_AND_PORT=localhost:6379

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
ENVIRONMENT=development

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx"]

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
```

### Environment Variables for Docker

When using Docker, some variables are automatically set:

```env
# Docker-specific variables (set automatically by docker-compose)
DOCKER_CONTAINER=true
DATABASE_HOST=fastapi_vibe_coding_db_svc
REDIS_HOST=fastapi_vibe_coding_redis_svc
```

## Database Setup

### Option 1: Docker Database Only (Recommended for Development)

Run only the database services in Docker while running the FastAPI app locally.

#### Start Database Services

```bash
# Start PostgreSQL and Redis
make d-db-and-redis

# Or start individually:
make d-db      # PostgreSQL only
make d-redis   # Redis only

# Check if services are running
docker ps
```

#### Database Connection Details

- **PostgreSQL**: `localhost:5432`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `fastapi_vibe_coding`

- **Redis**: `localhost:6379`
  - Password: `redis`

#### View Database Logs

```bash
# View all database logs
make d-db-and-redis-logs

# View PostgreSQL logs only
docker compose logs -f fastapi_vibe_coding_db_svc

# View Redis logs only
make d-redis-logs
```

### Option 2: Full Docker Setup

Run the entire application stack in Docker.

#### Start Full Stack

```bash
# Start all services (app + database + redis)
make d-up

# Or using docker-compose directly
docker compose up -d
```

#### View Application Logs

```bash
# View all logs
make d-logs

# View app logs only
make d-logs-app

# View specific service logs
docker compose logs -f fastapi_vibe_coding
```

#### Stop Services

```bash
# Stop all services
make d-down

# Or using docker-compose
docker compose down
```

## Database Migrations

### Initialize Database

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations (create tables)
make migrate

# Or manually:
alembic upgrade head
```

### Migration Commands

```bash
# Create a new migration
make makemigrations MSG="add user table"

# Apply migrations
make migrate

# Check current migration
make migrate-current

# View migration history
make migrate-history

# Reset database (downgrade and upgrade)
make migrate-reset

# Downgrade one migration
make migrate-downgrade
```

### Load Sample Data

```bash
# Load sensitive fields data
python scripts/load_sensitive_fields.py data/sensitive_fields.json
python scripts/load_sensitive_fields.py data/user_sensitive_fields.json
```

## Running the Application

### Local Development (Recommended)

```bash
# Activate virtual environment
source venv/bin/activate

# Start the FastAPI server in development mode (with auto-reload)
make run
# OR
make run-dev

# For production-like setup (gunicorn + uvicorn workers)
make run-prod

# Or manually:
# Development mode:
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production mode:
./deploy/uvicorn_start.sh
```

The application will be available at:

- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **ReDoc Documentation**: http://localhost:8000/redoc

### Docker Development

```bash
# Start full stack
make d-up

# View logs
make d-logs-app
```

## Development Workflow

### Complete Setup (First Time)

```bash
# 1. Clone the repository
git clone <repository-url>
cd fastapi-vibe-coding

# 2. Create and activate virtual environment
python3.12 -m venv venv
source venv/bin/activate

# 3. Install dependencies
make uv-update-package  # Using uv (recommended)
# OR
make update-package     # Using pip-tools

# 4. Create environment file
cp .env.example .env  # Edit with your settings

# 5. Start database services
make d-db-and-redis

# 6. Run database migrations
make migrate

# 7. Load sample data (optional)
python scripts/load_sensitive_fields.py data/sensitive_fields.json

# 8. Start the application
make run  # Development mode with auto-reload
```

### Daily Development Workflow

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start database services (if not running)
make d-db-and-redis

# 3. Run migrations (if needed)
make migrate

# 4. Start the application
make run  # Development mode with auto-reload

# 5. Run tests
make test

# 6. Check code quality
make lint  # If you have linting commands
```

## Testing Setup

### Run Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
make test

# Run tests with coverage
make test-coverage

# Run fast tests only (exclude slow tests)
make test-fast

# Run specific test categories
make test-unit        # Unit tests only
make test-integration # Integration tests only
make test-api         # API tests only

# Run tests in order
make test-pings       # Ping tests first
make test-utils       # Utility tests
make test-last        # Background job tests
```

### Test Database Setup

```bash
# Setup test database
make test-db-setup

# Drop test database
make test-db-drop
```

### Test Configuration

Tests use a separate test database. Environment variables for testing:

```env
# Test Database (automatically created)
TEST_DATABASE_NAME=fastapi_vibe_coding_test
TEST_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_vibe_coding_test

# Test Redis (optional)
TEST_REDIS_URL=redis://localhost:6379/1
```

## Makefile Commands Reference

### Virtual Environment

```bash
make venv-init              # Create virtual environment
make uv-venv-init          # Create virtual environment with uv
```

### Dependencies

```bash
# pip-tools
make update-deps           # Update requirement files
make install-deps          # Install dependencies
make update-package        # Update and install

# uv (recommended)
make uv-update-deps        # Update requirement files
make uv-install-deps       # Install dependencies
make uv-update-package     # Update and install

# Security auditing
make pip-audit-prod        # Audit production dependencies
make pip-audit-all         # Audit all dependencies
make uv-pip-audit-prod     # uv audit production dependencies
make uv-pip-audit-all      # uv audit all dependencies
```

### Docker Services

```bash
make d-db                  # Start PostgreSQL only
make d-redis               # Start Redis only
make d-db-and-redis        # Start PostgreSQL + Redis
make d-app                 # Start application only
make d-up                  # Start all services
make d-down                # Stop all services
make d-logs                # View all logs
make d-logs-app            # View app logs only
```

### Database Migrations

```bash
make makemigrations MSG="" # Create new migration
make migrate               # Apply migrations
make migrate-current       # Show current migration
make migrate-history       # Show migration history
make migrate-reset         # Reset migrations
make migrate-downgrade     # Downgrade one migration
```

### Development

```bash
make run                   # Start FastAPI server in development mode (uvicorn with reload)
make run-dev               # Start FastAPI server in development mode (uvicorn with reload)
make run-prod              # Start FastAPI server in production mode (gunicorn + uvicorn workers)
make dev-setup             # Complete development setup
make dev-reset             # Reset development database
```

### Testing

```bash
make test                  # Run all tests
make test-coverage         # Run tests with coverage
make test-fast             # Run fast tests only
make test-unit             # Run unit tests only
make test-integration      # Run integration tests only
make test-api              # Run API tests only
make pytest-all            # Run all tests with HTML report
make pytest-fast           # Run fast tests with HTML report
make test-pings            # Run ping tests first
make test-utils            # Run utility tests
make test-last             # Run background job tests
```

## Troubleshooting

### Common Issues

#### 1. Python Version Issues

```bash
# Check Python version
python3 --version

# If using wrong version, recreate venv
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
```

#### 2. Database Connection Issues

```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check database logs
make d-db-and-redis-logs

# Restart database services
make d-down
make d-db-and-redis
```

#### 3. Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Test Redis connection
docker exec -it fastapi_vibe_coding_redis_container redis-cli -a redis ping
```

#### 4. Port Conflicts

```bash
# Check if ports are in use
lsof -i :8000  # FastAPI
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Kill processes if needed
kill -9 <PID>
```

#### 5. Permission Issues

```bash
# Fix script permissions
chmod +x deploy/*.sh

# Fix file ownership (if needed)
sudo chown -R $USER:$USER .
```

#### 6. Virtual Environment Issues

```bash
# Deactivate and reactivate
deactivate
source venv/bin/activate

# Recreate virtual environment
rm -rf venv
python3.12 -m venv venv
source venv/bin/activate
make uv-update-package
```

#### 7. Migration Issues

```bash
# Reset migrations
make migrate-reset

# Or manually
alembic downgrade base
alembic upgrade head
```

### Getting Help

```bash
# View all available commands
make help

# Check application health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs
```

### Logs and Debugging

```bash
# Application logs (local)
tail -f tmp/logs/app-*.log

# SQLAlchemy logs (local)
tail -f tmp/logs/sqlalchemy-*.log

# Docker logs
make d-logs

# Database logs
docker compose logs -f fastapi_vibe_coding_db_svc
```

## Production Considerations

### Environment Variables for Production

```env
# Production settings
DEBUG=False
ENVIRONMENT=production
LOG_LEVEL=WARNING

# Secure secrets
SECRET_KEY=your-super-secure-production-secret-key
JWT_SECRET_KEY=your-super-secure-jwt-secret-key

# Production database
DATABASE_HOST=your-production-db-host
DATABASE_PASSWORD=your-secure-db-password

# Production Redis
REDIS_HOST=your-production-redis-host
REDIS_PASSWORD=your-secure-redis-password
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use strong, unique secrets
- [ ] Enable HTTPS in production
- [ ] Set up proper CORS origins
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Regular security audits
- [ ] Keep dependencies updated

---

## Quick Start Summary

For experienced developers who want to get started quickly:

```bash
# Clone and setup
git clone <repo-url> && cd fastapi-vibe-coding
python3.12 -m venv venv && source venv/bin/activate
make uv-update-package
make d-db-and-redis
make migrate
make run
```

Visit http://localhost:8000/docs to see the API documentation!
