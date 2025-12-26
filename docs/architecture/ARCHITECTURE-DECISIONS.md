# SQL2.AI Architecture Decision Records

This document consolidates all architectural decisions, technology choices, patterns, and integrations for the SQL2.AI platform.

---

## Table of Contents

1. [Core Technology Stack](#1-core-technology-stack)
2. [API & Backend](#2-api--backend)
3. [AI & LLM Layer](#3-ai--llm-layer)
4. [Database Strategy](#4-database-strategy)
5. [Authentication & Authorization](#5-authentication--authorization)
6. [Observability & Monitoring](#6-observability--monitoring)
7. [Payments & Billing](#7-payments--billing)
8. [Communications](#8-communications)
9. [Analytics & Product](#9-analytics--product)
10. [Enterprise Patterns](#10-enterprise-patterns)
11. [Infrastructure](#11-infrastructure)
12. [Security](#12-security)

---

## 1. Core Technology Stack

### Decision Summary

| Layer | Technology | Status | Rationale |
|-------|------------|--------|-----------|
| **Frontend (Site)** | Next.js 14 + App Router | ✅ Chosen | SSR, React ecosystem, Vercel optimization |
| **Frontend (App)** | Next.js 14 + App Router | ✅ Chosen | Shared codebase with site |
| **API Services** | Python + FastAPI | ✅ Chosen | Async, type hints, OpenAPI, AI ecosystem |
| **AI Layer** | LiteLLM + LangGraph | ✅ Chosen | Multi-provider, agentic workflows |
| **Database (Platform)** | PostgreSQL | ✅ Chosen | JSONB, RLS, proven reliability |
| **Cache** | Redis | ✅ Chosen | Caching, sessions, rate limiting, pub/sub |
| **Message Queue** | Redis Streams | ✅ Chosen | Simplicity, good enough for MVP |

### Alternatives Considered

| Technology | Considered For | Why Not Chosen |
|------------|----------------|----------------|
| Express.js | API | Python better for AI/ML ecosystem |
| Django | API | FastAPI more modern, async-first |
| Celery | Job Queue | Redis Streams simpler for our needs |
| RabbitMQ | Message Queue | Adds complexity, Redis sufficient |
| MongoDB | Platform DB | PostgreSQL RLS better for multi-tenancy |

---

## 2. API & Backend

### ADR-001: FastAPI for API Services

**Status:** ✅ Accepted

**Context:** Need a Python web framework for AI-powered API services.

**Decision:** Use FastAPI with async/await patterns.

**Consequences:**
- ✅ Native async support for AI workloads
- ✅ Automatic OpenAPI documentation
- ✅ Pydantic for validation
- ✅ Excellent TypeScript type generation
- ⚠️ Smaller ecosystem than Django/Flask
- ⚠️ Team must learn async patterns

### ADR-002: Service Architecture

**Status:** ✅ Accepted

**Decision:** Start with a modular monolith, extract services when needed.

```
apps/api/
├── src/
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   ├── ai/               # AI agents and chains
│   ├── middleware/       # Cross-cutting concerns
│   └── models/           # Domain models
```

**Rationale:** Simpler operations, easier debugging, can extract later.

---

## 3. AI & LLM Layer

### ADR-003: LiteLLM for LLM Provider Abstraction

**Status:** ✅ Accepted

**Context:** Need to support multiple LLM providers (OpenAI, Anthropic, Azure, local).

**Decision:** Use LiteLLM as unified interface.

**Benefits:**
- Single API for all providers
- Automatic fallbacks
- Cost tracking
- Caching support
- Provider-agnostic code

**Configuration:**
```python
AIConfig(
    default_model="gpt-4",
    fallback_models=["claude-3-sonnet", "gpt-3.5-turbo"],
    openai_api_key=SecretStr("..."),
    anthropic_api_key=SecretStr("..."),
)
```

### ADR-004: LangGraph for Agentic Workflows

**Status:** ✅ Accepted

**Context:** Need stateful, multi-step AI workflows for SQL agents.

**Decision:** Use LangGraph (not LangChain) for agent orchestration.

**Rationale:**
- Better state management than LangChain agents
- Explicit control flow
- Easier debugging
- Human-in-the-loop support

**Agents Implemented:**
- `SQLAgent` - Query generation and optimization
- `MigrationAgent` - Database migration planning
- (Planned) `ComplianceAgent` - Compliance scanning

### ADR-005: AI Observability

**Status:** 🔶 Planned

**Options:**
| Tool | Purpose | Priority |
|------|---------|----------|
| **LangSmith** | LangChain/LangGraph tracing | P1 |
| **Helicone** | Cost tracking, caching | P2 |
| **Weights & Biases** | Model evaluation | P3 |

**Decision:** Start with LangSmith for MVP, add Helicone for cost control.

---

## 4. Database Strategy

### ADR-006: PostgreSQL for Platform Data

**Status:** ✅ Accepted

**Rationale:**
- Row-Level Security (RLS) for multi-tenancy
- JSONB for flexible schema
- Proven at scale
- Rich ecosystem

**RLS Implementation:**
```sql
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON connections
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);
```

### ADR-007: Database Target Support

**Status:** ✅ Accepted

**Supported Databases:**
| Database | Priority | Status |
|----------|----------|--------|
| SQL Server | P0 | ✅ Implemented |
| PostgreSQL | P0 | ✅ Implemented |
| MySQL | P2 | 🔶 Planned |
| MariaDB | P3 | 🔶 Planned |

**Connection Abstraction:**
```python
class DatabaseType(Enum):
    SQLSERVER = "sqlserver"
    POSTGRESQL = "postgresql"

# Unified interface
conn = create_connection(DatabaseConfig(
    db_type=DatabaseType.SQLSERVER,
    host="localhost",
    ...
))
```

### ADR-008: Connection Pooling

**Status:** ✅ Accepted

**Decision:** Per-tenant connection pools with isolation.

```python
class TenantConnectionManager:
    """Each tenant gets isolated pool"""
    _pools: Dict[str, ConnectionPool]
```

---

## 5. Authentication & Authorization

### ADR-009: Authentication Provider

**Status:** 🔶 Deciding

**Options Evaluated:**

| Provider | Pros | Cons | Recommendation |
|----------|------|------|----------------|
| **Clerk** | Modern DX, React components, org support | Newer, less enterprise | ✅ Primary |
| **Auth0** | Mature, enterprise features | Complex, expensive | Alternative for enterprise |
| **WorkOS** | Enterprise SSO, SCIM | Limited free tier | Add-on for enterprise SSO |
| **Supabase Auth** | OSS, simple | Limited org features | Not recommended |

**Decision:** Clerk for MVP, add WorkOS for enterprise SSO.

### ADR-010: Authorization Model

**Status:** ✅ Accepted

**Model:** Role-Based Access Control (RBAC) with permissions.

```python
PREDEFINED_ROLES = {
    "admin": Role(permissions=[Permission(resource="*", action="*")]),
    "dba": Role(permissions=[
        Permission(resource="connections", action="*"),
        Permission(resource="queries", action="*"),
    ]),
    "developer": Role(permissions=[
        Permission(resource="queries", action="*"),
        Permission(resource="ai", action="*"),
    ]),
    "viewer": Role(permissions=[
        Permission(resource="*", action="read"),
    ]),
}
```

### ADR-011: JWT Token Strategy

**Status:** ✅ Accepted

**Implementation:**
- Access tokens: 30 min expiry
- Refresh tokens: 7 day expiry
- Token rotation on refresh
- ULID for `jti` claim (revocation support)

---

## 6. Observability & Monitoring

### ADR-012: Error Tracking

**Status:** ✅ Accepted - Sentry

**Rationale:**
- Industry standard
- Excellent Python/FastAPI support
- Performance monitoring included
- Release tracking

**Configuration:**
```python
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.environment,
    traces_sample_rate=0.1,
    profiles_sample_rate=0.1,
)
```

### ADR-013: APM & Metrics

**Status:** 🔶 Deciding

**Options:**

| Tool | Use Case | Decision |
|------|----------|----------|
| **Datadog** | Full observability (APM, logs, metrics) | ✅ Production |
| **OpenTelemetry** | Vendor-agnostic instrumentation | ✅ Implemented |
| **Grafana Cloud** | Self-hosted alternative | Alternative |
| **New Relic** | APM alternative | Not chosen |

**Decision:** OpenTelemetry for instrumentation → Datadog for visualization.

### ADR-014: Structured Logging

**Status:** ✅ Accepted - structlog

**Format:**
```python
logger.info(
    "query_executed",
    tenant_id=tenant.id,
    duration_ms=elapsed,
    query_hash=hash,
)
```

**Output:** JSON in production, colored console in development.

---

## 7. Payments & Billing

### ADR-015: Payment Provider

**Status:** ✅ Accepted - Stripe

**Features Used:**
- Subscriptions (monthly/yearly)
- Checkout sessions
- Customer portal
- Usage-based billing (AI tokens)
- Webhooks

**Pricing Tiers:**
| Tier | Billing | Features |
|------|---------|----------|
| Free | $0 | 1 DB, 100 queries/day |
| Pro | $49/mo | 10 DBs, 10K queries/day, AI |
| Enterprise | Custom | Unlimited, SSO, compliance |

### ADR-016: Usage-Based Billing

**Status:** 🔶 Planned

**Options:**
| Tool | Use Case | Decision |
|------|----------|----------|
| **Stripe Metering** | Simple usage billing | ✅ MVP |
| **Orb** | Complex usage-based pricing | 🔶 Future |
| **Lago** | OSS billing | Alternative |

---

## 8. Communications

### ADR-017: Transactional Email

**Status:** ✅ Accepted - Resend

**Rationale:**
- Developer-first API
- React Email templates
- Excellent deliverability
- Simple pricing

**Email Types:**
- Welcome emails
- Alert notifications
- Compliance reports
- Usage warnings
- Invoices

### ADR-018: In-App Messaging

**Status:** 🔶 Planned - Intercom

**Use Cases:**
- Customer support chat
- Product tours
- Knowledge base
- User engagement

---

## 9. Analytics & Product

### ADR-019: Product Analytics

**Status:** ✅ Accepted - PostHog

**Rationale:**
- Self-hostable (compliance)
- Feature flags included
- Session replay
- Funnels and retention
- SQL access to data

**Events Tracked:**
```python
class Events:
    SIGNUP_COMPLETED = "signup_completed"
    QUERY_EXECUTED = "query_executed"
    AI_QUERY_GENERATED = "ai_query_generated"
    COMPLIANCE_SCAN_RUN = "compliance_scan_run"
```

### ADR-020: Feature Flags

**Status:** ✅ Accepted - PostHog (built-in)

**Rationale:** Reduces vendor count, PostHog includes feature flags.

**Alternative for Enterprise:** LaunchDarkly (if needed).

---

## 10. Enterprise Patterns

### ADR-021: Multi-Tenancy

**Status:** ✅ Implemented

**Approach:** Shared database with Row-Level Security (RLS).

```python
# Context variable for tenant
_current_tenant: ContextVar[Optional[Tenant]]

# Middleware sets tenant context
async with TenantContext(tenant):
    # All queries automatically filtered by tenant_id
    results = await db.execute("SELECT * FROM connections")
```

### ADR-022: Resilience Patterns

**Status:** ✅ Implemented

| Pattern | Library | Use Case |
|---------|---------|----------|
| **Retry** | tenacity | Transient failures |
| **Circuit Breaker** | circuitbreaker | External service protection |
| **Bulkhead** | asyncio.Semaphore | Resource isolation |

```python
@with_retry(max_attempts=3, min_wait=1.0)
@circuit_protected(failure_threshold=5, recovery_timeout=30)
async def call_external_service():
    ...
```

### ADR-023: Audit Logging

**Status:** ✅ Implemented

**Features:**
- Hash-chained entries (tamper-proof)
- Compliance framework tagging
- Async buffered writes
- Query interface

```python
@audited(action=AuditAction.DATA_UPDATE, resource_type="connection")
async def update_connection(id: str, data: dict):
    ...
```

### ADR-024: Caching Strategy

**Status:** ✅ Implemented

**Layers:**
1. L1: In-memory (per-instance)
2. L2: Redis (shared)

**Patterns:**
- `@cached` decorator
- Tag-based invalidation
- Tenant-isolated namespaces

---

## 11. Infrastructure

### ADR-025: Hosting

**Status:** 🔶 Planned

| Component | Provider | Rationale |
|-----------|----------|-----------|
| **Marketing Site** | Vercel | Next.js optimized |
| **Web App** | Vercel | Same as site |
| **API** | Render | Easy Python deployment |
| **Database** | Neon | Serverless PostgreSQL |
| **Redis** | Upstash | Serverless Redis |

### ADR-026: Container Runtime

**Status:** ✅ Accepted

**Local Development:** OrbStack (macOS) / Docker Desktop
**Production:** Docker containers on Render/AWS ECS

### ADR-027: CI/CD

**Status:** 🔶 Planned

**Pipeline:**
```
Push → GitHub Actions →
  ├── Lint & Type Check
  ├── Unit Tests
  ├── Integration Tests
  ├── Build Docker Images
  └── Deploy to Environment
```

---

## 12. Security

### ADR-028: Secrets Management

**Status:** 🔶 Planned

| Environment | Solution |
|-------------|----------|
| **Local** | .env files (gitignored) |
| **CI/CD** | GitHub Secrets |
| **Production** | HashiCorp Vault / AWS Secrets Manager |

### ADR-029: Dependency Scanning

**Status:** 🔶 Planned

**Tools:**
- Snyk for vulnerability scanning
- Dependabot for updates
- GitHub Advanced Security for code scanning

### ADR-030: Data Encryption

**Status:** 🔶 Planned

| Data Type | At Rest | In Transit |
|-----------|---------|------------|
| Database credentials | Vault encryption | TLS |
| User data | PostgreSQL TDE | TLS |
| API keys | Vault | TLS |
| Backups | AES-256 | TLS |

---

## Decision Status Legend

| Status | Meaning |
|--------|---------|
| ✅ Accepted | Decision made and implemented |
| 🔶 Planned | Decision made, not yet implemented |
| 🔶 Deciding | Still evaluating options |
| ❌ Rejected | Considered but not chosen |

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| 2024-01-XX | Chris Therriault | Initial architecture decisions |

---

## References

- [ENTERPRISE-ARCHITECTURE.md](./ENTERPRISE-ARCHITECTURE.md) - Detailed patterns
- [TOOLSET-INTEGRATIONS.md](./TOOLSET-INTEGRATIONS.md) - Integration details
- [PLATFORM-ARCHITECTURE.md](./PLATFORM-ARCHITECTURE.md) - Shared library design
