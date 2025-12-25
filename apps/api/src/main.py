"""SQL2.AI API - Main FastAPI Application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import schemas, queries, migrations, telemetry, connections


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    print(f"Starting SQL2.AI API v{settings.VERSION}")
    yield
    # Shutdown
    print("Shutting down SQL2.AI API")


app = FastAPI(
    title="SQL2.AI API",
    description="AI-Driven Database Development Platform API",
    version=settings.VERSION,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(schemas.router, prefix="/api/schemas", tags=["schemas"])
app.include_router(queries.router, prefix="/api/queries", tags=["queries"])
app.include_router(migrations.router, prefix="/api/migrations", tags=["migrations"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "SQL2.AI API", "version": settings.VERSION}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
