"""Centralized string constants for SQL2.AI platform."""

from enum import Enum
from typing import Final


# =============================================================================
# Database Dialects
# =============================================================================

class DatabaseDialect(str, Enum):
    """Supported database dialects."""

    SQLSERVER = "sqlserver"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MARIADB = "mariadb"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names = {
            "sqlserver": "SQL Server",
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mariadb": "MariaDB",
        }
        return names.get(self.value, self.value)

    @property
    def version_query(self) -> str:
        """Query to get database version."""
        queries = {
            "sqlserver": "SELECT @@VERSION",
            "postgresql": "SELECT version()",
            "mysql": "SELECT VERSION()",
            "mariadb": "SELECT VERSION()",
        }
        return queries.get(self.value, "SELECT 1")


# =============================================================================
# SQL Operations
# =============================================================================

class SQLOperation(str, Enum):
    """Types of SQL operations."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    ALTER = "alter"
    DROP = "drop"
    TRUNCATE = "truncate"
    EXECUTE = "execute"
    MERGE = "merge"


class ObjectType(str, Enum):
    """Database object types."""

    TABLE = "table"
    VIEW = "view"
    STORED_PROCEDURE = "stored_procedure"
    FUNCTION = "function"
    TRIGGER = "trigger"
    INDEX = "index"
    CONSTRAINT = "constraint"
    SCHEMA = "schema"
    SEQUENCE = "sequence"
    TYPE = "type"


# =============================================================================
# AI Model Constants
# =============================================================================

class AIModel(str, Enum):
    """Supported AI models."""

    # OpenAI
    GPT4 = "gpt-4"
    GPT4_TURBO = "gpt-4-turbo"
    GPT4O = "gpt-4o"
    GPT4O_MINI = "gpt-4o-mini"
    GPT35_TURBO = "gpt-3.5-turbo"

    # Anthropic
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"

    # Azure
    AZURE_GPT4 = "azure/gpt-4"
    AZURE_GPT4_TURBO = "azure/gpt-4-turbo"


class EmbeddingModel(str, Enum):
    """Supported embedding models."""

    OPENAI_SMALL = "text-embedding-3-small"
    OPENAI_LARGE = "text-embedding-3-large"
    OPENAI_ADA = "text-embedding-ada-002"


# =============================================================================
# Compliance Frameworks
# =============================================================================

class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""

    SOC2 = "soc2"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    GDPR = "gdpr"
    FERPA = "ferpa"
    CCPA = "ccpa"
    ISO27001 = "iso27001"

    @property
    def display_name(self) -> str:
        names = {
            "soc2": "SOC 2",
            "hipaa": "HIPAA",
            "pci_dss": "PCI-DSS",
            "gdpr": "GDPR",
            "ferpa": "FERPA",
            "ccpa": "CCPA",
            "iso27001": "ISO 27001",
        }
        return names.get(self.value, self.value.upper())


# =============================================================================
# Error Messages
# =============================================================================

class ErrorMessages:
    """Standardized error messages."""

    # Authentication
    AUTH_INVALID_TOKEN: Final = "Invalid or expired authentication token"
    AUTH_MISSING_TOKEN: Final = "Authentication token required"
    AUTH_INSUFFICIENT_PERMISSIONS: Final = "Insufficient permissions for this operation"

    # Resources
    RESOURCE_NOT_FOUND: Final = "The requested resource was not found"
    CONNECTION_NOT_FOUND: Final = "Database connection not found"
    QUERY_NOT_FOUND: Final = "Query not found"
    TENANT_NOT_FOUND: Final = "Tenant not found"
    USER_NOT_FOUND: Final = "User not found"

    # Validation
    VALIDATION_FAILED: Final = "Request validation failed"
    INVALID_SQL_SYNTAX: Final = "Invalid SQL syntax"
    INVALID_CONNECTION_PARAMS: Final = "Invalid connection parameters"

    # Operations
    CONNECTION_FAILED: Final = "Failed to connect to database"
    QUERY_EXECUTION_FAILED: Final = "Query execution failed"
    QUERY_TIMEOUT: Final = "Query execution timed out"
    RATE_LIMIT_EXCEEDED: Final = "Rate limit exceeded, please try again later"

    # Limits
    MAX_CONNECTIONS_REACHED: Final = "Maximum number of connections reached for your plan"
    MAX_QUERIES_REACHED: Final = "Daily query limit reached for your plan"
    QUOTA_EXCEEDED: Final = "Usage quota exceeded"


# =============================================================================
# Success Messages
# =============================================================================

class SuccessMessages:
    """Standardized success messages."""

    CONNECTION_CREATED: Final = "Database connection created successfully"
    CONNECTION_UPDATED: Final = "Database connection updated successfully"
    CONNECTION_DELETED: Final = "Database connection deleted successfully"
    CONNECTION_TEST_SUCCESS: Final = "Connection test successful"

    QUERY_SAVED: Final = "Query saved successfully"
    QUERY_EXECUTED: Final = "Query executed successfully"
    QUERY_DELETED: Final = "Query deleted successfully"

    USER_INVITED: Final = "User invitation sent successfully"
    USER_UPDATED: Final = "User updated successfully"
    USER_REMOVED: Final = "User removed successfully"


# =============================================================================
# UI Labels
# =============================================================================

class UILabels:
    """UI string constants for consistency."""

    # Actions
    ACTION_SAVE: Final = "Save"
    ACTION_CANCEL: Final = "Cancel"
    ACTION_DELETE: Final = "Delete"
    ACTION_EDIT: Final = "Edit"
    ACTION_CREATE: Final = "Create"
    ACTION_TEST: Final = "Test Connection"
    ACTION_EXECUTE: Final = "Execute"
    ACTION_OPTIMIZE: Final = "Optimize"
    ACTION_EXPLAIN: Final = "Explain"
    ACTION_GENERATE: Final = "Generate SQL"

    # Sections
    SECTION_CONNECTIONS: Final = "Database Connections"
    SECTION_QUERIES: Final = "Queries"
    SECTION_HISTORY: Final = "Query History"
    SECTION_SETTINGS: Final = "Settings"
    SECTION_COMPLIANCE: Final = "Compliance"
    SECTION_MONITORING: Final = "Monitoring"

    # Status
    STATUS_CONNECTED: Final = "Connected"
    STATUS_DISCONNECTED: Final = "Disconnected"
    STATUS_PENDING: Final = "Pending"
    STATUS_RUNNING: Final = "Running"
    STATUS_COMPLETED: Final = "Completed"
    STATUS_FAILED: Final = "Failed"
    STATUS_ACTIVE: Final = "Active"
    STATUS_INACTIVE: Final = "Inactive"


# =============================================================================
# Prompt Roles
# =============================================================================

class PromptRole(str, Enum):
    """AI assistant roles for different contexts."""

    SQL_EXPERT = "sql_expert"
    DBA = "dba"
    SECURITY_ANALYST = "security_analyst"
    COMPLIANCE_AUDITOR = "compliance_auditor"
    PERFORMANCE_TUNER = "performance_tuner"
    DATA_ARCHITECT = "data_architect"
    MIGRATION_SPECIALIST = "migration_specialist"


# =============================================================================
# Prompt Categories
# =============================================================================

class PromptCategory(str, Enum):
    """Categories of prompts for organization."""

    QUERY_GENERATION = "query_generation"
    QUERY_OPTIMIZATION = "query_optimization"
    QUERY_EXPLANATION = "query_explanation"
    CODE_REVIEW = "code_review"
    SCHEMA_ANALYSIS = "schema_analysis"
    COMPLIANCE_CHECK = "compliance_check"
    MIGRATION = "migration"
    DOCUMENTATION = "documentation"
    ERROR_ANALYSIS = "error_analysis"
    PERFORMANCE_ANALYSIS = "performance_analysis"


# =============================================================================
# Feature Flags
# =============================================================================

class FeatureFlag(str, Enum):
    """Feature flag identifiers."""

    AI_QUERY_GENERATION = "ai_query_generation"
    AI_OPTIMIZATION = "ai_optimization"
    COMPLIANCE_SCANNING = "compliance_scanning"
    REAL_TIME_MONITORING = "real_time_monitoring"
    ADVANCED_ANALYTICS = "advanced_analytics"
    ENTERPRISE_SSO = "enterprise_sso"
    CUSTOM_ROLES = "custom_roles"
    API_ACCESS = "api_access"
    AUDIT_LOGGING = "audit_logging"
    DATA_MASKING = "data_masking"


# =============================================================================
# Tier Limits
# =============================================================================

class TierLimits:
    """Default limits per subscription tier."""

    FREE_MAX_CONNECTIONS: Final = 1
    FREE_MAX_QUERIES_PER_DAY: Final = 100
    FREE_MAX_USERS: Final = 1
    FREE_MAX_AI_TOKENS_PER_MONTH: Final = 10000

    PRO_MAX_CONNECTIONS: Final = 10
    PRO_MAX_QUERIES_PER_DAY: Final = 10000
    PRO_MAX_USERS: Final = 10
    PRO_MAX_AI_TOKENS_PER_MONTH: Final = 500000

    ENTERPRISE_MAX_CONNECTIONS: Final = -1  # Unlimited
    ENTERPRISE_MAX_QUERIES_PER_DAY: Final = -1  # Unlimited
    ENTERPRISE_MAX_USERS: Final = -1  # Unlimited
    ENTERPRISE_MAX_AI_TOKENS_PER_MONTH: Final = -1  # Unlimited
