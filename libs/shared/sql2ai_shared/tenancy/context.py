"""Tenant context management using context variables."""

from contextvars import ContextVar
from contextlib import contextmanager
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TenantLimits(BaseModel):
    """Resource limits for a tenant tier."""

    max_databases: int = Field(description="Maximum database connections (-1 = unlimited)")
    max_queries_per_day: int = Field(description="Maximum queries per day (-1 = unlimited)")
    max_ai_tokens_per_month: int = Field(description="Maximum AI tokens per month (-1 = unlimited)")
    max_users: int = Field(description="Maximum users (-1 = unlimited)")
    retention_days: int = Field(description="Data retention in days")
    features: List[str] = Field(description="Enabled feature flags")


class Tenant(BaseModel):
    """Tenant model with settings and limits."""

    id: str
    name: str
    slug: str
    tier: str = Field(description="Pricing tier: free, pro, enterprise")
    settings: dict = Field(default_factory=dict)
    limits: TenantLimits
    status: str = Field(default="active", description="active, suspended, deleted")
    created_at: datetime
    updated_at: datetime

    def has_feature(self, feature: str) -> bool:
        """Check if tenant has access to a feature."""
        if "*" in self.limits.features:
            return True
        return feature in self.limits.features

    def is_unlimited(self, resource: str) -> bool:
        """Check if a resource limit is unlimited."""
        limit_map = {
            "databases": self.limits.max_databases,
            "queries": self.limits.max_queries_per_day,
            "ai_tokens": self.limits.max_ai_tokens_per_month,
            "users": self.limits.max_users,
        }
        return limit_map.get(resource, 0) == -1


class TenantContext(BaseModel):
    """Request-scoped tenant context."""

    tenant: Tenant
    user_id: Optional[str] = None
    request_id: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


# Context variable for request-scoped tenant
_current_tenant: ContextVar[Optional[Tenant]] = ContextVar("current_tenant", default=None)
_current_context: ContextVar[Optional[TenantContext]] = ContextVar("tenant_context", default=None)


def get_current_tenant() -> Optional[Tenant]:
    """Get the current tenant from context."""
    return _current_tenant.get()


def get_current_context() -> Optional[TenantContext]:
    """Get the full tenant context."""
    return _current_context.get()


def set_current_tenant(tenant: Optional[Tenant]) -> None:
    """Set the current tenant in context."""
    _current_tenant.set(tenant)


def set_current_context(context: Optional[TenantContext]) -> None:
    """Set the full tenant context."""
    _current_context.set(context)
    if context:
        _current_tenant.set(context.tenant)
    else:
        _current_tenant.set(None)


@contextmanager
def tenant_context(tenant: Tenant, **kwargs):
    """Context manager for tenant-scoped operations.

    Usage:
        with tenant_context(tenant, user_id="123", request_id="req-456"):
            # All operations here are tenant-scoped
            results = await query_service.execute(sql)
    """
    from ulid import ULID

    context = TenantContext(
        tenant=tenant,
        request_id=kwargs.get("request_id", str(ULID())),
        user_id=kwargs.get("user_id"),
        ip_address=kwargs.get("ip_address"),
        user_agent=kwargs.get("user_agent"),
    )

    token = _current_context.set(context)
    tenant_token = _current_tenant.set(tenant)
    try:
        yield context
    finally:
        _current_context.reset(token)
        _current_tenant.reset(tenant_token)
