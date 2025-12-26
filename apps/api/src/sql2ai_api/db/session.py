"""Database session and connection management."""

from typing import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker, Session

from sql2ai_api.config import settings


# Async engine for FastAPI
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=settings.database_pool_size,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Sync engine for migrations and scripts
sync_database_url = settings.DATABASE_URL.replace("+asyncpg", "")
engine = create_engine(
    sync_database_url,
    echo=settings.DEBUG,
    pool_size=settings.database_pool_size,
    pool_pre_ping=True,
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

SessionLocal = sessionmaker(
    engine,
    class_=Session,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Alias for FastAPI dependency injection
get_db = get_async_session


@asynccontextmanager
async def get_tenant_session(tenant_id: str) -> AsyncGenerator[AsyncSession, None]:
    """Get a session with tenant context set for RLS."""
    async with AsyncSessionLocal() as session:
        try:
            # Set tenant context for Row-Level Security
            await session.execute(
                text("SET app.current_tenant_id = :tenant_id"),
                {"tenant_id": tenant_id},
            )
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database (create tables if needed)."""
    from sql2ai_api.db.base import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await async_engine.dispose()
