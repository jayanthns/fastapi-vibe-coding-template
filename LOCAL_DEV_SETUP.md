# Local Development Setup

## Running FastAPI and Dramatiq Locally (Redis/Postgres in Docker)

This setup allows you to run FastAPI and the Dramatiq worker locally while keeping Redis and Postgres in Docker containers. This makes debugging much easier.

### Prerequisites

1. **Start Docker services** (Redis & Postgres only):
   ```bash
   docker compose up -d fastapi_vibe_coding_db_svc fastapi_vibe_coding_redis_svc
   ```

2. **Verify services are running**:
   ```bash
   docker compose ps
   ```

### Environment Setup

The `.env` file is already configured for local development. Key settings:

```bash
# Database (connects to Docker Postgres)
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_USERNAME=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=fastapi_vibe_coding

# Redis (connects to Docker Redis)
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis
```

### Running FastAPI Locally

**Terminal 1 - FastAPI Server**:
```bash
# Activate virtual environment
source venv/bin/activate

# Run FastAPI with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### Running Dramatiq Worker Locally

**Terminal 2 - Dramatiq Worker**:
```bash
# Activate virtual environment
source venv/bin/activate

# Run Dramatiq worker
dramatiq src.worker --processes 1 --threads 1 --watch src
```

The `--watch src` flag enables auto-reload when code changes.

### Testing the Setup

**Terminal 3 - Test Commands**:

1. **Test hello world task**:
   ```bash
   python -c "from src.test_tasks import hello_world; hello_world.send('Local Test'); print('Task sent!')"
   ```

2. **Check worker output** in Terminal 2 - you should see:
   ```
   Hello, Local Test! Dramatiq is working!
   ```

3. **Test audit logging**:
   ```bash
   curl -X POST http://localhost:8000/api/v1/animals/ \
     -H "Content-Type: application/json" \
     -d '{"name": "Local Test Dog", "species": "Dog", "age": 5}'
   ```

4. **Check audit logs**:
   ```bash
   curl http://localhost:8000/api/v1/audit/ | python3 -m json.tool
   ```

### Debugging Tips

1. **View worker logs in real-time**: The worker runs in your terminal, so you see all output immediately

2. **Set breakpoints**: You can use `pdb` or your IDE's debugger in both FastAPI and worker code

3. **Check Redis queue**:
   ```bash
   docker compose exec fastapi_vibe_coding_redis_svc redis-cli -a redis
   > KEYS *
   > LLEN default
   ```

4. **Check Postgres**:
   ```bash
   docker compose exec fastapi_vibe_coding_db_svc psql -U postgres -d fastapi_vibe_coding
   > SELECT COUNT(*) FROM audit_logs;
   > SELECT COUNT(*) FROM background_jobs;
   ```

### Stopping Services

```bash
# Stop FastAPI: Ctrl+C in Terminal 1
# Stop Worker: Ctrl+C in Terminal 2
# Stop Docker services:
docker compose down
```

### Common Issues

1. **Port already in use**: Make sure no other services are running on ports 8000, 5432, or 6379

2. **Connection refused**: Ensure Docker services are running:
   ```bash
   docker compose ps
   ```

3. **Module not found**: Make sure you're in the project root and virtual environment is activated

4. **Database migrations**: Run migrations if needed:
   ```bash
   alembic upgrade head
   ```
