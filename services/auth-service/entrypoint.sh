#!/bin/bash
# ============================================
# Entrypoint Script for Auth Service
# ============================================
# This script runs when the container starts:
# 1. Waits for database to be ready
# 2. Runs Alembic migrations
# 3. Starts the FastAPI application

set -e  # Exit on any error

echo "============================================"
echo "Auth Service Entrypoint"
echo "============================================"

# ============================================
# Wait for Database to be Ready
# ============================================
echo "Waiting for database to be ready..."

# Use pg_isready to check if PostgreSQL is accepting connections
# The depends_on with health check should handle this, but this is a safety net
max_retries=30
retry_count=0

while ! pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER" -d "$DATABASE_NAME" -q; do
    retry_count=$((retry_count + 1))
    if [ $retry_count -ge $max_retries ]; then
        echo "ERROR: Database not ready after $max_retries attempts. Exiting."
        exit 1
    fi
    echo "Database not ready yet. Waiting... (attempt $retry_count/$max_retries)"
    sleep 2
done

echo "Database is ready!"

# ============================================
# Run Alembic Migrations
# ============================================
echo "Running Alembic migrations..."

# Run migrations to bring database to latest version
# 'upgrade head' applies all pending migrations
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "Migrations completed successfully!"
else
    echo "ERROR: Migrations failed!"
    exit 1
fi

# ============================================
# Start the Application
# ============================================
echo "Starting FastAPI application..."
echo "============================================"

# Execute the CMD passed to the container (uvicorn command)
# Using exec replaces this shell with uvicorn, so signals are handled properly
exec "$@"

