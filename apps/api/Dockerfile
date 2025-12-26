# SQL2.AI API Dockerfile
# Multi-stage build for optimal image size

# ===========================================
# Build Stage
# ===========================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN pip install uv

# Create virtual environment
RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install shared library first
COPY libs/shared /libs/shared
RUN cd /libs/shared && uv pip install .

# Copy and install API dependencies
COPY apps/api/pyproject.toml /build/
WORKDIR /build
RUN uv pip install --no-deps .

# Install remaining dependencies
RUN uv pip install \
    fastapi>=0.109.0 \
    uvicorn[standard]>=0.27.0 \
    python-multipart>=0.0.6 \
    pydantic>=2.5.0 \
    pydantic-settings>=2.1.0 \
    email-validator>=2.1.0 \
    asyncpg>=0.29.0 \
    sqlalchemy[asyncio]>=2.0.0 \
    alembic>=1.13.0 \
    stripe>=7.0.0 \
    python-jose[cryptography]>=3.3.0 \
    passlib[bcrypt]>=1.7.4 \
    structlog>=24.1.0 \
    redis>=5.0.0 \
    httpx>=0.26.0 \
    ulid-py>=1.1.0 \
    psycopg2-binary>=2.9.0 \
    cryptography>=42.0.0

# ===========================================
# Runtime Stage
# ===========================================
FROM python:3.11-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY apps/api/src/ ./src/
COPY apps/api/alembic/ ./alembic/
COPY apps/api/alembic.ini ./alembic.ini
COPY apps/api/scripts/start.sh ./start.sh

# Make start script executable
RUN chmod +x ./start.sh

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app/src

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with migrations
CMD ["./start.sh"]
