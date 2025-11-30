#!/bin/sh

# Generic entrypoint script that can be used for various services
# This script loads environment variables and executes the command passed to it

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

# Execute the command passed as arguments
echo "Executing command: $@"
exec "$@"
