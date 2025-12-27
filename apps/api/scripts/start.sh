#!/bin/bash
set -e

echo "=== SQL2.AI API Startup ==="

# Transform DATABASE_URL for asyncpg compatibility
# Render provides postgres:// but asyncpg needs postgresql+asyncpg://
if [ -n "$SQL2AI_DATABASE_URL" ]; then
    export SQL2AI_DATABASE_URL=$(echo "$SQL2AI_DATABASE_URL" | sed 's|^postgres://|postgresql+asyncpg://|' | sed 's|^postgresql://|postgresql+asyncpg://|')
    echo "Database URL configured for asyncpg"
fi

# Run database migrations
echo "Running database migrations..."
cd /app
python -m alembic -c /app/alembic.ini upgrade head

echo "Migrations complete."

# Start the API server
echo "Starting API server..."
exec uvicorn sql2ai_api.main:app --host 0.0.0.0 --port ${PORT:-8000}
