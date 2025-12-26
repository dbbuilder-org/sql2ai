"""SQLAlchemy models for SQL2.AI platform."""

from sql2ai_api.models.tenant import Tenant, TenantTier
from sql2ai_api.models.user import User, UserRole
from sql2ai_api.models.connection import Connection, DatabaseType
from sql2ai_api.models.query import Query, QueryExecution, QueryStatus
from sql2ai_api.models.audit import AuditLog, AuditAction

__all__ = [
    # Tenant
    "Tenant",
    "TenantTier",
    # User
    "User",
    "UserRole",
    # Connection
    "Connection",
    "DatabaseType",
    # Query
    "Query",
    "QueryExecution",
    "QueryStatus",
    # Audit
    "AuditLog",
    "AuditAction",
]
