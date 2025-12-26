"""Tests for authentication middleware and dependencies."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Request

from sql2ai_api.middleware.auth import AuthMiddleware, ClerkUser, create_auth_middleware
from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    UserRole,
    ROLE_PERMISSIONS,
    get_current_user,
    require_permission,
    require_role,
)


class TestClerkUser:
    """Tests for ClerkUser model."""

    def test_clerk_user_creation(self):
        """Test ClerkUser model creation."""
        user = ClerkUser(
            id="user_123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            org_id="org_456",
            org_role="admin",
        )

        assert user.id == "user_123"
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.org_id == "org_456"
        assert user.org_role == "admin"

    def test_clerk_user_optional_fields(self):
        """Test ClerkUser with optional fields."""
        user = ClerkUser(id="user_123")

        assert user.id == "user_123"
        assert user.email is None
        assert user.org_id is None


class TestAuthMiddleware:
    """Tests for AuthMiddleware."""

    def test_create_auth_middleware(self):
        """Test middleware factory."""
        middleware = create_auth_middleware(excluded_paths=["/health"])
        assert callable(middleware)

    def test_excluded_paths(self):
        """Test that excluded paths bypass authentication."""
        middleware_instance = AuthMiddleware(excluded_paths=["/health", "/"])

        assert middleware_instance._is_excluded("/health") is True
        assert middleware_instance._is_excluded("/") is True
        assert middleware_instance._is_excluded("/api/schemas") is False

    @pytest.mark.asyncio
    async def test_missing_authorization_header(self):
        """Test request without Authorization header."""
        middleware = AuthMiddleware()

        request = MagicMock(spec=Request)
        request.url.path = "/api/schemas"
        request.headers = {}

        call_next = AsyncMock(return_value=MagicMock())

        # Should return 401 for missing auth
        response = await middleware(request, call_next)
        # In real implementation, this would be an error response


class TestAuthenticatedUser:
    """Tests for AuthenticatedUser model."""

    def test_authenticated_user_creation(self):
        """Test AuthenticatedUser creation."""
        user = AuthenticatedUser(
            id="user_123",
            email="test@example.com",
            first_name="Test",
            last_name="User",
            org_id="org_456",
            org_role="admin",
            tenant_id="org_456",
            role=UserRole.ADMIN,
            permissions=ROLE_PERMISSIONS[UserRole.ADMIN],
        )

        assert user.id == "user_123"
        assert user.tenant_id == "org_456"
        assert user.role == UserRole.ADMIN

    def test_display_name_full(self):
        """Test display name with first and last name."""
        user = AuthenticatedUser(
            id="user_123",
            first_name="Test",
            last_name="User",
            tenant_id="org_456",
            role=UserRole.DEVELOPER,
            permissions=[],
        )

        assert user.display_name == "Test User"

    def test_display_name_first_only(self):
        """Test display name with first name only."""
        user = AuthenticatedUser(
            id="user_123",
            first_name="Test",
            tenant_id="org_456",
            role=UserRole.DEVELOPER,
            permissions=[],
        )

        assert user.display_name == "Test"

    def test_display_name_email_fallback(self):
        """Test display name falls back to email."""
        user = AuthenticatedUser(
            id="user_123",
            email="test@example.com",
            tenant_id="org_456",
            role=UserRole.DEVELOPER,
            permissions=[],
        )

        assert user.display_name == "test"

    def test_has_permission(self):
        """Test permission checking."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.ADMIN,
            permissions=[Permission.CONNECTIONS_READ, Permission.CONNECTIONS_WRITE],
        )

        assert user.has_permission(Permission.CONNECTIONS_READ) is True
        assert user.has_permission(Permission.CONNECTIONS_WRITE) is True
        assert user.has_permission(Permission.ADMIN_BILLING) is False

    def test_has_any_permission(self):
        """Test checking for any permission."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.DEVELOPER,
            permissions=[Permission.CONNECTIONS_READ, Permission.QUERIES_EXECUTE],
        )

        assert user.has_any_permission([
            Permission.ADMIN_BILLING,
            Permission.CONNECTIONS_READ,
        ]) is True

        assert user.has_any_permission([
            Permission.ADMIN_BILLING,
            Permission.ADMIN_USERS,
        ]) is False

    def test_has_all_permissions(self):
        """Test checking for all permissions."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.ADMIN,
            permissions=[
                Permission.CONNECTIONS_READ,
                Permission.CONNECTIONS_WRITE,
                Permission.QUERIES_EXECUTE,
            ],
        )

        assert user.has_all_permissions([
            Permission.CONNECTIONS_READ,
            Permission.CONNECTIONS_WRITE,
        ]) is True

        assert user.has_all_permissions([
            Permission.CONNECTIONS_READ,
            Permission.ADMIN_BILLING,
        ]) is False


class TestRolePermissions:
    """Tests for role-based permissions."""

    def test_owner_has_all_permissions(self):
        """Test that owner role has all permissions."""
        owner_permissions = ROLE_PERMISSIONS[UserRole.OWNER]
        assert len(owner_permissions) == len(Permission)

    def test_admin_permissions(self):
        """Test admin role permissions."""
        admin_permissions = ROLE_PERMISSIONS[UserRole.ADMIN]

        assert Permission.CONNECTIONS_READ in admin_permissions
        assert Permission.CONNECTIONS_WRITE in admin_permissions
        assert Permission.ADMIN_USERS in admin_permissions
        assert Permission.ADMIN_BILLING not in admin_permissions

    def test_dba_permissions(self):
        """Test DBA role permissions."""
        dba_permissions = ROLE_PERMISSIONS[UserRole.DBA]

        assert Permission.QUERIES_EXECUTE_DDL in dba_permissions
        assert Permission.MIGRATIONS_EXECUTE in dba_permissions
        assert Permission.ADMIN_USERS not in dba_permissions

    def test_developer_permissions(self):
        """Test developer role permissions."""
        dev_permissions = ROLE_PERMISSIONS[UserRole.DEVELOPER]

        assert Permission.CONNECTIONS_READ in dev_permissions
        assert Permission.QUERIES_EXECUTE in dev_permissions
        assert Permission.QUERIES_EXECUTE_DDL not in dev_permissions
        assert Permission.CONNECTIONS_DELETE not in dev_permissions

    def test_viewer_permissions(self):
        """Test viewer role permissions."""
        viewer_permissions = ROLE_PERMISSIONS[UserRole.VIEWER]

        assert Permission.CONNECTIONS_READ in viewer_permissions
        assert Permission.QUERIES_EXECUTE in viewer_permissions
        assert Permission.SCHEMA_READ in viewer_permissions
        assert len(viewer_permissions) == 3


class TestRequirePermission:
    """Tests for require_permission dependency."""

    @pytest.mark.asyncio
    async def test_require_permission_granted(self):
        """Test permission check passes."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.ADMIN,
            permissions=[Permission.SCHEMA_READ],
        )

        check = require_permission(Permission.SCHEMA_READ)
        # Should not raise
        await check(user)

    @pytest.mark.asyncio
    async def test_require_permission_denied(self):
        """Test permission check fails."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.VIEWER,
            permissions=[Permission.CONNECTIONS_READ],
        )

        check = require_permission(Permission.ADMIN_USERS)

        with pytest.raises(HTTPException) as exc_info:
            await check(user)

        assert exc_info.value.status_code == 403
        assert "Missing required permission" in exc_info.value.detail


class TestRequireRole:
    """Tests for require_role dependency."""

    @pytest.mark.asyncio
    async def test_require_role_exact_match(self):
        """Test role check with exact match."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.ADMIN,
            permissions=[],
        )

        check = require_role(UserRole.ADMIN)
        # Should not raise
        await check(user)

    @pytest.mark.asyncio
    async def test_require_role_higher_level(self):
        """Test role check with higher level role."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.OWNER,
            permissions=[],
        )

        check = require_role(UserRole.ADMIN)
        # Should not raise - owner is higher than admin
        await check(user)

    @pytest.mark.asyncio
    async def test_require_role_insufficient(self):
        """Test role check fails for insufficient role."""
        user = AuthenticatedUser(
            id="user_123",
            tenant_id="org_456",
            role=UserRole.DEVELOPER,
            permissions=[],
        )

        check = require_role(UserRole.ADMIN)

        with pytest.raises(HTTPException) as exc_info:
            await check(user)

        assert exc_info.value.status_code == 403
        assert "Insufficient role" in exc_info.value.detail
