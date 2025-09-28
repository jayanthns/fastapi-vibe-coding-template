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
