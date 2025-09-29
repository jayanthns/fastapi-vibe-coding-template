# Background Jobs Code Cleanup

This guide helps you remove the background jobs feature from your FastAPI project if you don't need it.

## Overview

The background jobs feature is a complete example of:
- Asynchronous job processing
- Status tracking with in-memory caching
- Trace ID integration
- RESTful API endpoints
- Comprehensive testing

**If you don't need background job functionality, follow these steps to remove it:**

### 1. Remove Background Jobs API Endpoints

Delete the background jobs API file:
```bash
rm app/api/v1/background_jobs.py
```

### 2. Update API Router

Edit `app/api/urls.py` and remove the background jobs import and router:

```python
# Remove this import
from app.api.v1 import articles, background_jobs

# Remove this line
api_router.include_router(background_jobs.router, prefix="/v1", tags=["background-jobs"])

# Keep only this
from app.api.v1 import articles
api_router.include_router(articles.router, prefix="/v1/articles", tags=["articles"])
```

### 3. Remove Background Job Service

Delete the background job service files:
```bash
rm app/services/background_job_service.py
rm app/core/background_tasks.py
```

### 4. Update Main Application

Edit `app/main.py` and remove background task manager:

```python
# Remove this import
from app.core.background_tasks import background_task_manager

# Remove these lines from the lifespan function
await background_task_manager.start()
await background_task_manager.stop()
```

### 5. Remove Background Jobs Tests

Delete the background jobs test file:
```bash
rm tests/test_background_jobs.py
```

### 6. Update Documentation

Remove or update these files:
```bash
rm BACKGROUND_JOBS_API.md
rm test_background_jobs.py  # If it exists in root
```

### 7. Update README.md

Remove the background jobs section from `README.md`:
- Remove "Background Jobs API" section
- Remove background jobs examples
- Update the API endpoints list

### 8. Update TESTING.md

Remove background jobs test examples from `TESTING.md`:
- Remove `@pytest.mark.background` references
- Remove background jobs test examples
- Update test structure documentation

### 9. Update Makefile

Remove background jobs test commands from `Makefile`:
```makefile
# Remove this line
test-background:
	@echo "Running background job tests only..."
	@$(VENV_ACTIVATE) && PYTHONPATH=. pytest -m "background"
```

And update the help section to remove the background jobs test command.

### 10. Update pyproject.toml

Remove the background marker from pytest configuration:
```toml
# Remove "background: marks tests as background job tests" from markers
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
    "api: marks tests as API tests",
]
```

## Verification Steps

After cleanup, verify everything works:

1. **Test the application starts:**
   ```bash
   make run
   ```

2. **Check API endpoints:**
   ```bash
   curl http://localhost:8000/api/v1/articles/
   ```

3. **Run tests:**
   ```bash
   make test
   ```

4. **Check logs:**
   ```bash
   tail -f tmp/logs/app-*.log
   ```

## What Remains After Cleanup

After removing background jobs, you'll still have:

✅ **Core FastAPI Application**
- Article CRUD API
- Database integration (SQLAlchemy + Alembic)
- Request tracing and logging
- Health check endpoint

✅ **Development Tools**
- Makefile commands for migrations
- Testing framework (pytest)
- Code formatting (ruff)
- Documentation

✅ **Production Features**
- Docker support
- Environment configuration
- Logging system
- Trace ID middleware

## Alternative: Keep as Reference

If you want to keep the background jobs code as a reference but not use it:

1. **Comment out the router** in `app/api/urls.py`
2. **Don't start the background task manager** in `app/main.py`
3. **Keep the files** for future reference

This way you can easily re-enable it later by uncommenting the relevant lines.

## Need Help?

If you encounter any issues during cleanup:

1. Check the logs in `tmp/logs/`
2. Verify all imports are removed
3. Ensure no references remain in documentation
4. Run `make test` to verify everything works

The core application should work perfectly without the background jobs feature!
