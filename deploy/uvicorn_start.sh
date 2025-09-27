#!/usr/bin/env bash
set -euo pipefail

# Defaults (can be overridden via env vars)
APP_MODULE=${APP_MODULE:-app.main:app}
HOST=${HOST:-0.0.0.0}
PORT=${PORT:-8000}
WORKERS=${WORKERS:-1}
RELOAD=${RELOAD:-false}
UVICORN_CMD=${UVICORN_CMD:-uvicorn}

OPTS=("$APP_MODULE" --host "$HOST" --port "$PORT")

# Use workers only when not reloading (common dev vs prod split)
if [[ "$RELOAD" == "true" ]]; then
  OPTS+=(--reload)
else
  OPTS+=(--workers "$WORKERS")
fi

exec "$UVICORN_CMD" "${OPTS[@]}"
