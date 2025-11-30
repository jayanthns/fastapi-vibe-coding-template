# Deployment Guide

## Docker Deployment

The project is designed to be deployed using **Docker**.

### 1. Dockerfile
The `Dockerfile` is a multi-stage build based on `python:3.12-slim`.
It:
1. Installs system dependencies.
2. Installs Python dependencies using `uv`.
3. Copies the application code.
4. Sets up `supervisord` to manage processes.
5. Runs migrations on startup.

### 2. Entrypoint
The entrypoint script (`deploy/entrypoint_scripts/gunicorn_entrypoint.sh`) handles:
- Environment variable loading.
- Starting `supervisord`.

`supervisord` then starts `gunicorn`, which manages `uvicorn` workers.

### 3. Building and Running

```bash
docker compose build
docker compose up -d
```

### 4. Environment Variables
Ensure all required environment variables are set in `.env` (or injected by your orchestration platform).
See `.env.example` for the list of variables.

Key variables:
- `DATABASE_URL`: Connection string for PostgreSQL.
- `REDIS_URL`: Connection string for Redis.
- `SECRET_KEY`: Security key for JWT/Sessions.
- `ENVIRONMENT`: `production` or `development`.

## Production Considerations

### 1. Database Migrations
Migrations are automatically applied on container startup via `deploy/shell_scripts/gunicorn_start.sh`.
Ensure the database user has permissions to alter tables.

### 2. Static Files
FastAPI serves API responses, but if you have static files (e.g., for a frontend), they should be served by a reverse proxy like **Nginx** or a CDN.

### 3. HTTPS
Terminate SSL/TLS at the load balancer or reverse proxy (e.g., Nginx, AWS ALB) before traffic reaches the container.

### 4. Monitoring
- **Logs**: JSON logs are output to stdout/stderr. Integrate with a log aggregator (e.g., ELK, Datadog).
- **Health Checks**: Use `/health` endpoint for load balancer health checks.
- **Metrics**: Prometheus metrics are available (if configured).

## Scaling
The application is stateless. You can scale horizontally by adding more container instances behind a load balancer.
Ensure `REDIS_URL` points to a shared Redis instance for caching and background tasks.
