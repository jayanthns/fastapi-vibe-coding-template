# Detect the operating system
ifeq ($(OS),Windows_NT)
	# Windows
	VENV_ACTIVATE = .\\venv\\Scripts\\activate
else
	# Unix-based systems (Linux/Mac)
	VENV_ACTIVATE = source ./venv/bin/activate
	# Ensure uv uses the correct virtual environment
	export UV_PROJECT_ENVIRONMENT = $(shell pwd)/venv
endif

# ============================================================================
# DEVELOPMENT COMMANDS
# ============================================================================

run:
	@echo "Running FastAPI server..."
	@$(VENV_ACTIVATE) && ./deploy/shell_scripts/gunicorn_start.sh

run-dev:
	@echo "Running FastAPI development server with reload..."
	@$(VENV_ACTIVATE) && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

kill-port:
	@echo "Killing processes on port 8000..."
	@lsof -ti:8000 | xargs kill -9 || true

shell:
	@echo "Starting Python shell..."
	@$(VENV_ACTIVATE) && python

run-worker:
	@echo "Starting Dramatiq worker..."
	@$(VENV_ACTIVATE) && dramatiq src.worker --processes 1 --threads 1

# ============================================================================
# SETUP & INSTALLATION
# ============================================================================

init: uv-venv-init install
	@echo "Initialization complete!"

venv_init:
	python3 -m venv venv
	@$(VENV_ACTIVATE) && python -m pip install --upgrade uv pip-tools pip wheel

uv-venv-init:
	python3 -m pip install uv
	uv venv venv
	@$(VENV_ACTIVATE) && python -m pip install --upgrade uv pip-tools pip wheel

install:
	@echo "Installing dependencies with uv..."
	@uv sync --all-extras

install-legacy:
	@echo "Installing from requirements files (legacy)..."
	@$(VENV_ACTIVATE) && python -m pip install -r requirements/requirements.txt -r requirements/local_requirements.txt

# ============================================================================
# DEPENDENCY MANAGEMENT (uv.lock workflow)
# ============================================================================

add-package:
	@echo "Adding package to production dependencies..."
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE is required. Usage: make add-package PACKAGE=requests [VERSION=2.31.0]"; \
		exit 1; \
	fi
	@if [ -n "$(VERSION)" ]; then \
		$(VENV_ACTIVATE) && uv add "$(PACKAGE)==$(VERSION)"; \
	else \
		$(VENV_ACTIVATE) && uv add "$(PACKAGE)"; \
	fi

add-dev-package:
	@echo "Adding package to dev dependencies..."
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE is required. Usage: make add-dev-package PACKAGE=pytest [VERSION=8.3.3]"; \
		exit 1; \
	fi
	@if [ -n "$(VERSION)" ]; then \
		$(VENV_ACTIVATE) && uv add --dev "$(PACKAGE)==$(VERSION)"; \
	else \
		$(VENV_ACTIVATE) && uv add --dev "$(PACKAGE)"; \
	fi

remove-package:
	@echo "Removing package from production dependencies..."
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE is required. Usage: make remove-package PACKAGE=requests"; \
		exit 1; \
	fi
	@$(VENV_ACTIVATE) && uv remove "$(PACKAGE)"

remove-dev-package:
	@echo "Removing package from dev dependencies..."
	@if [ -z "$(PACKAGE)" ]; then \
		echo "Error: PACKAGE is required. Usage: make remove-dev-package PACKAGE=pytest"; \
		exit 1; \
	fi
	@$(VENV_ACTIVATE) && uv remove --dev "$(PACKAGE)"

compile-deps:
	@echo "Locking dependencies from pyproject.toml..."
	@$(VENV_ACTIVATE) && uv lock

update-deps:
	@echo "Upgrading all dependencies to latest..."
	@$(VENV_ACTIVATE) && uv lock --upgrade

package-sync: update-deps
	@echo "Syncing packages..."
	@$(VENV_ACTIVATE) && uv sync

export-requirements:
	@echo "Exporting uv.lock to requirements.txt format..."
	@$(VENV_ACTIVATE) && uv pip compile pyproject.toml -o requirements.txt

# ============================================================================
# DATABASE MIGRATION COMMANDS
# ============================================================================

makemigrations:
	@echo "Creating new migration..."
	@$(VENV_ACTIVATE) && alembic revision --autogenerate -m "$(MSG)"

migrate:
	@echo "Applying migrations..."
	@$(VENV_ACTIVATE) && alembic upgrade head

migrate-downgrade:
	@echo "Downgrading one migration..."
	@$(VENV_ACTIVATE) && alembic downgrade -1

migrate-reset:
	@echo "Resetting all migrations..."
	@$(VENV_ACTIVATE) && alembic downgrade base && alembic upgrade head

migrate-history:
	@echo "Migration history:"
	@$(VENV_ACTIVATE) && alembic history

migrate-current:
	@echo "Current migration:"
	@$(VENV_ACTIVATE) && alembic current

migrate-show:
	@echo "Show migration details:"
	@$(VENV_ACTIVATE) && alembic show head

db-init:
	@echo "Initializing database..."
	@$(VENV_ACTIVATE) && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	@$(VENV_ACTIVATE) && alembic downgrade base && alembic upgrade head

# ============================================================================
# TESTING COMMANDS
# ============================================================================

pytest-run:
	@echo "Running Pytest with Coverage"
	@$(VENV_ACTIVATE) && pytest --cov=src --cov-report=html:coverage_html_report --cov-report=term-missing --cov-fail-under=80

pytest-v:
	@echo "Running Pytest (Verbose Mode)"
	@$(VENV_ACTIVATE) && pytest -v

pytest-q:
	@echo "Running Pytest (Quiet Mode)"
	@$(VENV_ACTIVATE) && pytest -q

pytest-lf:
	@echo "Running Pytest (Last Failed Tests)"
	@$(VENV_ACTIVATE) && pytest --lf

pytest-x:
	@echo "Running Pytest (Exit on First Failure)"
	@$(VENV_ACTIVATE) && pytest -x

pytest-slow:
	@echo "Running Pytest (Show Slowest Tests)"
	@$(VENV_ACTIVATE) && pytest --durations=10

pytest-k:
	@echo "Running Pytest (Keyword Search)"
	@echo "Usage: make pytest-k K=keyword"
	@if [ -z "$(K)" ]; then \
		echo "Error: K (keyword) is required. Example: make pytest-k K=test_login"; \
		exit 1; \
	fi
	@$(VENV_ACTIVATE) && pytest -k "$(K)"

pytest-w:
	@echo "Running Pytest (Show Warnings)"
	@$(VENV_ACTIVATE) && pytest -W always

# Aliases
dynamic-test: pytest-run
run-tests: pytest-run
pytest: pytest-run
test: pytest-run

pytest-open-report:
	@echo "Opening Pytest Report"
	@open coverage_html_report/index.html

test-report: pytest-open-report

test-fast:
	@echo "Running fast tests (excluding slow tests)..."
	@$(VENV_ACTIVATE) && PYTHONPATH=. pytest -m "not slow" --cov=src --cov-report=html:coverage_html_report

test-api:
	@echo "Running API tests only..."
	@$(VENV_ACTIVATE) && PYTHONPATH=. pytest tests/test_api/

# ============================================================================
# CODE QUALITY COMMANDS
# ============================================================================

isort_check:
	@echo "Running isort check..."
	@$(VENV_ACTIVATE) && isort --check-only .

black_check:
	@echo "Running black check..."
	@$(VENV_ACTIVATE) && black --check .

flake8:
	@echo "Running flake8..."
	@$(VENV_ACTIVATE) && flake8 .

ruff:
	@echo "Running ruff..."
	@$(VENV_ACTIVATE) && ruff check .

ruff-fix:
	@echo "Running ruff with auto-fix..."
	@$(VENV_ACTIVATE) && ruff check --fix .

static-tests: isort_check black_check flake8

format:
	@echo "Formatting code..."
	@$(VENV_ACTIVATE) && isort . && black .

# ============================================================================
# DOCKER COMMANDS
# ============================================================================

d-shell:
	docker exec -it fastapi_vibe_coding_app_svc /bin/bash

d-db:
	docker compose up -d fastapi_vibe_coding_db_svc

d-redis:
	docker compose up -d fastapi_vibe_coding_redis_svc

d-db-logs:
	docker compose logs -f fastapi_vibe_coding_db_svc

d-redis-logs:
	docker compose logs -f fastapi_vibe_coding_redis_svc

d-db-and-redis:
	docker compose up -d fastapi_vibe_coding_db_svc fastapi_vibe_coding_redis_svc

d-db-and-redis-down:
	docker compose down fastapi_vibe_coding_db_svc fastapi_vibe_coding_redis_svc

d-db-and-redis-restart:
	docker compose restart fastapi_vibe_coding_db_svc fastapi_vibe_coding_redis_svc

d-up:
	docker compose up -d

d-down:
	docker compose down

d-restart:
	docker compose restart

d-logs:
	docker compose logs -f

d-logs-app:
	docker compose logs -f fastapi_vibe_coding_app_svc

d-ps:
	docker compose ps

d-build:
	docker compose build

d-pull:
	docker compose pull

d-push:
	docker compose push

d-exec:
	docker exec -it fastapi_vibe_coding_app_svc /bin/bash

d-supervisor-logs:
	docker exec -it fastapi_vibe_coding_app_svc tail -f /var/log/supervisor/supervisord.log

d-uvicorn-logs:
	docker exec -it fastapi_vibe_coding_app_svc tail -f /var/log/supervisor/uvicorn.log

d-gunicorn-logs:
	docker exec -it fastapi_vibe_coding_app_svc tail -f /var/log/supervisor/gunicorn_error.log

d-all-logs:
	docker exec -it fastapi_vibe_coding_app_svc sh -c "tail -f /var/log/supervisor/*.log"

# ============================================================================
# HELP COMMAND
# ============================================================================

help:
	@echo "Available Makefile commands:"
	@echo ""
	@echo "== Development Commands =="
	@echo "  run                    Run the FastAPI server (Gunicorn + Uvicorn)"
	@echo "  run-dev                Run development server with auto-reload"
	@echo "  kill-port              Kill processes using port 8000"
	@echo "  shell                  Start Python shell"
	@echo "  run-worker             Start Dramatiq worker"
	@echo ""
	@echo "== Setup & Installation =="
	@echo "  init                   Initialize venv and install dependencies"
	@echo "  install                Install all dependencies from pyproject.toml"
	@echo "  install-legacy         Install from requirements files (deprecated)"
	@echo ""
	@echo "== Dependency Management (uv.lock workflow) =="
	@echo "  add-package            Add package to production dependencies"
	@echo "      Usage: make add-package PACKAGE=requests [VERSION=2.31.0]"
	@echo "  add-dev-package        Add package to dev dependencies"
	@echo "      Usage: make add-dev-package PACKAGE=pytest [VERSION=8.3.3]"
	@echo "  remove-package         Remove package from production dependencies"
	@echo "      Usage: make remove-package PACKAGE=requests"
	@echo "  remove-dev-package     Remove package from dev dependencies"
	@echo "      Usage: make remove-dev-package PACKAGE=pytest"
	@echo "  compile-deps           Lock dependencies from pyproject.toml"
	@echo "  update-deps            Upgrade all dependencies to latest"
	@echo "  package-sync           Upgrade + lock + sync dependencies"
	@echo "  export-requirements    Export uv.lock to requirements.txt (for CI/CD)"
	@echo ""
	@echo "== Database Migration Commands =="
	@echo "  makemigrations MSG='message'  Create new migration"
	@echo "  migrate                       Apply migrations"
	@echo "  migrate-downgrade             Downgrade one migration"
	@echo "  migrate-reset                 Reset all migrations"
	@echo "  migrate-history               Show migration history"
	@echo "  migrate-current               Show current migration"
	@echo "  migrate-show                  Show migration details"
	@echo "  db-init                       Initialize database"
	@echo "  db-reset                      Reset database"
	@echo ""
	@echo "== Testing & Quality =="
	@echo "  pytest                 Run all tests with coverage (default)"
	@echo "  pytest-v               Run tests in verbose mode"
	@echo "  pytest-q               Run tests in quiet mode"
	@echo "  pytest-lf              Run only last failed tests"
	@echo "  pytest-x               Stop after first failure"
	@echo "  pytest-slow            Show 10 slowest tests"
	@echo "  pytest-k K=term        Run tests matching keyword"
	@echo "  pytest-w               Run tests with warnings"
	@echo "  pytest-open-report     Open HTML coverage report"
	@echo "  test-fast              Run fast tests (exclude slow)"
	@echo "  test-api               Run API tests only"
	@echo "  isort_check            Check import sorting"
	@echo "  black_check            Check code formatting"
	@echo "  flake8                 Run flake8 linter"
	@echo "  ruff                   Run ruff linter"
	@echo "  ruff-fix               Run ruff with auto-fix"
	@echo "  static-tests           Run all static checks"
	@echo "  format                 Format code (isort + black)"
	@echo ""
	@echo "== Docker Commands =="
	@echo "  d-shell                Shell into app container"
	@echo "  d-db                   Start database container"
	@echo "  d-redis                Start Redis container"
	@echo "  d-db-logs              Show database logs"
	@echo "  d-redis-logs           Show Redis logs"
	@echo "  d-db-and-redis         Start DB and Redis"
	@echo "  d-db-and-redis-down    Stop DB and Redis"
	@echo "  d-db-and-redis-restart Restart DB and Redis"
	@echo "  d-up                   Start all containers"
	@echo "  d-down                 Stop all containers"
	@echo "  d-restart              Restart all containers"
	@echo "  d-logs                 Show all logs"
	@echo "  d-logs-app             Show app logs"
	@echo "  d-ps                   Show running containers"
	@echo "  d-build                Build containers"
	@echo "  d-supervisor-logs      Show Supervisor logs"
	@echo "  d-uvicorn-logs         Show Uvicorn logs"
	@echo "  d-gunicorn-logs        Show Gunicorn logs"
	@echo "  d-all-logs             Show all Supervisor logs"
	@echo ""
	@echo "== Examples =="
	@echo "  make add-package PACKAGE=httpx VERSION=0.25.0"
	@echo "  make makemigrations MSG='add animals table'"
	@echo "  make migrate"
	@echo "  make pytest-k K=test_animals"
	@echo "  make test-api"

.PHONY: run run-dev kill-port shell init install install-legacy add-package add-dev-package remove-package remove-dev-package compile-deps update-deps package-sync export-requirements makemigrations migrate migrate-downgrade migrate-reset migrate-history migrate-current migrate-show db-init db-reset pytest-run pytest-v pytest-q pytest-lf pytest-x pytest-slow pytest-k pytest-w dynamic-test run-tests pytest test pytest-open-report test-report test-fast test-api isort_check black_check flake8 ruff ruff-fix static-tests format d-shell d-db d-redis d-db-logs d-redis-logs d-db-and-redis d-db-and-redis-down d-db-and-redis-restart d-up d-down d-restart d-logs d-logs-app d-ps d-build d-pull d-push d-exec d-supervisor-logs d-uvicorn-logs d-gunicorn-logs d-all-logs help run-worker
