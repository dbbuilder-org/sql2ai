# SQL2.AI Enterprise Architecture

## Overview

This document defines the enterprise-grade architecture patterns for the SQL2.AI platform, ensuring scalability, reliability, security, and maintainability.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CLIENTS                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web App   │  │  CLI Tool   │  │ SSMS Plugin │  │  MCP Client │        │
│  │  (Next.js)  │  │ (TypeScript)│  │   (.NET)    │  │ (TypeScript)│        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼────────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   API Gateway     │
                          │   (Kong/Traefik)  │
                          │   Rate Limiting   │
                          │   Auth Validation │
                          └─────────┬─────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────┐
│                           SERVICE MESH                                     │
│                                   │                                        │
│  ┌────────────────────────────────┼────────────────────────────────────┐  │
│  │                         CORE SERVICES                                │  │
│  │                                │                                     │  │
│  │  ┌─────────────┐  ┌───────────▼───────────┐  ┌─────────────┐       │  │
│  │  │   Auth      │  │      AI Service       │  │  Database   │       │  │
│  │  │  Service    │  │      (FastAPI)        │  │  Service    │       │  │
│  │  │  (FastAPI)  │  │                       │  │  (FastAPI)  │       │  │
│  │  │             │  │  • LiteLLM            │  │             │       │  │
│  │  │  • JWT      │  │  • LangGraph          │  │  • Query    │       │  │
│  │  │  • OAuth    │  │  • LangChain          │  │  • Monitor  │       │  │
│  │  │  • RBAC     │  │  • Agents             │  │  • Migrate  │       │  │
│  │  │  • MFA      │  │                       │  │             │       │  │
│  │  └──────┬──────┘  └───────────┬───────────┘  └──────┬──────┘       │  │
│  │         │                     │                     │              │  │
│  └─────────┼─────────────────────┼─────────────────────┼──────────────┘  │
│            │                     │                     │                  │
│  ┌─────────┼─────────────────────┼─────────────────────┼──────────────┐  │
│  │         │           SHARED INFRASTRUCTURE           │              │  │
│  │         │                     │                     │              │  │
│  │  ┌──────▼──────┐  ┌───────────▼───────────┐  ┌─────▼───────┐      │  │
│  │  │   Redis     │  │    Message Queue      │  │  Postgres   │      │  │
│  │  │             │  │    (RabbitMQ/SQS)     │  │  (Platform) │      │  │
│  │  │  • Cache    │  │                       │  │             │      │  │
│  │  │  • Sessions │  │  • Events             │  │  • Users    │      │  │
│  │  │  • Pub/Sub  │  │  • Jobs               │  │  • Tenants  │      │  │
│  │  │  • Rate Lim │  │  • Notifications      │  │  • Audit    │      │  │
│  │  └─────────────┘  └───────────────────────┘  └─────────────┘      │  │
│  │                                                                    │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
                                    │
┌───────────────────────────────────┼───────────────────────────────────────┐
│                      OBSERVABILITY LAYER                                   │
│                                   │                                        │
│  ┌─────────────┐  ┌───────────────┴───────────────┐  ┌─────────────┐      │
│  │  Prometheus │  │      OpenTelemetry            │  │   Grafana   │      │
│  │  (Metrics)  │  │  (Traces, Logs, Metrics)      │  │ (Dashboard) │      │
│  └─────────────┘  └───────────────────────────────┘  └─────────────┘      │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Enterprise Patterns

### 1. Resilience Patterns

#### Circuit Breaker
```python
# libs/shared/resilience.py
from circuitbreaker import circuit
from tenacity import retry, stop_after_attempt, wait_exponential

class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 30
    expected_exceptions: tuple = (ConnectionError, TimeoutError)

@circuit(
    failure_threshold=5,
    recovery_timeout=30,
    expected_exception=ConnectionError
)
async def call_external_service(url: str) -> dict:
    """Protected external call with circuit breaker"""
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10.0)
        return response.json()
```

#### Retry with Exponential Backoff
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((ConnectionError, TimeoutError))
)
async def resilient_operation():
    """Operation with automatic retry"""
    pass
```

#### Bulkhead Pattern
```python
import asyncio
from asyncio import Semaphore

class BulkheadManager:
    """Isolate failures by limiting concurrent operations"""

    def __init__(self):
        self.bulkheads = {
            'ai_requests': Semaphore(10),      # Max 10 concurrent AI calls
            'db_connections': Semaphore(50),   # Max 50 DB connections
            'file_processing': Semaphore(5),   # Max 5 file operations
        }

    async def execute(self, bulkhead: str, operation):
        async with self.bulkheads[bulkhead]:
            return await operation()
```

---

### 2. Multi-Tenancy Architecture

```python
# libs/shared/tenancy.py
from contextvars import ContextVar
from typing import Optional
from pydantic import BaseModel

# Tenant context for request-scoped isolation
current_tenant: ContextVar[Optional['Tenant']] = ContextVar('current_tenant', default=None)

class Tenant(BaseModel):
    id: str
    name: str
    slug: str
    tier: str  # 'free', 'pro', 'enterprise'
    settings: dict
    limits: 'TenantLimits'

class TenantLimits(BaseModel):
    max_databases: int
    max_queries_per_day: int
    max_ai_tokens_per_month: int
    max_users: int
    retention_days: int
    features: list[str]

# Tier definitions
TIER_LIMITS = {
    'free': TenantLimits(
        max_databases=1,
        max_queries_per_day=100,
        max_ai_tokens_per_month=50_000,
        max_users=1,
        retention_days=7,
        features=['query', 'basic_monitor']
    ),
    'pro': TenantLimits(
        max_databases=10,
        max_queries_per_day=10_000,
        max_ai_tokens_per_month=1_000_000,
        max_users=10,
        retention_days=90,
        features=['query', 'monitor', 'optimize', 'migrate', 'ai_assist']
    ),
    'enterprise': TenantLimits(
        max_databases=-1,  # Unlimited
        max_queries_per_day=-1,
        max_ai_tokens_per_month=-1,
        max_users=-1,
        retention_days=365,
        features=['*']  # All features
    )
}
```

#### Row-Level Security
```sql
-- PostgreSQL RLS for multi-tenancy
ALTER TABLE connections ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON connections
    USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Function to set tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(p_tenant_id uuid)
RETURNS void AS $$
BEGIN
    PERFORM set_config('app.current_tenant_id', p_tenant_id::text, true);
END;
$$ LANGUAGE plpgsql;
```

---

### 3. Event-Driven Architecture

```python
# libs/shared/events.py
from datetime import datetime
from typing import Any, Callable, Dict, List
from pydantic import BaseModel
import json

class DomainEvent(BaseModel):
    """Base class for all domain events"""
    event_id: str
    event_type: str
    tenant_id: str
    user_id: str | None
    timestamp: datetime
    version: int = 1
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = {}

# Event Types
class QueryExecutedEvent(DomainEvent):
    event_type: str = "query.executed"

class MigrationAppliedEvent(DomainEvent):
    event_type: str = "migration.applied"

class AlertTriggeredEvent(DomainEvent):
    event_type: str = "alert.triggered"

class ComplianceViolationEvent(DomainEvent):
    event_type: str = "compliance.violation"

# Event Bus
class EventBus:
    """In-process event bus with async support"""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def publish(self, event: DomainEvent):
        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            await handler(event)

    async def publish_to_queue(self, event: DomainEvent, queue: str = "events"):
        """Publish to external message queue for cross-service communication"""
        # Redis Streams or RabbitMQ
        pass

# Event Store for Event Sourcing
class EventStore:
    """Append-only event store"""

    async def append(self, stream_id: str, events: List[DomainEvent]):
        """Append events to a stream"""
        pass

    async def read_stream(self, stream_id: str, from_version: int = 0) -> List[DomainEvent]:
        """Read all events from a stream"""
        pass

    async def subscribe_to_stream(self, stream_id: str, handler: Callable):
        """Subscribe to real-time events on a stream"""
        pass
```

---

### 4. CQRS Pattern (Command Query Responsibility Segregation)

```python
# libs/shared/cqrs.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

TCommand = TypeVar('TCommand')
TQuery = TypeVar('TQuery')
TResult = TypeVar('TResult')

# Commands (Write operations)
class Command(ABC):
    """Base command"""
    pass

class CommandHandler(ABC, Generic[TCommand]):
    @abstractmethod
    async def handle(self, command: TCommand) -> None:
        pass

# Queries (Read operations)
class Query(ABC, Generic[TResult]):
    """Base query"""
    pass

class QueryHandler(ABC, Generic[TQuery, TResult]):
    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        pass

# Example Commands
class ExecuteQueryCommand(Command):
    connection_id: str
    sql: str
    parameters: dict | None = None

class ApplyMigrationCommand(Command):
    connection_id: str
    migration_id: str
    dry_run: bool = False

# Example Queries
class GetQueryHistoryQuery(Query[list]):
    connection_id: str
    limit: int = 100
    offset: int = 0

class GetDatabaseHealthQuery(Query[dict]):
    connection_id: str

# Dispatcher
class Dispatcher:
    def __init__(self):
        self._command_handlers: dict = {}
        self._query_handlers: dict = {}

    def register_command_handler(self, command_type: type, handler: CommandHandler):
        self._command_handlers[command_type] = handler

    def register_query_handler(self, query_type: type, handler: QueryHandler):
        self._query_handlers[query_type] = handler

    async def send(self, command: Command) -> None:
        handler = self._command_handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler for {type(command)}")
        await handler.handle(command)

    async def query(self, query: Query[TResult]) -> TResult:
        handler = self._query_handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler for {type(query)}")
        return await handler.handle(query)
```

---

### 5. Distributed Caching Strategy

```python
# libs/shared/caching.py
from abc import ABC, abstractmethod
from typing import Any, Optional
import hashlib
import json

class CacheKey:
    """Structured cache key generation"""

    @staticmethod
    def build(namespace: str, *parts: str) -> str:
        return f"sql2ai:{namespace}:{':'.join(parts)}"

    @staticmethod
    def for_query_result(tenant_id: str, query_hash: str) -> str:
        return CacheKey.build("query", tenant_id, query_hash)

    @staticmethod
    def for_schema(tenant_id: str, connection_id: str) -> str:
        return CacheKey.build("schema", tenant_id, connection_id)

    @staticmethod
    def for_ai_response(prompt_hash: str, model: str) -> str:
        return CacheKey.build("ai", model, prompt_hash)

class CachePolicy:
    """Cache TTL and invalidation policies"""

    # TTL in seconds
    QUERY_RESULT = 300          # 5 minutes
    SCHEMA_METADATA = 3600      # 1 hour
    AI_RESPONSE = 86400         # 24 hours
    USER_SESSION = 1800         # 30 minutes
    RATE_LIMIT = 60             # 1 minute window

    # Invalidation patterns
    INVALIDATE_ON_DDL = ["schema", "metadata"]
    INVALIDATE_ON_DML = ["query"]

class CacheManager:
    """Multi-level cache manager"""

    def __init__(self, redis_client, local_cache_size: int = 1000):
        self.redis = redis_client
        self.local = LRUCache(local_cache_size)  # L1 cache

    async def get(self, key: str) -> Optional[Any]:
        # L1: Local cache
        if value := self.local.get(key):
            return value

        # L2: Redis
        if value := await self.redis.get(key):
            self.local.set(key, value)
            return json.loads(value)

        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        serialized = json.dumps(value)
        await self.redis.setex(key, ttl, serialized)
        self.local.set(key, value)

    async def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = await self.redis.keys(f"sql2ai:{pattern}:*")
        if keys:
            await self.redis.delete(*keys)
        self.local.clear()
```

---

### 6. Rate Limiting

```python
# libs/shared/rate_limiting.py
from datetime import datetime
from typing import Optional
import redis.asyncio as redis

class RateLimitConfig:
    """Rate limit configurations by tier"""

    LIMITS = {
        'free': {
            'api_requests': (100, 3600),      # 100 per hour
            'ai_requests': (10, 3600),        # 10 per hour
            'query_executions': (50, 3600),   # 50 per hour
        },
        'pro': {
            'api_requests': (10000, 3600),
            'ai_requests': (1000, 3600),
            'query_executions': (5000, 3600),
        },
        'enterprise': {
            'api_requests': (-1, 0),          # Unlimited
            'ai_requests': (-1, 0),
            'query_executions': (-1, 0),
        }
    }

class SlidingWindowRateLimiter:
    """Sliding window rate limiter using Redis"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def is_allowed(
        self,
        key: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, dict]:
        """
        Check if request is allowed and return remaining quota

        Returns: (is_allowed, {remaining, reset_at, limit})
        """
        if limit == -1:  # Unlimited
            return True, {'remaining': -1, 'reset_at': None, 'limit': -1}

        now = datetime.utcnow().timestamp()
        window_start = now - window_seconds

        pipe = self.redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Count requests in window
        pipe.zcard(key)
        # Set expiry
        pipe.expire(key, window_seconds)

        results = await pipe.execute()
        request_count = results[2]

        remaining = max(0, limit - request_count)
        reset_at = datetime.fromtimestamp(now + window_seconds)

        return request_count <= limit, {
            'remaining': remaining,
            'reset_at': reset_at.isoformat(),
            'limit': limit
        }

class RateLimitMiddleware:
    """FastAPI middleware for rate limiting"""

    async def __call__(self, request, call_next):
        tenant = get_current_tenant()
        tier = tenant.tier if tenant else 'free'

        limits = RateLimitConfig.LIMITS[tier]
        key = f"ratelimit:{tenant.id}:api_requests"

        allowed, info = await self.limiter.is_allowed(
            key,
            limits['api_requests'][0],
            limits['api_requests'][1]
        )

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={'error': 'Rate limit exceeded', **info},
                headers={
                    'X-RateLimit-Limit': str(info['limit']),
                    'X-RateLimit-Remaining': str(info['remaining']),
                    'X-RateLimit-Reset': info['reset_at']
                }
            )

        response = await call_next(request)
        response.headers['X-RateLimit-Remaining'] = str(info['remaining'])
        return response
```

---

### 7. Audit Logging

```python
# libs/shared/audit.py
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
import hashlib

class AuditAction(str, Enum):
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_REFRESH = "auth.token_refresh"

    # Database operations
    QUERY_EXECUTED = "db.query_executed"
    CONNECTION_CREATED = "db.connection_created"
    CONNECTION_DELETED = "db.connection_deleted"

    # Migration operations
    MIGRATION_APPLIED = "migration.applied"
    MIGRATION_ROLLED_BACK = "migration.rolled_back"

    # AI operations
    AI_QUERY = "ai.query"
    AI_ANALYSIS = "ai.analysis"

    # Admin operations
    USER_CREATED = "admin.user_created"
    USER_DELETED = "admin.user_deleted"
    PERMISSION_CHANGED = "admin.permission_changed"
    SETTINGS_CHANGED = "admin.settings_changed"

class AuditEntry(BaseModel):
    id: str
    timestamp: datetime
    tenant_id: str
    user_id: Optional[str]
    action: AuditAction
    resource_type: str
    resource_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: str

    # What changed
    old_value: Optional[dict] = None
    new_value: Optional[dict] = None

    # Result
    success: bool
    error_message: Optional[str] = None

    # Tamper-proof hash chain
    previous_hash: Optional[str] = None
    entry_hash: str

    def compute_hash(self) -> str:
        """Compute SHA-256 hash for tamper detection"""
        data = f"{self.timestamp}{self.tenant_id}{self.action}{self.resource_id}{self.previous_hash}"
        return hashlib.sha256(data.encode()).hexdigest()

class AuditLogger:
    """Tamper-proof audit logging"""

    def __init__(self, repository: 'AuditRepository'):
        self.repository = repository
        self._last_hash: Optional[str] = None

    async def log(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        old_value: Optional[dict] = None,
        new_value: Optional[dict] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ):
        context = get_request_context()

        entry = AuditEntry(
            id=generate_ulid(),
            timestamp=datetime.utcnow(),
            tenant_id=context.tenant_id,
            user_id=context.user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=context.ip_address,
            user_agent=context.user_agent,
            request_id=context.request_id,
            old_value=old_value,
            new_value=new_value,
            success=success,
            error_message=error_message,
            previous_hash=self._last_hash,
            entry_hash=""
        )

        entry.entry_hash = entry.compute_hash()
        self._last_hash = entry.entry_hash

        await self.repository.save(entry)

        # Publish event for real-time monitoring
        await event_bus.publish(AuditLoggedEvent(entry=entry))
```

---

### 8. Health Checks & Observability

```python
# libs/shared/health.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List

class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheckResult:
    name: str
    status: HealthStatus
    latency_ms: float
    message: str | None = None
    details: dict | None = None

class HealthCheck(ABC):
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        pass

class DatabaseHealthCheck(HealthCheck):
    async def check(self) -> HealthCheckResult:
        start = datetime.utcnow()
        try:
            await db.execute("SELECT 1")
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheckResult(
                name="database",
                status=HealthStatus.HEALTHY,
                latency_ms=latency
            )
        except Exception as e:
            return HealthCheckResult(
                name="database",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=str(e)
            )

class RedisHealthCheck(HealthCheck):
    async def check(self) -> HealthCheckResult:
        start = datetime.utcnow()
        try:
            await redis.ping()
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.HEALTHY,
                latency_ms=latency
            )
        except Exception as e:
            return HealthCheckResult(
                name="redis",
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=str(e)
            )

class AIServiceHealthCheck(HealthCheck):
    async def check(self) -> HealthCheckResult:
        start = datetime.utcnow()
        try:
            # Simple completion to verify AI service
            await litellm.acompletion(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )
            latency = (datetime.utcnow() - start).total_seconds() * 1000
            return HealthCheckResult(
                name="ai_service",
                status=HealthStatus.HEALTHY,
                latency_ms=latency
            )
        except Exception as e:
            return HealthCheckResult(
                name="ai_service",
                status=HealthStatus.DEGRADED,  # Degraded, not unhealthy
                latency_ms=0,
                message=str(e)
            )

class HealthService:
    def __init__(self, checks: List[HealthCheck]):
        self.checks = checks

    async def check_all(self) -> Dict:
        results = []
        overall_status = HealthStatus.HEALTHY

        for check in self.checks:
            result = await check.check()
            results.append(result)

            if result.status == HealthStatus.UNHEALTHY:
                overall_status = HealthStatus.UNHEALTHY
            elif result.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.DEGRADED

        return {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat(),
            "checks": [
                {
                    "name": r.name,
                    "status": r.status,
                    "latency_ms": r.latency_ms,
                    "message": r.message
                }
                for r in results
            ]
        }
```

---

### 9. OpenTelemetry Integration

```python
# libs/shared/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from functools import wraps

def setup_telemetry(service_name: str, otlp_endpoint: str):
    """Initialize OpenTelemetry with OTLP exporters"""

    # Tracing
    trace.set_tracer_provider(TracerProvider())
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint))
    )

    # Metrics
    metrics.set_meter_provider(MeterProvider())

    # Auto-instrument frameworks
    FastAPIInstrumentor.instrument()
    HTTPXClientInstrumentor().instrument()
    RedisInstrumentor().instrument()

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Custom metrics
query_duration = meter.create_histogram(
    name="sql2ai.query.duration",
    description="Query execution duration",
    unit="ms"
)

ai_tokens_used = meter.create_counter(
    name="sql2ai.ai.tokens",
    description="AI tokens consumed"
)

active_connections = meter.create_up_down_counter(
    name="sql2ai.connections.active",
    description="Active database connections"
)

def traced(span_name: str = None):
    """Decorator for adding tracing to functions"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with tracer.start_as_current_span(name) as span:
                span.set_attribute("function", func.__name__)
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(trace.Status(trace.StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise
        return wrapper
    return decorator
```

---

### 10. Feature Flags

```python
# libs/shared/features.py
from enum import Enum
from typing import Optional

class Feature(str, Enum):
    # AI Features
    AI_QUERY_OPTIMIZATION = "ai.query_optimization"
    AI_CODE_GENERATION = "ai.code_generation"
    AI_AGENT_MODE = "ai.agent_mode"

    # Database Features
    MULTI_DATABASE = "db.multi_database"
    REAL_TIME_MONITORING = "db.real_time_monitoring"
    QUERY_STORE_ANALYSIS = "db.query_store_analysis"

    # Compliance Features
    COMPLIANCE_SCANNING = "compliance.scanning"
    PII_DETECTION = "compliance.pii_detection"
    AUDIT_EXPORT = "compliance.audit_export"

    # Beta Features
    BETA_LANGGRAPH_AGENTS = "beta.langgraph_agents"
    BETA_VOICE_QUERIES = "beta.voice_queries"

class FeatureFlagService:
    """Feature flag management with rollout support"""

    def __init__(self, repository: 'FeatureFlagRepository'):
        self.repository = repository
        self._cache: dict = {}

    async def is_enabled(
        self,
        feature: Feature,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """Check if feature is enabled for given context"""

        flag = await self._get_flag(feature)
        if not flag:
            return False

        # Global kill switch
        if not flag.enabled:
            return False

        # Check tenant-specific override
        if tenant_id and tenant_id in flag.tenant_overrides:
            return flag.tenant_overrides[tenant_id]

        # Check tier-based access
        if tenant_id:
            tenant = await get_tenant(tenant_id)
            if feature.value not in TIER_LIMITS[tenant.tier].features:
                if '*' not in TIER_LIMITS[tenant.tier].features:
                    return False

        # Percentage rollout
        if flag.rollout_percentage < 100:
            # Consistent hashing for stable rollout
            hash_input = f"{feature.value}:{user_id or tenant_id}"
            bucket = int(hashlib.md5(hash_input.encode()).hexdigest(), 16) % 100
            return bucket < flag.rollout_percentage

        return True

    async def get_all_flags(self, tenant_id: str) -> dict[str, bool]:
        """Get all feature flags for a tenant"""
        result = {}
        for feature in Feature:
            result[feature.value] = await self.is_enabled(feature, tenant_id)
        return result
```

---

## Service Directory Structure

```
sql2ai/
├── apps/
│   ├── api/                          # Main API (FastAPI)
│   │   ├── src/
│   │   │   ├── main.py               # FastAPI app
│   │   │   ├── config.py             # Configuration
│   │   │   ├── dependencies.py       # DI container
│   │   │   │
│   │   │   ├── routers/              # API endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── connections.py
│   │   │   │   ├── queries.py
│   │   │   │   ├── ai.py
│   │   │   │   ├── migrations.py
│   │   │   │   ├── monitoring.py
│   │   │   │   └── health.py
│   │   │   │
│   │   │   ├── services/             # Business logic
│   │   │   │   ├── database_service.py
│   │   │   │   ├── query_service.py
│   │   │   │   ├── migration_service.py
│   │   │   │   └── monitoring_service.py
│   │   │   │
│   │   │   ├── ai/                   # AI layer
│   │   │   │   ├── providers/
│   │   │   │   │   └── litellm_provider.py
│   │   │   │   ├── agents/
│   │   │   │   │   ├── sql_agent.py
│   │   │   │   │   ├── optimizer_agent.py
│   │   │   │   │   └── compliance_agent.py
│   │   │   │   ├── chains/
│   │   │   │   │   ├── query_chain.py
│   │   │   │   │   └── analysis_chain.py
│   │   │   │   └── tools/
│   │   │   │       ├── database_tools.py
│   │   │   │       └── file_tools.py
│   │   │   │
│   │   │   └── middleware/
│   │   │       ├── auth.py
│   │   │       ├── tenant.py
│   │   │       ├── rate_limit.py
│   │   │       └── telemetry.py
│   │   │
│   │   ├── tests/
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── site/                         # Marketing site (Next.js)
│   └── web/                          # Web app (Next.js)
│
├── libs/
│   └── shared/                       # Shared Python library
│       ├── sql2ai_shared/
│       │   ├── __init__.py
│       │   ├── auth/
│       │   │   ├── jwt.py
│       │   │   ├── oauth.py
│       │   │   └── rbac.py
│       │   ├── database/
│       │   │   ├── connection.py
│       │   │   ├── pool.py
│       │   │   └── dialects/
│       │   │       ├── sqlserver.py
│       │   │       └── postgresql.py
│       │   ├── events/
│       │   │   ├── bus.py
│       │   │   ├── store.py
│       │   │   └── types.py
│       │   ├── caching/
│       │   │   ├── manager.py
│       │   │   └── policies.py
│       │   ├── resilience/
│       │   │   ├── circuit_breaker.py
│       │   │   ├── retry.py
│       │   │   └── bulkhead.py
│       │   ├── telemetry/
│       │   │   ├── tracing.py
│       │   │   ├── metrics.py
│       │   │   └── logging.py
│       │   ├── audit/
│       │   │   ├── logger.py
│       │   │   └── models.py
│       │   └── tenancy/
│       │       ├── context.py
│       │       ├── limits.py
│       │       └── rls.py
│       ├── tests/
│       └── pyproject.toml
│
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   └── docker-compose.prod.yml
│   ├── kubernetes/
│   │   ├── base/
│   │   ├── overlays/
│   │   │   ├── dev/
│   │   │   ├── staging/
│   │   │   └── prod/
│   │   └── kustomization.yaml
│   └── terraform/
│       ├── modules/
│       └── environments/
│
└── docs/
    └── architecture/
```

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|------------|---------|
| **API Gateway** | Kong / Traefik | Rate limiting, auth, routing |
| **API Services** | FastAPI | REST API, async, OpenAPI |
| **AI Orchestration** | LiteLLM + LangGraph | Multi-provider AI, agents |
| **Message Queue** | RabbitMQ / Redis Streams | Async jobs, events |
| **Cache** | Redis | Caching, sessions, rate limits |
| **Database** | PostgreSQL | Platform data, audit logs |
| **Search** | Elasticsearch | Query history, logs |
| **Observability** | OpenTelemetry + Grafana | Traces, metrics, dashboards |
| **Secrets** | HashiCorp Vault / AWS Secrets | Credential management |

---

## Next Steps

1. **Create `libs/shared/` Python package** with enterprise patterns
2. **Create `apps/api/` FastAPI service** with AI integration
3. **Set up Docker Compose** for local development
4. **Implement core patterns** (auth, tenancy, events)
5. **Add OpenTelemetry** instrumentation
