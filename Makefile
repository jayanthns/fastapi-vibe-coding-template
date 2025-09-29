# Detect the operating system
ifeq ($(OS),Windows_NT)
	# Windows
	VENV_ACTIVATE = .\venv\Scripts\activate
else
	# Unix-based systems (Linux/Mac)
	VENV_ACTIVATE = source ./venv/bin/activate
endif

run:
	@echo "Running FastAPI server..."
	@$(VENV_ACTIVATE) && uvicorn main:app --reload

venv_init:
	python3 -m venv venv
	@$(VENV_ACTIVATE) && python -m pip install --upgrade uv pip-tools pip wheel

update-deps:
	@$(VENV_ACTIVATE) && python -m pip install --upgrade pip-tools pip wheel
	@$(VENV_ACTIVATE) && python -m piptools compile --upgrade --resolver backtracking -o requirements/requirements.txt requirements_raw/requirements.in
	@$(VENV_ACTIVATE) && python -m piptools compile --upgrade --resolver backtracking -o requirements/local_requirements.txt requirements_raw/local_requirements.in

install-deps:
	@$(VENV_ACTIVATE) && python -m pip install --upgrade pip-tools pip wheel
	@$(VENV_ACTIVATE) && python -m pip install -r requirements/requirements.txt -r requirements/local_requirements.txt

update-package: update-deps install-deps

uv-venv-init:
	python3 -m pip install uv
	uv venv venv
	@$(VENV_ACTIVATE) && python -m pip install --upgrade uv pip-tools pip wheel

uv-update-deps:
	@$(VENV_ACTIVATE) && uv pip compile --upgrade --resolver backtracking -o requirements/requirements.txt requirements_raw/requirements.in
	@$(VENV_ACTIVATE) && uv pip compile --upgrade --resolver backtracking -o requirements/local_requirements.txt requirements_raw/local_requirements.in

uv-install-deps:
	@$(VENV_ACTIVATE) && uv pip install -r requirements/requirements.txt -r requirements/local_requirements.txt

uv-update-package: uv-update-deps uv-install-deps

pip-audit-prod:
	@echo "Running pip-audit..."
	@$(VENV_ACTIVATE) && pip-audit -r requirements/requirements.txt

pip-audit-all:
	@echo "Running pip-audit..."
	@$(VENV_ACTIVATE) && pip-audit -r requirements/requirements.txt -r requirements/local_requirements.txt

uv-pip-audit-prod:
	@echo "Running uv pip-audit..."
	@$(VENV_ACTIVATE) && uv pip-audit -r requirements/requirements.txt

uv-pip-audit-all:
	@echo "Running uv pip-audit..."
	@$(VENV_ACTIVATE) && uv pip-audit -r requirements/requirements.txt -r requirements/local_requirements.txt


d-db:
	docker compose up fastapi_vibe_coding_db_svc -d

d-app:
	docker compose up fastapi_vibe_coding_app_svc -d

d-up:
	docker compose up -d

d-down:
	docker compose down

d-logs:
	docker compose logs -f

d-logs-app:
	docker compose logs -f fastapi_vibe_coding_app_svc

# Database Migration Commands (Django-style)
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

# Database Management Commands
db-init:
	@echo "Initializing database..."
	@$(VENV_ACTIVATE) && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	@$(VENV_ACTIVATE) && alembic downgrade base && alembic upgrade head

db-seed:
	@echo "Seeding database with initial data..."
	@$(VENV_ACTIVATE) && python -c "from app.db.session import engine; from app.models.article import Base; Base.metadata.create_all(bind=engine)"

# Development Commands
dev-setup: install-deps db-init
	@echo "Development environment setup complete!"

dev-reset: db-reset
	@echo "Development database reset complete!"

# Help command
help:
	@echo "Available commands:"
	@echo ""
	@echo "Database Migration Commands:"
	@echo "  makemigrations MSG='message'  - Create new migration (like Django makemigrations)"
	@echo "  migrate                       - Apply migrations (like Django migrate)"
	@echo "  migrate-downgrade             - Downgrade one migration"
	@echo "  migrate-reset                 - Reset all migrations"
	@echo "  migrate-history               - Show migration history"
	@echo "  migrate-current               - Show current migration"
	@echo "  migrate-show                  - Show migration details"
	@echo ""
	@echo "Database Management:"
	@echo "  db-init                       - Initialize database"
	@echo "  db-reset                      - Reset database"
	@echo "  db-seed                       - Seed database with initial data"
	@echo ""
	@echo "Development:"
	@echo "  dev-setup                     - Setup development environment"
	@echo "  dev-reset                     - Reset development database"
	@echo ""
	@echo "Examples:"
	@echo "  make makemigrations MSG='add user table'"
	@echo "  make migrate"
	@echo "  make db-reset"
