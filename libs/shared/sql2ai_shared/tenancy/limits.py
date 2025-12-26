"""Tenant tier limits and quota checking."""

from typing import Optional
from sql2ai_shared.tenancy.context import TenantLimits, get_current_tenant


# Tier limit definitions
TIER_LIMITS = {
    "free": TenantLimits(
        max_databases=1,
        max_queries_per_day=100,
        max_ai_tokens_per_month=50_000,
        max_users=1,
        retention_days=7,
        features=["query", "basic_monitor"],
    ),
    "pro": TenantLimits(
        max_databases=10,
        max_queries_per_day=10_000,
        max_ai_tokens_per_month=1_000_000,
        max_users=10,
        retention_days=90,
        features=[
            "query",
            "monitor",
            "optimize",
            "migrate",
            "ai_assist",
            "code_review",
            "version_control",
        ],
    ),
    "enterprise": TenantLimits(
        max_databases=-1,  # Unlimited
        max_queries_per_day=-1,
        max_ai_tokens_per_month=-1,
        max_users=-1,
        retention_days=365,
        features=["*"],  # All features
    ),
}


class LimitExceededError(Exception):
    """Raised when a tenant exceeds their quota."""

    def __init__(self, resource: str, limit: int, current: int):
        self.resource = resource
        self.limit = limit
        self.current = current
        super().__init__(
            f"Limit exceeded for {resource}: {current}/{limit}. "
            f"Please upgrade your plan or contact support."
        )


async def check_limit(
    resource: str,
    current_usage: int,
    increment: int = 1,
    tenant: Optional["Tenant"] = None,
) -> bool:
    """Check if an operation would exceed tenant limits.

    Args:
        resource: The resource type (databases, queries, ai_tokens, users)
        current_usage: Current usage count
        increment: How much to increment (default 1)
        tenant: Optional tenant (uses current context if not provided)

    Returns:
        True if within limits

    Raises:
        LimitExceededError: If limit would be exceeded
    """
    if tenant is None:
        tenant = get_current_tenant()

    if tenant is None:
        # No tenant context - apply free tier limits
        limits = TIER_LIMITS["free"]
    else:
        limits = tenant.limits

    limit_map = {
        "databases": limits.max_databases,
        "queries": limits.max_queries_per_day,
        "ai_tokens": limits.max_ai_tokens_per_month,
        "users": limits.max_users,
    }

    limit = limit_map.get(resource)
    if limit is None:
        raise ValueError(f"Unknown resource type: {resource}")

    # -1 means unlimited
    if limit == -1:
        return True

    if current_usage + increment > limit:
        raise LimitExceededError(resource, limit, current_usage + increment)

    return True


def get_tier_limits(tier: str) -> TenantLimits:
    """Get limits for a specific tier."""
    if tier not in TIER_LIMITS:
        raise ValueError(f"Unknown tier: {tier}. Valid tiers: {list(TIER_LIMITS.keys())}")
    return TIER_LIMITS[tier]


def get_feature_tiers(feature: str) -> list[str]:
    """Get which tiers have access to a feature."""
    tiers = []
    for tier_name, limits in TIER_LIMITS.items():
        if "*" in limits.features or feature in limits.features:
            tiers.append(tier_name)
    return tiers
