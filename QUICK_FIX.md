# Quick Fix: Install Dependencies and Run Tests

## Issue
`make pytest` fails because dev dependencies aren't installed.

## Solution

The project uses `uv` for package management. Follow these steps:

### Step 1: Install Dev Dependencies

```bash
# Option 1: Using uv (recommended)
source ./venv/bin/activate
uv pip install pytest pytest-asyncio pytest-cov pytest-timeout httpx ruff

# Option 2: Reinstall everything with dev dependencies
uv pip sync pyproject.toml --extra dev
```

### Step 2: Run Tests

```bash
make pytest
```

## Alternative: Manual Test Run

If make pytest still fails, run pytest directly:

```bash
source ./venv/bin/activate
python -m pytest --cov=src --cov-report=html:coverage_html_report --cov-report=term-missing
```

## What's Installed

After running `make install`, you have:
- ✅ FastAPI and core dependencies
- ✅ python-multipart (for file uploads)
- ❌ Dev dependencies (pytest, ruff, etc.) - **Need to install separately**

## Fix the Makefile

Update the `install` command in Makefile to include dev dependencies:

```makefile
install:
	@echo "Installing dependencies..."
	@$(VENV_ACTIVATE) && uv pip sync pyproject.toml --extra dev
```

## Quick Commands

```bash
# Install everything (production + dev)
source ./venv/bin/activate && uv pip install -e ".[dev]"

# Or install from pyproject.toml with dev extras
source ./venv/bin/activate && uv pip install pytest pytest-asyncio pytest-cov pytest-timeout httpx ruff

# Then run tests
make pytest
```

## Expected Test Results

Once dependencies are installed, you should see:
- Tests for database pings
- Tests for cache pings  
- Tests for utilities
- Some tests may fail due to missing archived apps (expected)

## Next Steps After Tests Pass

1. Create database migrations for new tables (animals, audit_logs)
2. Write tests for new apps (animals, audit, files)
3. Fix any failing tests
4. Update documentation
