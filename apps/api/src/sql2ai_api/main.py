"""SQL2.AI API - Main FastAPI Application."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
import structlog

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from sql2ai_api.config import settings
from sql2ai_api.routers import (
    schemas, queries, migrations, telemetry, connections,
    orchestrator, migrator, optimize, compliance,
    writer, codereview, version, dashboard, billing
)
from sql2ai_api.routers.webhooks import clerk_router
from sql2ai_api.middleware.auth import create_auth_middleware
from sql2ai_api.db.session import init_db, close_db

# Initialize structured logging
logger = structlog.get_logger()


def init_sentry():
    """Initialize Sentry error tracking."""
    if settings.sentry_dsn:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            release=f"sql2ai-api@{settings.VERSION}",
            traces_sample_rate=settings.sentry_traces_sample_rate,
            integrations=[FastApiIntegration(transaction_style="endpoint")],
        )
        logger.info("sentry_initialized", environment=settings.environment)


def init_posthog():
    """Initialize PostHog analytics."""
    if settings.posthog_api_key:
        from posthog import Posthog
        posthog = Posthog(
            project_api_key=settings.posthog_api_key,
            host=settings.posthog_host,
        )
        logger.info("posthog_initialized")
        return posthog
    return None


async def init_redis():
    """Initialize Redis connection."""
    try:
        import redis.asyncio as redis
        client = redis.from_url(settings.redis_url)
        await client.ping()
        logger.info("redis_connected", url=settings.redis_url)
        return client
    except Exception as e:
        logger.warning("redis_connection_failed", error=str(e))
        return None


async def init_ai_provider():
    """Initialize AI provider with LiteLLM."""
    try:
        from sql2ai_shared.ai.providers import AIConfig, create_ai_provider

        config = AIConfig(
            default_model=settings.default_llm_model,
            embedding_model=settings.default_embedding_model,
        )

        if settings.openai_api_key.get_secret_value():
            config.openai_api_key = settings.openai_api_key

        if settings.ANTHROPIC_API_KEY:
            from pydantic import SecretStr
            config.anthropic_api_key = SecretStr(settings.ANTHROPIC_API_KEY)

        provider = create_ai_provider(config)
        logger.info("ai_provider_initialized", model=settings.default_llm_model)
        return provider
    except Exception as e:
        logger.warning("ai_provider_init_failed", error=str(e))
        return None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info(
        "app_starting",
        version=settings.VERSION,
        environment=settings.environment,
    )

    # Initialize integrations
    init_sentry()
    app.state.posthog = init_posthog()
    app.state.redis = await init_redis()
    app.state.ai_provider = await init_ai_provider()

    # Initialize database (create tables if dev mode)
    if settings.is_development:
        try:
            await init_db()
            logger.info("database_tables_created")
        except Exception as e:
            logger.warning("database_init_skipped", error=str(e))

    logger.info("app_started", version=settings.VERSION)

    yield

    # Shutdown
    logger.info("app_shutting_down")

    if app.state.redis:
        await app.state.redis.close()

    await close_db()

    logger.info("app_shutdown_complete")


app = FastAPI(
    title="SQL2.AI API",
    description="AI-Driven Database Development Platform API",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Clerk authentication middleware
auth_middleware = create_auth_middleware(
    excluded_paths=[
        "/",
        "/health",
        "/ready",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        "/api/webhooks/clerk",  # Webhooks have their own signature verification
        "/api/billing/webhook",  # Stripe webhook has signature verification
        "/api/billing/pricing",  # Public pricing info
    ]
)
app.middleware("http")(auth_middleware)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add request ID to all requests for tracing."""
    from ulid import ULID
    request_id = str(ULID())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    request_id = getattr(request.state, "request_id", "unknown")
    logger.error(
        "unhandled_exception",
        request_id=request_id,
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": request_id,
        },
    )


# Include routers
app.include_router(schemas.router, prefix="/api/schemas", tags=["schemas"])
app.include_router(queries.router, prefix="/api/queries", tags=["queries"])
app.include_router(migrations.router, prefix="/api/migrations", tags=["migrations"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])
app.include_router(connections.router, prefix="/api/connections", tags=["connections"])
app.include_router(orchestrator.router, prefix="/api/orchestrator", tags=["orchestrator"])
app.include_router(migrator.router, prefix="/api/migrator", tags=["migrator"])
app.include_router(optimize.router, prefix="/api/optimize", tags=["optimize"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["compliance"])
app.include_router(writer.router, prefix="/api/writer", tags=["writer"])
app.include_router(codereview.router, prefix="/api/codereview", tags=["codereview"])
app.include_router(version.router, prefix="/api/version", tags=["version"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(billing.router, prefix="/api/billing", tags=["billing"])
app.include_router(clerk_router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "SQL2.AI API",
        "version": settings.VERSION,
        "environment": settings.environment,
    }


@app.get("/health")
async def health_check(request: Request) -> dict:
    """Health check endpoint with dependency status."""
    health = {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.environment,
        "checks": {},
    }

    # Check Redis
    if request.app.state.redis:
        try:
            await request.app.state.redis.ping()
            health["checks"]["redis"] = {"status": "healthy"}
        except Exception as e:
            health["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
            health["status"] = "degraded"
    else:
        health["checks"]["redis"] = {"status": "not_configured"}

    # Check AI Provider
    if request.app.state.ai_provider:
        health["checks"]["ai"] = {"status": "healthy"}
    else:
        health["checks"]["ai"] = {"status": "not_configured"}

    return health


@app.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Kubernetes readiness probe."""
    return {"status": "ready"}
