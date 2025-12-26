#!/bin/bash
set -e

echo "=== SQL2.AI API Startup ==="

# Run database migrations
echo "Running database migrations..."
cd /app
python -m alembic -c /app/alembic.ini upgrade head

echo "Migrations complete."

# Start the API server
echo "Starting API server..."
exec uvicorn sql2ai_api.main:app --host 0.0.0.0 --port ${PORT:-8000}
