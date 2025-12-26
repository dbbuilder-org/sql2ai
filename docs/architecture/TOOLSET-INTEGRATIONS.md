# SQL2.AI Toolset Integration Architecture

## Overview

This document outlines the enterprise toolset integrations for the SQL2.AI platform, organized by domain. Each integration is evaluated for our specific needs with database management, AI-powered workflows, and enterprise compliance requirements.

---

## Integration Categories

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           SQL2.AI INTEGRATION STACK                           │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │  OBSERVABILITY  │  │  AUTHENTICATION │  │    ANALYTICS    │              │
│  │                 │  │                 │  │                 │              │
│  │  • Datadog      │  │  • Clerk        │  │  • PostHog      │              │
│  │  • Sentry       │  │  • Auth0        │  │  • Mixpanel     │              │
│  │  • Grafana      │  │  • WorkOS       │  │  • Amplitude    │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   PAYMENTS      │  │ COMMUNICATIONS  │  │  FEATURE FLAGS  │              │
│  │                 │  │                 │  │                 │              │
│  │  • Stripe       │  │  • Resend       │  │  • LaunchDarkly │              │
│  │  • Orb (Usage)  │  │  • Twilio       │  │  • PostHog      │              │
│  │  • Lago         │  │  • Intercom     │  │  • Flagsmith    │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐              │
│  │   AI/LLM        │  │   SECURITY      │  │ INFRASTRUCTURE  │              │
│  │                 │  │                 │  │                 │              │
│  │  • LiteLLM      │  │  • Snyk         │  │  • Vercel       │              │
│  │  • LangSmith    │  │  • Vault        │  │  • Render       │              │
│  │  • Helicone     │  │  • 1Password    │  │  • Neon/Planet  │              │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘              │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Observability & Monitoring

### Primary: Datadog
**Why Datadog for SQL2.AI:**
- Unified APM, logs, metrics, and RUM in one platform
- Excellent database monitoring (DBM) for SQL Server and PostgreSQL
- AI-powered anomaly detection aligns with our AI-first approach
- Enterprise compliance features (SOC2, HIPAA)

```python
# libs/shared/sql2ai_shared/integrations/datadog.py
from ddtrace import tracer, patch_all
from datadog import initialize, statsd

class DatadogConfig:
    api_key: str
    app_key: str
    service_name: str = "sql2ai-api"
    env: str = "production"
    version: str = "1.0.0"

def init_datadog(config: DatadogConfig):
    """Initialize Datadog APM and StatsD"""
    initialize(
        api_key=config.api_key,
        app_key=config.app_key,
    )

    # Auto-instrument common libraries
    patch_all(
        fastapi=True,
        httpx=True,
        redis=True,
        asyncpg=True,
    )

    # Configure tracer
    tracer.configure(
        hostname="datadog-agent",
        port=8126,
        service=config.service_name,
        env=config.env,
        version=config.version,
    )

# Custom metrics
def record_query_metric(duration_ms: float, db_type: str, success: bool):
    statsd.histogram(
        'sql2ai.query.duration',
        duration_ms,
        tags=[f'db_type:{db_type}', f'success:{success}']
    )

def record_ai_metric(tokens: int, model: str, latency_ms: float):
    statsd.increment('sql2ai.ai.requests', tags=[f'model:{model}'])
    statsd.histogram('sql2ai.ai.tokens', tokens, tags=[f'model:{model}'])
    statsd.histogram('sql2ai.ai.latency', latency_ms, tags=[f'model:{model}'])
```

### Secondary: Sentry
**Why Sentry:**
- Best-in-class error tracking with stack traces
- Performance monitoring with transaction tracing
- Release tracking and deployment correlation
- AI-powered issue grouping

```python
# libs/shared/sql2ai_shared/integrations/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.asyncpg import AsyncPGIntegration

class SentryConfig:
    dsn: str
    environment: str = "production"
    release: str = "sql2ai@1.0.0"
    traces_sample_rate: float = 0.1
    profiles_sample_rate: float = 0.1

def init_sentry(config: SentryConfig):
    """Initialize Sentry error tracking and performance monitoring"""
    sentry_sdk.init(
        dsn=config.dsn,
        environment=config.environment,
        release=config.release,
        traces_sample_rate=config.traces_sample_rate,
        profiles_sample_rate=config.profiles_sample_rate,
        integrations=[
            FastApiIntegration(transaction_style="endpoint"),
            RedisIntegration(),
            AsyncPGIntegration(),
        ],
        # Filter sensitive data
        before_send=filter_sensitive_data,
        # Capture user context
        before_send_transaction=add_tenant_context,
    )

def filter_sensitive_data(event, hint):
    """Remove sensitive data before sending to Sentry"""
    if 'request' in event:
        headers = event['request'].get('headers', {})
        # Remove auth headers
        headers.pop('authorization', None)
        headers.pop('x-api-key', None)
    return event

def add_tenant_context(event, hint):
    """Add tenant context to transactions"""
    from sql2ai_shared.tenancy.context import get_current_tenant
    tenant = get_current_tenant()
    if tenant:
        event['tags'] = event.get('tags', {})
        event['tags']['tenant_id'] = tenant.id
        event['tags']['tenant_tier'] = tenant.tier
    return event
```

### Dashboard: Grafana
**Use Cases:**
- Custom dashboards for database performance
- Query analytics visualization
- AI token usage tracking
- SLA monitoring

---

## 2. Authentication & Authorization

### Primary: Clerk
**Why Clerk for SQL2.AI:**
- Modern DX with React/Next.js components
- Built-in MFA, social login, SSO
- Organization/team support (multi-tenancy)
- Webhook integration for user lifecycle

```python
# libs/shared/sql2ai_shared/integrations/clerk.py
from clerk_backend_api import Clerk
from clerk_backend_api.jwks import AuthenticateRequestOptions
from fastapi import Request, HTTPException

class ClerkConfig:
    secret_key: str
    publishable_key: str
    webhook_secret: str
    jwt_verification_key: str

class ClerkAuth:
    """Clerk authentication integration"""

    def __init__(self, config: ClerkConfig):
        self.client = Clerk(bearer_auth=config.secret_key)
        self.config = config

    async def verify_session(self, request: Request) -> dict:
        """Verify Clerk session from request"""
        session_token = request.headers.get("Authorization", "").replace("Bearer ", "")

        if not session_token:
            raise HTTPException(status_code=401, detail="No session token")

        try:
            # Verify JWT
            claims = await self.client.verify_token(
                session_token,
                AuthenticateRequestOptions(
                    authorized_parties=["https://sql2.ai", "https://app.sql2.ai"]
                )
            )
            return claims
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def get_user(self, user_id: str) -> dict:
        """Get user details from Clerk"""
        return await self.client.users.get(user_id)

    async def get_organization(self, org_id: str) -> dict:
        """Get organization (tenant) details"""
        return await self.client.organizations.get(org_id)

    def handle_webhook(self, payload: dict, signature: str) -> dict:
        """Handle Clerk webhooks for user/org events"""
        # Verify webhook signature
        # Process user.created, user.updated, organization.created, etc.
        event_type = payload.get("type")

        handlers = {
            "user.created": self._on_user_created,
            "user.deleted": self._on_user_deleted,
            "organization.created": self._on_org_created,
            "organizationMembership.created": self._on_member_added,
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(payload["data"])
        return {"status": "ignored"}
```

### Enterprise Alternative: WorkOS
**When to use WorkOS:**
- Enterprise SSO requirements (SAML, OIDC)
- Directory sync (SCIM)
- Audit logs for compliance
- Fine-grained authorization

```python
# libs/shared/sql2ai_shared/integrations/workos.py
import workos
from workos import client

class WorkOSConfig:
    api_key: str
    client_id: str

class WorkOSAuth:
    """WorkOS for enterprise SSO and directory sync"""

    def __init__(self, config: WorkOSConfig):
        workos.api_key = config.api_key
        workos.client_id = config.client_id

    async def get_authorization_url(
        self,
        organization_id: str,
        redirect_uri: str,
    ) -> str:
        """Get SSO authorization URL"""
        return client.sso.get_authorization_url(
            organization=organization_id,
            redirect_uri=redirect_uri,
        )

    async def get_profile(self, code: str) -> dict:
        """Exchange code for user profile"""
        profile = client.sso.get_profile_and_token(code)
        return profile.to_dict()

    async def sync_directory(self, directory_id: str) -> list:
        """Sync users from enterprise directory"""
        users = client.directory_sync.list_users(directory=directory_id)
        return users.to_dict()
```

---

## 3. Product Analytics

### Primary: PostHog
**Why PostHog for SQL2.AI:**
- Self-hostable for compliance (SOC2, HIPAA data residency)
- Built-in feature flags (reduces vendor count)
- Session replay for UX debugging
- Funnels and retention for product metrics
- SQL access to analytics data

```python
# libs/shared/sql2ai_shared/integrations/posthog.py
from posthog import Posthog

class PostHogConfig:
    api_key: str
    host: str = "https://app.posthog.com"
    personal_api_key: str = None  # For feature flags

class PostHogAnalytics:
    """PostHog product analytics and feature flags"""

    def __init__(self, config: PostHogConfig):
        self.client = Posthog(
            project_api_key=config.api_key,
            host=config.host,
        )
        self.config = config

    def track(
        self,
        user_id: str,
        event: str,
        properties: dict = None,
        tenant_id: str = None,
    ):
        """Track a product event"""
        props = properties or {}
        if tenant_id:
            props["$groups"] = {"company": tenant_id}

        self.client.capture(
            distinct_id=user_id,
            event=event,
            properties=props,
        )

    def identify(
        self,
        user_id: str,
        properties: dict,
        tenant_id: str = None,
    ):
        """Identify a user with properties"""
        self.client.identify(
            distinct_id=user_id,
            properties=properties,
        )

        if tenant_id:
            self.client.group_identify(
                group_type="company",
                group_key=tenant_id,
                properties={"tenant_id": tenant_id},
            )

    def is_feature_enabled(
        self,
        feature: str,
        user_id: str,
        default: bool = False,
    ) -> bool:
        """Check if feature flag is enabled"""
        return self.client.feature_enabled(
            feature,
            user_id,
            default=default,
        )

    def get_feature_flag_payload(
        self,
        feature: str,
        user_id: str,
    ) -> dict:
        """Get feature flag payload (for A/B tests)"""
        return self.client.get_feature_flag_payload(feature, user_id)

# Event constants for SQL2.AI
class Events:
    # Onboarding
    SIGNUP_COMPLETED = "signup_completed"
    ONBOARDING_STARTED = "onboarding_started"
    FIRST_CONNECTION_ADDED = "first_connection_added"
    FIRST_QUERY_EXECUTED = "first_query_executed"

    # Core usage
    QUERY_EXECUTED = "query_executed"
    AI_QUERY_GENERATED = "ai_query_generated"
    MIGRATION_CREATED = "migration_created"
    MIGRATION_APPLIED = "migration_applied"

    # Features
    COMPLIANCE_SCAN_RUN = "compliance_scan_run"
    ALERT_CREATED = "alert_created"
    REPORT_EXPORTED = "report_exported"

    # Monetization
    UPGRADE_INITIATED = "upgrade_initiated"
    SUBSCRIPTION_STARTED = "subscription_started"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
```

---

## 4. Payments & Billing

### Primary: Stripe
**Why Stripe:**
- Industry standard for SaaS billing
- Subscription management built-in
- Usage-based billing support (for AI tokens)
- Customer portal for self-service

```python
# libs/shared/sql2ai_shared/integrations/stripe.py
import stripe
from typing import Optional

class StripeConfig:
    secret_key: str
    publishable_key: str
    webhook_secret: str

    # Product/Price IDs
    pro_monthly_price: str
    pro_yearly_price: str
    enterprise_price: str
    ai_token_price: str  # Usage-based

class StripeBilling:
    """Stripe billing integration"""

    def __init__(self, config: StripeConfig):
        stripe.api_key = config.secret_key
        self.config = config

    async def create_customer(
        self,
        email: str,
        name: str,
        tenant_id: str,
    ) -> str:
        """Create Stripe customer for tenant"""
        customer = stripe.Customer.create(
            email=email,
            name=name,
            metadata={"tenant_id": tenant_id},
        )
        return customer.id

    async def create_subscription(
        self,
        customer_id: str,
        price_id: str,
        trial_days: int = 14,
    ) -> dict:
        """Create subscription"""
        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{"price": price_id}],
            trial_period_days=trial_days,
            payment_behavior="default_incomplete",
            expand=["latest_invoice.payment_intent"],
        )
        return {
            "subscription_id": subscription.id,
            "client_secret": subscription.latest_invoice.payment_intent.client_secret,
            "status": subscription.status,
        }

    async def create_checkout_session(
        self,
        customer_id: str,
        price_id: str,
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create Checkout session for upgrade"""
        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return session.url

    async def report_usage(
        self,
        subscription_item_id: str,
        quantity: int,
        timestamp: int = None,
    ):
        """Report usage for usage-based billing (AI tokens)"""
        stripe.SubscriptionItem.create_usage_record(
            subscription_item_id,
            quantity=quantity,
            timestamp=timestamp or int(time.time()),
            action="increment",
        )

    async def create_billing_portal(
        self,
        customer_id: str,
        return_url: str,
    ) -> str:
        """Create customer billing portal session"""
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url

# Webhook handler
class StripeWebhooks:
    """Handle Stripe webhook events"""

    def __init__(self, config: StripeConfig):
        self.config = config

    def verify_and_handle(self, payload: bytes, signature: str) -> dict:
        """Verify webhook and dispatch to handler"""
        event = stripe.Webhook.construct_event(
            payload, signature, self.config.webhook_secret
        )

        handlers = {
            "customer.subscription.created": self._on_subscription_created,
            "customer.subscription.updated": self._on_subscription_updated,
            "customer.subscription.deleted": self._on_subscription_deleted,
            "invoice.paid": self._on_invoice_paid,
            "invoice.payment_failed": self._on_payment_failed,
        }

        handler = handlers.get(event.type)
        if handler:
            return handler(event.data.object)
        return {"status": "ignored"}
```

### Usage-Based Billing: Orb
**When to use Orb:**
- Complex usage-based pricing
- Real-time usage tracking
- Multiple pricing dimensions (queries, AI tokens, storage)

```python
# libs/shared/sql2ai_shared/integrations/orb.py
class OrbConfig:
    api_key: str
    base_url: str = "https://api.withorb.com/v1"

class OrbBilling:
    """Orb for usage-based billing"""

    async def ingest_event(
        self,
        event_name: str,
        customer_id: str,
        properties: dict,
        timestamp: str = None,
    ):
        """Ingest usage event"""
        # e.g., "ai_tokens_used", "queries_executed", "storage_gb"
        pass

    async def get_current_usage(self, customer_id: str) -> dict:
        """Get current period usage"""
        pass
```

---

## 5. Communications

### Transactional Email: Resend
**Why Resend:**
- Developer-first API
- React email templates
- Excellent deliverability
- Built-in analytics

```python
# libs/shared/sql2ai_shared/integrations/resend.py
import resend
from typing import List, Optional

class ResendConfig:
    api_key: str
    from_email: str = "SQL2.AI <notifications@sql2.ai>"
    reply_to: str = "support@sql2.ai"

class EmailService:
    """Resend email integration"""

    def __init__(self, config: ResendConfig):
        resend.api_key = config.api_key
        self.config = config

    async def send_welcome(self, to: str, name: str):
        """Send welcome email"""
        return resend.Emails.send({
            "from": self.config.from_email,
            "to": to,
            "subject": "Welcome to SQL2.AI",
            "html": self._render_template("welcome", {"name": name}),
        })

    async def send_alert(
        self,
        to: str,
        alert_name: str,
        severity: str,
        details: dict,
    ):
        """Send database alert notification"""
        return resend.Emails.send({
            "from": self.config.from_email,
            "to": to,
            "subject": f"[{severity.upper()}] {alert_name}",
            "html": self._render_template("alert", {
                "alert_name": alert_name,
                "severity": severity,
                "details": details,
            }),
        })

    async def send_compliance_report(
        self,
        to: List[str],
        report_type: str,
        report_url: str,
    ):
        """Send compliance report notification"""
        return resend.Emails.send({
            "from": self.config.from_email,
            "to": to,
            "subject": f"SQL2.AI Compliance Report: {report_type}",
            "html": self._render_template("compliance_report", {
                "report_type": report_type,
                "report_url": report_url,
            }),
        })

# Email templates
EMAIL_TEMPLATES = {
    "welcome": "templates/emails/welcome.html",
    "alert": "templates/emails/alert.html",
    "compliance_report": "templates/emails/compliance_report.html",
    "migration_complete": "templates/emails/migration_complete.html",
    "usage_warning": "templates/emails/usage_warning.html",
}
```

### In-App & Support: Intercom
**Why Intercom:**
- In-app messaging and support
- Knowledge base
- User onboarding tours
- Product engagement tracking

```python
# libs/shared/sql2ai_shared/integrations/intercom.py
class IntercomConfig:
    app_id: str
    access_token: str
    identity_verification_secret: str

class IntercomIntegration:
    """Intercom for support and engagement"""

    def generate_user_hash(self, user_id: str) -> str:
        """Generate identity verification hash for frontend"""
        import hmac
        import hashlib
        return hmac.new(
            self.config.identity_verification_secret.encode(),
            user_id.encode(),
            hashlib.sha256
        ).hexdigest()

    async def create_or_update_user(
        self,
        user_id: str,
        email: str,
        name: str,
        custom_attributes: dict,
    ):
        """Sync user to Intercom"""
        pass

    async def track_event(
        self,
        user_id: str,
        event_name: str,
        metadata: dict = None,
    ):
        """Track event in Intercom"""
        pass
```

---

## 6. AI/LLM Observability

### LLM Gateway: LiteLLM (Primary)
Already implemented in shared library. Provides:
- Unified interface for OpenAI, Claude, Azure, local models
- Automatic fallbacks and load balancing
- Cost tracking

### LLM Observability: LangSmith
**Why LangSmith:**
- LangChain native observability
- Trace debugging for LangGraph agents
- Prompt versioning and testing
- Dataset management for evals

```python
# libs/shared/sql2ai_shared/integrations/langsmith.py
from langsmith import Client
from langsmith.run_trees import RunTree

class LangSmithConfig:
    api_key: str
    project: str = "sql2ai-production"

class LangSmithTracing:
    """LangSmith for LLM observability"""

    def __init__(self, config: LangSmithConfig):
        self.client = Client(api_key=config.api_key)
        self.project = config.project

    def create_run(
        self,
        name: str,
        run_type: str,  # "llm", "chain", "tool", "agent"
        inputs: dict,
        parent_run_id: str = None,
    ) -> RunTree:
        """Create a new run for tracing"""
        return RunTree(
            name=name,
            run_type=run_type,
            inputs=inputs,
            project_name=self.project,
            parent_run_id=parent_run_id,
        )

    async def log_feedback(
        self,
        run_id: str,
        score: float,
        comment: str = None,
    ):
        """Log user feedback on LLM output"""
        self.client.create_feedback(
            run_id=run_id,
            key="user_rating",
            score=score,
            comment=comment,
        )
```

### Cost Tracking: Helicone
**Why Helicone:**
- Detailed cost attribution per tenant
- Request caching to reduce costs
- Rate limiting at LLM layer
- Prompt management

```python
# libs/shared/sql2ai_shared/integrations/helicone.py
class HeliconeConfig:
    api_key: str
    base_url: str = "https://oai.helicone.ai/v1"

class HeliconeProxy:
    """Helicone for LLM cost tracking and caching"""

    def get_headers(self, tenant_id: str, user_id: str) -> dict:
        """Get headers for Helicone proxy"""
        return {
            "Helicone-Auth": f"Bearer {self.config.api_key}",
            "Helicone-User-Id": user_id,
            "Helicone-Property-TenantId": tenant_id,
            "Helicone-Cache-Enabled": "true",
            "Helicone-Retry-Enabled": "true",
        }
```

---

## 7. Security & Secrets

### Secrets Management: HashiCorp Vault
**Why Vault:**
- Dynamic database credentials
- Encryption as a service
- PKI infrastructure
- Audit logging

```python
# libs/shared/sql2ai_shared/integrations/vault.py
import hvac

class VaultConfig:
    url: str
    token: str = None
    role_id: str = None
    secret_id: str = None

class VaultSecrets:
    """HashiCorp Vault for secrets management"""

    def __init__(self, config: VaultConfig):
        self.client = hvac.Client(url=config.url)
        if config.token:
            self.client.token = config.token
        elif config.role_id and config.secret_id:
            self.client.auth.approle.login(
                role_id=config.role_id,
                secret_id=config.secret_id,
            )

    async def get_secret(self, path: str) -> dict:
        """Get secret from Vault KV store"""
        response = self.client.secrets.kv.v2.read_secret_version(path=path)
        return response["data"]["data"]

    async def get_database_creds(self, role: str) -> dict:
        """Get dynamic database credentials"""
        response = self.client.secrets.database.generate_credentials(name=role)
        return {
            "username": response["data"]["username"],
            "password": response["data"]["password"],
            "lease_duration": response["lease_duration"],
        }

    async def encrypt(self, plaintext: str, key_name: str) -> str:
        """Encrypt using Vault transit engine"""
        response = self.client.secrets.transit.encrypt_data(
            name=key_name,
            plaintext=plaintext,
        )
        return response["data"]["ciphertext"]

    async def decrypt(self, ciphertext: str, key_name: str) -> str:
        """Decrypt using Vault transit engine"""
        response = self.client.secrets.transit.decrypt_data(
            name=key_name,
            ciphertext=ciphertext,
        )
        return response["data"]["plaintext"]
```

### Dependency Scanning: Snyk
**Why Snyk:**
- Vulnerability scanning for Python/Node.js
- Container image scanning
- IaC security scanning
- License compliance

---

## 8. Infrastructure

### Frontend Hosting: Vercel
- Optimal for Next.js (marketing site + web app)
- Edge functions for low latency
- Preview deployments for PRs
- Analytics built-in

### API Hosting: Render
- Easy FastAPI deployment
- Background workers
- Managed PostgreSQL
- Private networking

### Database: Neon
**Why Neon:**
- Serverless PostgreSQL
- Branching for dev/preview
- Autoscaling
- Point-in-time recovery

---

## Integration Priority Matrix

| Integration | Priority | Phase | Rationale |
|------------|----------|-------|-----------|
| **Clerk** | P0 | MVP | Authentication is foundational |
| **Stripe** | P0 | MVP | Revenue from day 1 |
| **Resend** | P0 | MVP | Transactional email required |
| **PostHog** | P0 | MVP | Product analytics + feature flags |
| **Sentry** | P0 | MVP | Error tracking essential |
| **LiteLLM** | P0 | MVP | AI layer (done) |
| **Datadog** | P1 | Post-MVP | Full observability |
| **LangSmith** | P1 | Post-MVP | LLM debugging |
| **Intercom** | P1 | Post-MVP | Customer support |
| **Vault** | P2 | Scale | Enhanced security |
| **WorkOS** | P2 | Enterprise | Enterprise SSO |
| **Orb** | P2 | Scale | Complex usage billing |

---

## Configuration Structure

```python
# apps/api/src/config.py
from pydantic_settings import BaseSettings

class IntegrationSettings(BaseSettings):
    """All integration configuration"""

    # Authentication
    clerk_secret_key: str
    clerk_publishable_key: str
    clerk_webhook_secret: str

    # Payments
    stripe_secret_key: str
    stripe_publishable_key: str
    stripe_webhook_secret: str

    # Analytics
    posthog_api_key: str
    posthog_host: str = "https://app.posthog.com"

    # Error Tracking
    sentry_dsn: str
    sentry_environment: str = "production"

    # Observability
    datadog_api_key: str = None
    datadog_app_key: str = None

    # Email
    resend_api_key: str

    # AI
    openai_api_key: str
    anthropic_api_key: str = None
    langsmith_api_key: str = None

    # Secrets
    vault_url: str = None
    vault_token: str = None

    class Config:
        env_prefix = "SQL2AI_"
        env_file = ".env"
```

---

## Next Steps

1. **Phase 1 (MVP):** Implement Clerk, Stripe, Resend, PostHog, Sentry
2. **Phase 2 (Launch):** Add Datadog, LangSmith, Intercom
3. **Phase 3 (Scale):** Add Vault, WorkOS, advanced billing
