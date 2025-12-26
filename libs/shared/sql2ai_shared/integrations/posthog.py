"""PostHog product analytics and feature flags integration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import structlog

from sql2ai_shared.tenancy.context import get_current_tenant

logger = structlog.get_logger()


class PostHogConfig(BaseModel):
    """PostHog configuration."""

    api_key: str
    host: str = "https://app.posthog.com"
    personal_api_key: Optional[str] = None
    disabled: bool = False


class Events:
    """Standard event names for SQL2.AI."""

    # Onboarding
    SIGNUP_COMPLETED = "signup_completed"
    ONBOARDING_STARTED = "onboarding_started"
    ONBOARDING_COMPLETED = "onboarding_completed"
    FIRST_CONNECTION_ADDED = "first_connection_added"
    FIRST_QUERY_EXECUTED = "first_query_executed"

    # Core usage
    QUERY_EXECUTED = "query_executed"
    AI_QUERY_GENERATED = "ai_query_generated"
    AI_QUERY_APPROVED = "ai_query_approved"
    AI_QUERY_REJECTED = "ai_query_rejected"

    # Migrations
    MIGRATION_CREATED = "migration_created"
    MIGRATION_APPLIED = "migration_applied"
    MIGRATION_ROLLED_BACK = "migration_rolled_back"

    # Monitoring
    ALERT_CREATED = "alert_created"
    ALERT_TRIGGERED = "alert_triggered"
    ALERT_RESOLVED = "alert_resolved"

    # Compliance
    COMPLIANCE_SCAN_RUN = "compliance_scan_run"
    COMPLIANCE_VIOLATION_FOUND = "compliance_violation_found"
    COMPLIANCE_REPORT_GENERATED = "compliance_report_generated"

    # Features
    FEATURE_USED = "feature_used"
    REPORT_EXPORTED = "report_exported"

    # Monetization
    UPGRADE_INITIATED = "upgrade_initiated"
    UPGRADE_COMPLETED = "upgrade_completed"
    SUBSCRIPTION_STARTED = "subscription_started"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    USAGE_LIMIT_REACHED = "usage_limit_reached"


class PostHogAnalytics:
    """PostHog product analytics and feature flags."""

    def __init__(self, config: PostHogConfig):
        self.config = config
        self._client = None

        if not config.disabled:
            self._init_client()

    def _init_client(self):
        """Initialize PostHog client."""
        try:
            from posthog import Posthog

            self._client = Posthog(
                project_api_key=self.config.api_key,
                host=self.config.host,
            )
            logger.info("posthog_initialized", host=self.config.host)
        except ImportError:
            logger.warning("posthog_not_installed")
        except Exception as e:
            logger.error("posthog_init_failed", error=str(e))

    def identify(
        self,
        user_id: str,
        properties: Dict[str, Any],
        tenant_id: Optional[str] = None,
    ) -> None:
        """Identify a user with properties."""
        if not self._client:
            return

        self._client.identify(
            distinct_id=user_id,
            properties=properties,
        )

        # Associate with company group
        if tenant_id:
            self._client.group_identify(
                group_type="company",
                group_key=tenant_id,
                properties={"tenant_id": tenant_id},
            )

        logger.debug("posthog_identify", user_id=user_id)

    def track(
        self,
        user_id: str,
        event: str,
        properties: Optional[Dict[str, Any]] = None,
        tenant_id: Optional[str] = None,
    ) -> None:
        """Track a product event."""
        if not self._client:
            return

        props = properties or {}

        # Auto-add tenant context
        if tenant_id is None:
            tenant = get_current_tenant()
            if tenant:
                tenant_id = tenant.id
                props["tenant_tier"] = tenant.tier

        if tenant_id:
            props["$groups"] = {"company": tenant_id}

        self._client.capture(
            distinct_id=user_id,
            event=event,
            properties=props,
        )

        logger.debug("posthog_track", user_id=user_id, event=event)

    def track_feature_usage(
        self,
        user_id: str,
        feature: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Track feature usage for product analytics."""
        props = {"feature": feature}
        if metadata:
            props.update(metadata)

        self.track(
            user_id=user_id,
            event=Events.FEATURE_USED,
            properties=props,
        )

    def is_feature_enabled(
        self,
        feature: str,
        user_id: str,
        default: bool = False,
        groups: Optional[Dict[str, str]] = None,
    ) -> bool:
        """Check if a feature flag is enabled."""
        if not self._client:
            return default

        try:
            return self._client.feature_enabled(
                feature,
                user_id,
                groups=groups,
                default=default,
            )
        except Exception as e:
            logger.warning(
                "posthog_feature_check_failed",
                feature=feature,
                error=str(e),
            )
            return default

    def get_feature_flag(
        self,
        feature: str,
        user_id: str,
        default: Any = None,
    ) -> Any:
        """Get feature flag value (for multivariate flags)."""
        if not self._client:
            return default

        try:
            return self._client.get_feature_flag(feature, user_id) or default
        except Exception as e:
            logger.warning(
                "posthog_feature_get_failed",
                feature=feature,
                error=str(e),
            )
            return default

    def get_all_flags(
        self,
        user_id: str,
        groups: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Get all feature flags for a user."""
        if not self._client:
            return {}

        try:
            return self._client.get_all_flags(user_id, groups=groups)
        except Exception as e:
            logger.warning("posthog_all_flags_failed", error=str(e))
            return {}

    def alias(self, previous_id: str, new_id: str) -> None:
        """Create an alias between two user IDs."""
        if not self._client:
            return

        self._client.alias(previous_id, new_id)

    def flush(self) -> None:
        """Flush pending events."""
        if self._client:
            self._client.flush()

    def shutdown(self) -> None:
        """Shutdown the client."""
        if self._client:
            self._client.shutdown()
