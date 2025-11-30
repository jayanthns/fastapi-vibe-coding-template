#!/usr/bin/env bash
set -euo pipefail

# Environment variables are loaded by Docker or system environment
echo "Using system environment variables..."

echo "DISPLAYING THE ENVIRONMENT VARIABLES..."
echo "APP_MODULE: ${APP_MODULE:-src.main:app}"
echo "HOST: ${HOST:-0.0.0.0}"
echo "PORT: ${PORT:-8000}"
echo "WORKERS: ${WORKERS:-1}"
echo "RELOAD: ${RELOAD:-false}"
echo "GUNICORN_CMD: ${GUNICORN_CMD:-gunicorn}"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Database migrations completed."

# Defaults (can be overridden via env vars)
APP_MODULE=${APP_MODULE:-src.main:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-false}
GUNICORN_CMD=${GUNICORN_CMD:-gunicorn}

OPTS=(
  "$APP_MODULE"
  -k uvicorn.workers.UvicornWorker
  -b "$HOST:$PORT"
)

# Use reload in dev, workers in prod
if [[ "$RELOAD" == "true" ]]; then
  OPTS+=(--reload)
else
  OPTS+=(-w "$WORKERS")
fi

# Always show workers in the echo, even if reload is set
echo "Running: $GUNICORN_CMD $APP_MODULE -k uvicorn.workers.UvicornWorker -b $HOST:$PORT -w $WORKERS ${RELOAD:+--reload}"

# Execute the command
exec "$GUNICORN_CMD" "${OPTS[@]}"
