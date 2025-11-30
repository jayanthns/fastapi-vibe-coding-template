#!/bin/bash
set -e

# Load environment variables from env/.env file
echo "Loading the environment variables..."
if [ -f env/.env ]; then
    set -a
    . env/.env || { echo "Failed to load environment variables"; exit 1; }
    set +a
    echo "Environment variables loaded successfully."
else
    echo "Warning: env/.env file not found. Skipping environment variable loading."
fi

# Configuration Variables
PROCESSES=${DRAMATIQ_PROCESSES:-1}
THREADS=${DRAMATIQ_THREADS:-1}

echo "Starting Dramatiq worker with processes=${PROCESSES}, threads=${THREADS}"

# Start Dramatiq worker
exec dramatiq src.worker \
    --processes $PROCESSES \
    --threads $THREADS
