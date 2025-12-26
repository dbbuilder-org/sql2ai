"""Pytest configuration and fixtures."""

import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import AsyncClient

from sql2ai_api.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_app() -> FastAPI:
    """Get test FastAPI application."""
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Get test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Get async test client."""
    async with AsyncClient(app=test_app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def mock_clerk_user() -> dict:
    """Mock Clerk user data."""
    return {
        "id": "user_test123",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "org_id": "org_test456",
        "org_role": "admin",
    }


@pytest.fixture
def mock_jwt_token() -> str:
    """Mock JWT token."""
    return "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyX3Rlc3QxMjMiLCJlbWFpbCI6InRlc3RAZXhhbXBsZS5jb20iLCJvcmdfaWQiOiJvcmdfdGVzdDQ1NiIsIm9yZ19yb2xlIjoiYWRtaW4ifQ.mock_signature"


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_connection() -> MagicMock:
    """Mock database connection model."""
    from sql2ai_api.models.connection import DatabaseType

    conn = MagicMock()
    conn.id = "conn_test789"
    conn.tenant_id = "org_test456"
    conn.name = "Test Connection"
    conn.db_type = DatabaseType.SQLSERVER
    conn.host = "localhost"
    conn.port = 1433
    conn.database = "TestDB"
    conn.username = "sa"
    conn.encrypted_password = None
    conn.password_secret_id = None
    conn.trust_server_certificate = True
    conn.encrypt = False
    conn.deleted_at = None
    return conn
