"""
SQL2.AI Shared Enterprise Library

Core enterprise patterns for building scalable, resilient database services.

Modules:
- tenancy: Multi-tenant context and limits
- auth: JWT authentication and authorization
- events: Domain event bus
- resilience: Retry, circuit breaker, bulkhead patterns
- database: SQL Server/PostgreSQL connection pools
- caching: Redis distributed caching
- telemetry: OpenTelemetry tracing, metrics, logging
- audit: Tamper-proof audit logging
- ai: LiteLLM and LangGraph AI integration
- prompts: Versionable prompts with harnesses and tracking
- integrations: Third-party service integrations
- constants: Centralized string constants
"""

__version__ = "0.1.0"

# Tenancy
from sql2ai_shared.tenancy.context import Tenant, TenantContext, get_current_tenant
from sql2ai_shared.tenancy.limits import TenantLimits, check_limit

# Auth
from sql2ai_shared.auth.models import User, TokenPayload, AuthResult, Role
from sql2ai_shared.auth.jwt import JWTService, create_jwt_service

# Events
from sql2ai_shared.events.types import DomainEvent
from sql2ai_shared.events.bus import EventBus, get_event_bus, publish

# Resilience
from sql2ai_shared.resilience.retry import with_retry, RetryConfig
from sql2ai_shared.resilience.circuit_breaker import circuit_protected
from sql2ai_shared.resilience.bulkhead import Bulkhead, create_bulkhead

# Database
from sql2ai_shared.database.connection import (
    DatabaseType,
    DatabaseConfig,
    DatabaseConnection,
    create_connection,
)
from sql2ai_shared.database.pool import ConnectionPool, get_pool, create_pool

# Caching
from sql2ai_shared.caching.redis import RedisConfig, RedisCache, get_cache, create_cache
from sql2ai_shared.caching.decorators import cached, invalidate

# Telemetry
from sql2ai_shared.telemetry.tracing import init_tracing, traced, get_tracer
from sql2ai_shared.telemetry.metrics import init_metrics, counter, histogram
from sql2ai_shared.telemetry.logging import init_logging, get_logger

# Audit
from sql2ai_shared.audit.models import AuditAction, AuditEntry, AuditSeverity
from sql2ai_shared.audit.logger import AuditLogger, get_audit_logger, create_audit_logger
from sql2ai_shared.audit.decorators import audited

# AI
from sql2ai_shared.ai.providers import AIConfig, AIProvider, get_ai_provider, create_ai_provider
from sql2ai_shared.ai.models import Message, ChatRequest, ChatResponse
from sql2ai_shared.ai.agents import AgentConfig, AgentState, SQLAgent

# Constants
from sql2ai_shared.constants import (
    DatabaseDialect,
    SQLOperation,
    ObjectType,
    AIModel,
    EmbeddingModel,
    ComplianceFramework,
    PromptRole,
    PromptCategory,
    FeatureFlag,
    ErrorMessages,
    SuccessMessages,
    UILabels,
    TierLimits,
)

# Prompts
from sql2ai_shared.prompts import (
    Prompt,
    PromptVersion,
    PromptExecution,
    prompt_registry,
    PromptExecutor,
    ExecutionConfig,
    ExecutionResult,
    # Harnesses
    SQLExpertHarness,
    DBAHarness,
    ComplianceHarness,
    PerformanceHarness,
    # Templates
    QueryGenerationPrompt,
    QueryOptimizationPrompt,
    QueryExplanationPrompt,
    ComplianceCheckPrompt,
)

__all__ = [
    # Tenancy
    "Tenant",
    "TenantContext",
    "get_current_tenant",
    "TenantLimits",
    "check_limit",
    # Auth
    "User",
    "TokenPayload",
    "AuthResult",
    "Role",
    "JWTService",
    "create_jwt_service",
    # Events
    "DomainEvent",
    "EventBus",
    "get_event_bus",
    "publish",
    # Resilience
    "with_retry",
    "RetryConfig",
    "circuit_protected",
    "Bulkhead",
    "create_bulkhead",
    # Database
    "DatabaseType",
    "DatabaseConfig",
    "DatabaseConnection",
    "create_connection",
    "ConnectionPool",
    "get_pool",
    "create_pool",
    # Caching
    "RedisConfig",
    "RedisCache",
    "get_cache",
    "create_cache",
    "cached",
    "invalidate",
    # Telemetry
    "init_tracing",
    "traced",
    "get_tracer",
    "init_metrics",
    "counter",
    "histogram",
    "init_logging",
    "get_logger",
    # Audit
    "AuditAction",
    "AuditEntry",
    "AuditSeverity",
    "AuditLogger",
    "get_audit_logger",
    "create_audit_logger",
    "audited",
    # AI
    "AIConfig",
    "AIProvider",
    "get_ai_provider",
    "create_ai_provider",
    "Message",
    "ChatRequest",
    "ChatResponse",
    "AgentConfig",
    "AgentState",
    "SQLAgent",
    # Constants
    "DatabaseDialect",
    "SQLOperation",
    "ObjectType",
    "AIModel",
    "EmbeddingModel",
    "ComplianceFramework",
    "PromptRole",
    "PromptCategory",
    "FeatureFlag",
    "ErrorMessages",
    "SuccessMessages",
    "UILabels",
    "TierLimits",
    # Prompts
    "Prompt",
    "PromptVersion",
    "PromptExecution",
    "prompt_registry",
    "PromptExecutor",
    "ExecutionConfig",
    "ExecutionResult",
    "SQLExpertHarness",
    "DBAHarness",
    "ComplianceHarness",
    "PerformanceHarness",
    "QueryGenerationPrompt",
    "QueryOptimizationPrompt",
    "QueryExplanationPrompt",
    "ComplianceCheckPrompt",
]
