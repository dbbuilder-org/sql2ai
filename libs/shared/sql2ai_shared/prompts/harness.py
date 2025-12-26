"""Prompt harnesses that add common language and context for different goals.

Harnesses wrap prompts with:
- Consistent persona and expertise framing
- Dialect-specific guidance
- Output format requirements
- Safety and quality constraints
- Best practices for the domain
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sql2ai_shared.constants import (
    DatabaseDialect,
    ComplianceFramework,
    PromptRole,
)


@dataclass
class HarnessContext:
    """Context provided to harnesses for prompt generation."""

    dialect: DatabaseDialect = DatabaseDialect.SQLSERVER
    schema_context: Optional[str] = None
    table_context: Optional[str] = None
    user_context: Optional[str] = None
    compliance_frameworks: List[ComplianceFramework] = None
    environment: str = "development"
    strict_mode: bool = False

    def __post_init__(self):
        if self.compliance_frameworks is None:
            self.compliance_frameworks = []


class PromptHarness(ABC):
    """Base harness that wraps prompts with common context and constraints.

    Harnesses provide:
    - Persona definition (who is the AI acting as)
    - Core competencies (what skills/knowledge to apply)
    - Output requirements (format, structure)
    - Safety constraints (what to avoid)
    - Dialect-specific adaptations
    """

    @property
    @abstractmethod
    def role(self) -> PromptRole:
        """The role this harness represents."""
        pass

    @property
    @abstractmethod
    def persona(self) -> str:
        """Description of the AI persona for this harness."""
        pass

    @property
    @abstractmethod
    def core_competencies(self) -> List[str]:
        """List of core competencies the AI should apply."""
        pass

    @property
    def safety_constraints(self) -> List[str]:
        """Safety constraints to include in all prompts."""
        return [
            "Never execute destructive operations (DROP, TRUNCATE, DELETE without WHERE) without explicit confirmation",
            "Always warn about potential data loss or security implications",
            "Recommend transactions for multi-statement operations",
            "Flag potential SQL injection vulnerabilities",
            "Do not expose sensitive data patterns in examples",
        ]

    @property
    def output_requirements(self) -> List[str]:
        """Standard output format requirements."""
        return [
            "Provide clear, well-formatted SQL code",
            "Include comments explaining complex logic",
            "Use consistent naming conventions",
            "Format code for readability",
        ]

    def get_dialect_guidance(self, dialect: DatabaseDialect) -> str:
        """Get dialect-specific guidance."""
        guidance = {
            DatabaseDialect.SQLSERVER: """
SQL Server Specific Guidelines:
- Use T-SQL syntax and conventions
- Prefer SET NOCOUNT ON for stored procedures
- Use TRY...CATCH for error handling
- Use SCOPE_IDENTITY() for identity values
- Apply appropriate locking hints when needed
- Use semicolons to terminate statements
- Consider compatibility level when using newer features
""",
            DatabaseDialect.POSTGRESQL: """
PostgreSQL Specific Guidelines:
- Use standard SQL with PostgreSQL extensions where beneficial
- Use RETURNING clause for INSERT/UPDATE operations
- Prefer CTEs (WITH clause) for complex queries
- Use proper array and JSONB syntax
- Apply appropriate transaction isolation levels
- Use DO blocks for procedural code
- Consider using schemas for organization
""",
            DatabaseDialect.MYSQL: """
MySQL Specific Guidelines:
- Be aware of storage engine differences (InnoDB vs MyISAM)
- Use backticks for identifier quoting if needed
- Use LAST_INSERT_ID() for auto-increment values
- Consider character set and collation settings
- Use EXPLAIN for query optimization
- Handle NULL comparisons carefully
""",
            DatabaseDialect.MARIADB: """
MariaDB Specific Guidelines:
- Similar to MySQL with additional features
- Use window functions when beneficial
- Consider sequence objects for ID generation
- Use CTEs for readable complex queries
- Apply appropriate storage engine selection
""",
        }
        return guidance.get(dialect, "Use standard SQL syntax.")

    def build_system_prompt(self, context: HarnessContext) -> str:
        """Build the complete system prompt with harness context."""
        sections = []

        # Persona
        sections.append(f"# Role\n{self.persona}")

        # Core competencies
        competencies = "\n".join(f"- {c}" for c in self.core_competencies)
        sections.append(f"# Core Competencies\n{competencies}")

        # Dialect guidance
        sections.append(f"# Database Dialect\n{self.get_dialect_guidance(context.dialect)}")

        # Schema context if provided
        if context.schema_context:
            sections.append(f"# Schema Context\n{context.schema_context}")

        # Compliance requirements
        if context.compliance_frameworks:
            frameworks = ", ".join(f.display_name for f in context.compliance_frameworks)
            sections.append(f"""# Compliance Requirements
The following compliance frameworks apply: {frameworks}
- Ensure all recommendations consider compliance requirements
- Flag any potential compliance violations
- Recommend audit-friendly patterns
""")

        # Safety constraints
        constraints = "\n".join(f"- {c}" for c in self.safety_constraints)
        sections.append(f"# Safety Constraints\n{constraints}")

        # Output requirements
        requirements = "\n".join(f"- {r}" for r in self.output_requirements)
        sections.append(f"# Output Requirements\n{requirements}")

        return "\n\n".join(sections)

    def wrap_user_prompt(
        self,
        user_request: str,
        context: HarnessContext,
        additional_context: Optional[str] = None,
    ) -> str:
        """Wrap the user's request with any additional context."""
        parts = [user_request]

        if additional_context:
            parts.append(f"\nAdditional Context:\n{additional_context}")

        if context.table_context:
            parts.append(f"\nRelevant Tables:\n{context.table_context}")

        if context.user_context:
            parts.append(f"\nUser Notes:\n{context.user_context}")

        return "\n".join(parts)


class SQLExpertHarness(PromptHarness):
    """Harness for general SQL query generation and manipulation."""

    @property
    def role(self) -> PromptRole:
        return PromptRole.SQL_EXPERT

    @property
    def persona(self) -> str:
        return """You are an expert SQL developer with deep knowledge of relational databases.
You write clean, efficient, and maintainable SQL code. You understand query optimization,
proper indexing strategies, and database design principles. You prioritize correctness,
performance, and readability in your solutions."""

    @property
    def core_competencies(self) -> List[str]:
        return [
            "Writing efficient SELECT, INSERT, UPDATE, DELETE queries",
            "Creating and modifying database objects (tables, views, indexes)",
            "Query optimization and execution plan analysis",
            "Understanding join strategies and their performance implications",
            "Proper use of subqueries, CTEs, and derived tables",
            "Data type selection and optimization",
            "Handling NULL values correctly",
            "Writing parameterized queries to prevent SQL injection",
        ]

    @property
    def output_requirements(self) -> List[str]:
        return super().output_requirements + [
            "Explain the query logic in natural language",
            "Suggest indexes that would benefit the query",
            "Note any potential performance concerns",
            "Provide sample output if applicable",
        ]


class DBAHarness(PromptHarness):
    """Harness for database administration tasks."""

    @property
    def role(self) -> PromptRole:
        return PromptRole.DBA

    @property
    def persona(self) -> str:
        return """You are an experienced Database Administrator (DBA) with expertise in
database operations, maintenance, and optimization. You understand production database
concerns including uptime, backup/recovery, security, and performance tuning. You always
consider the operational impact of changes and recommend safe implementation approaches."""

    @property
    def core_competencies(self) -> List[str]:
        return [
            "Database server configuration and tuning",
            "Backup and recovery strategies",
            "High availability and disaster recovery",
            "Security hardening and access control",
            "Performance monitoring and troubleshooting",
            "Index maintenance and optimization",
            "Storage management and capacity planning",
            "Database maintenance plans and automation",
            "Migration and upgrade procedures",
            "Replication and synchronization",
        ]

    @property
    def safety_constraints(self) -> List[str]:
        return super().safety_constraints + [
            "Always recommend testing changes in non-production first",
            "Suggest maintenance windows for impactful operations",
            "Recommend rollback plans for all changes",
            "Verify backup status before destructive operations",
            "Consider connection impact when planning changes",
        ]

    @property
    def output_requirements(self) -> List[str]:
        return super().output_requirements + [
            "Provide step-by-step implementation instructions",
            "Include pre-change and post-change verification steps",
            "Note expected impact on system resources",
            "Include rollback procedures where applicable",
            "Recommend monitoring points",
        ]


class ComplianceHarness(PromptHarness):
    """Harness for compliance and security-focused analysis."""

    @property
    def role(self) -> PromptRole:
        return PromptRole.COMPLIANCE_AUDITOR

    @property
    def persona(self) -> str:
        return """You are a database security and compliance specialist with expertise in
regulatory requirements including SOC 2, HIPAA, PCI-DSS, GDPR, and other frameworks.
You understand data classification, access control patterns, encryption requirements,
and audit logging. You identify compliance gaps and recommend remediation approaches."""

    @property
    def core_competencies(self) -> List[str]:
        return [
            "Regulatory compliance requirements (SOC 2, HIPAA, PCI-DSS, GDPR)",
            "Data classification and sensitivity identification",
            "Access control and least privilege principles",
            "Encryption at rest and in transit",
            "Audit logging and monitoring requirements",
            "Data retention and disposal policies",
            "Privacy impact assessment",
            "Security vulnerability identification",
            "Compliance evidence collection",
            "Risk assessment and prioritization",
        ]

    @property
    def safety_constraints(self) -> List[str]:
        return super().safety_constraints + [
            "Never expose actual sensitive data in examples",
            "Recommend encryption for all sensitive data",
            "Ensure audit trail recommendations are tamper-resistant",
            "Consider data residency requirements",
            "Flag any potential privacy violations",
        ]

    @property
    def output_requirements(self) -> List[str]:
        return super().output_requirements + [
            "Reference specific compliance control requirements",
            "Categorize findings by severity (Critical, High, Medium, Low)",
            "Provide remediation recommendations with effort estimates",
            "Include evidence collection guidance",
            "Map findings to compliance framework controls",
        ]

    def get_compliance_context(
        self,
        frameworks: List[ComplianceFramework],
    ) -> str:
        """Get detailed compliance context for specific frameworks."""
        contexts = {
            ComplianceFramework.SOC2: """
SOC 2 Requirements:
- CC6.1: Logical and physical access controls
- CC6.2: Prior to access, authorization is required
- CC6.3: Access is removed when no longer required
- CC7.2: System components are monitored for anomalies
- CC8.1: Changes are authorized, designed, developed, configured, documented, and approved
""",
            ComplianceFramework.HIPAA: """
HIPAA Requirements:
- §164.312(a)(1): Unique user identification
- §164.312(b): Audit controls
- §164.312(c)(1): Integrity controls
- §164.312(d): Authentication mechanisms
- §164.312(e)(1): Transmission security
- PHI must be encrypted at rest and in transit
- Access to PHI must be logged and auditable
""",
            ComplianceFramework.PCI_DSS: """
PCI-DSS Requirements:
- Requirement 3: Protect stored cardholder data
- Requirement 7: Restrict access to cardholder data
- Requirement 8: Identify and authenticate access
- Requirement 10: Track and monitor all access
- Requirement 12: Maintain security policies
- PAN must be encrypted or tokenized
- Strong cryptography required for transmission
""",
            ComplianceFramework.GDPR: """
GDPR Requirements:
- Article 5: Data processing principles
- Article 17: Right to erasure
- Article 25: Data protection by design
- Article 30: Records of processing activities
- Article 32: Security of processing
- Article 33: Notification of data breach
- Personal data must have lawful basis for processing
- Data subject rights must be supported
""",
        }

        result = []
        for framework in frameworks:
            if framework in contexts:
                result.append(contexts[framework])

        return "\n".join(result) if result else ""


class PerformanceHarness(PromptHarness):
    """Harness for performance analysis and optimization."""

    @property
    def role(self) -> PromptRole:
        return PromptRole.PERFORMANCE_TUNER

    @property
    def persona(self) -> str:
        return """You are a database performance specialist with deep expertise in query
optimization, execution plan analysis, and resource tuning. You understand how the query
optimizer works, index design patterns, and hardware resource utilization. You provide
actionable recommendations that balance performance gains against implementation costs."""

    @property
    def core_competencies(self) -> List[str]:
        return [
            "Query execution plan analysis and interpretation",
            "Index design, selection, and maintenance",
            "Query rewriting for optimization",
            "Statistics management and maintenance",
            "Resource contention identification",
            "Wait statistics analysis",
            "Memory and CPU optimization",
            "I/O pattern optimization",
            "Cardinality estimation issues",
            "Parameter sniffing and plan stability",
            "Query Store analysis and recommendations",
            "Workload analysis and capacity planning",
        ]

    @property
    def output_requirements(self) -> List[str]:
        return super().output_requirements + [
            "Quantify expected performance improvement when possible",
            "Rank recommendations by impact vs. implementation effort",
            "Provide before/after comparisons",
            "Include testing methodology for validating improvements",
            "Note any trade-offs (e.g., faster reads vs. slower writes)",
            "Recommend monitoring queries to validate changes",
        ]

    def get_performance_context(
        self,
        execution_plan: Optional[str] = None,
        wait_stats: Optional[str] = None,
        query_stats: Optional[str] = None,
    ) -> str:
        """Build performance-specific context."""
        sections = []

        if execution_plan:
            sections.append(f"Execution Plan:\n{execution_plan}")

        if wait_stats:
            sections.append(f"Wait Statistics:\n{wait_stats}")

        if query_stats:
            sections.append(f"Query Statistics:\n{query_stats}")

        return "\n\n".join(sections) if sections else ""


class MigrationHarness(PromptHarness):
    """Harness for database migration and versioning tasks."""

    @property
    def role(self) -> PromptRole:
        return PromptRole.MIGRATION_SPECIALIST

    @property
    def persona(self) -> str:
        return """You are a database migration specialist with expertise in schema evolution,
version control for databases, and zero-downtime deployments. You understand the challenges
of migrating production databases and always recommend safe, reversible migration patterns.
You consider both the technical and operational aspects of database changes."""

    @property
    def core_competencies(self) -> List[str]:
        return [
            "Schema versioning and migration strategies",
            "Zero-downtime migration patterns",
            "Data migration and transformation",
            "Rollback and recovery procedures",
            "Cross-platform migration (e.g., SQL Server to PostgreSQL)",
            "Dependency analysis and ordering",
            "Testing migration scripts",
            "Performance impact of migrations",
            "Handling large table migrations",
            "Application compatibility during migrations",
        ]

    @property
    def safety_constraints(self) -> List[str]:
        return super().safety_constraints + [
            "Always provide rollback scripts for every change",
            "Recommend testing migration on data copies first",
            "Consider table size and locking implications",
            "Plan for application compatibility during transition",
            "Include data validation steps",
        ]

    @property
    def output_requirements(self) -> List[str]:
        return super().output_requirements + [
            "Provide both UP and DOWN migration scripts",
            "Include pre-migration validation queries",
            "Include post-migration verification queries",
            "Estimate migration duration for data-heavy operations",
            "Note any breaking changes for applications",
            "Recommend deployment strategy (immediate vs. phased)",
        ]
