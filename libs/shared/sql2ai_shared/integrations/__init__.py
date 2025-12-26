"""Third-party service integrations."""

from sql2ai_shared.integrations.posthog import PostHogAnalytics, PostHogConfig, Events
from sql2ai_shared.integrations.resend import EmailService, ResendConfig, EmailTemplate
from sql2ai_shared.integrations.stripe import (
    StripeBilling,
    StripeConfig,
    StripeWebhookHandler,
    SubscriptionStatus,
)
from sql2ai_shared.integrations.sentry import SentryIntegration, SentryConfig, traced
from sql2ai_shared.integrations.clerk import (
    ClerkAuth,
    ClerkConfig,
    ClerkUser,
    ClerkOrganization,
    ClerkWebhookHandler,
)
from sql2ai_shared.integrations.ai import (
    AIService,
    AIConfig,
    AIProvider,
    AIResponse,
    Message,
    SQLAIHelper,
)

__all__ = [
    # PostHog Analytics
    "PostHogAnalytics",
    "PostHogConfig",
    "Events",
    # Resend Email
    "EmailService",
    "ResendConfig",
    "EmailTemplate",
    # Stripe Billing
    "StripeBilling",
    "StripeConfig",
    "StripeWebhookHandler",
    "SubscriptionStatus",
    # Sentry Error Tracking
    "SentryIntegration",
    "SentryConfig",
    "traced",
    # Clerk Authentication
    "ClerkAuth",
    "ClerkConfig",
    "ClerkUser",
    "ClerkOrganization",
    "ClerkWebhookHandler",
    # AI/LLM
    "AIService",
    "AIConfig",
    "AIProvider",
    "AIResponse",
    "Message",
    "SQLAIHelper",
]
