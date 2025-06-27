#!/bin/bash

# Development entrypoint script
# This script is used when the backend directory is mounted as a volume
# It activates the virtual environment and executes the provided command

source /app/.venv/bin/activate
exec "$@"
