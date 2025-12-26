"""Versioned prompt templates for SQL2.AI operations.

Each template is a complete, version-tracked prompt that can be:
- Registered in the prompt registry
- Tracked for execution metrics
- A/B tested against variations
- Rolled back to previous versions
"""

from typing import List, Optional

from sql2ai_shared.constants import (
    DatabaseDialect,
    PromptCategory,
    PromptRole,
    AIModel,
    ComplianceFramework,
)
from sql2ai_shared.prompts.base import (
    Prompt,
    PromptVersion,
    prompt_registry,
)
from sql2ai_shared.prompts.harness import (
    SQLExpertHarness,
    DBAHarness,
    ComplianceHarness,
    PerformanceHarness,
    MigrationHarness,
    HarnessContext,
)


# =============================================================================
# Query Generation Prompts
# =============================================================================

@prompt_registry.register
class QueryGenerationPrompt(Prompt):
    """Generate SQL from natural language description."""

    _name = "query_generation"
    _description = "Generate SQL queries from natural language requests"
    _category = PromptCategory.QUERY_GENERATION
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["generation", "natural-language", "core"]
    _recommended_model = AIModel.GPT4O
    _temperature = 0.3

    def __init__(
        self,
        request: str,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        schema_context: Optional[str] = None,
        table_list: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(
            request=request,
            dialect=dialect,
            schema_context=schema_context or "",
            table_list=", ".join(table_list) if table_list else "",
            **kwargs,
        )
        self._harness = SQLExpertHarness()
        self._context = HarnessContext(dialect=dialect, schema_context=schema_context)

    @property
    def system_prompt(self) -> str:
        return self._harness.build_system_prompt(self._context) + """

# Task: SQL Query Generation

Generate a SQL query based on the user's natural language request. Follow these guidelines:

1. **Understand Intent**: Parse the user's request to understand what data they need
2. **Select Appropriate Tables**: Use the schema context to identify relevant tables
3. **Build Query**: Construct an efficient query that fulfills the request
4. **Validate**: Ensure the query is syntactically correct for the target dialect
5. **Optimize**: Apply basic optimization principles (proper joins, avoid SELECT *)

# Output Format

Provide your response in the following format:

```sql
-- Generated query
<your SQL query here>
```

**Explanation**: <Brief explanation of what the query does>

**Tables Used**: <List of tables referenced>

**Suggestions**: <Any recommendations for indexes or improvements>
"""

    @property
    def user_prompt_template(self) -> str:
        return """Generate a {dialect.display_name} query for the following request:

Request: {request}

{schema_context}

{table_list}"""


@prompt_registry.register
class QueryFromExamplePrompt(Prompt):
    """Generate SQL that produces output matching a given example."""

    _name = "query_from_example"
    _description = "Generate SQL based on example output data"
    _category = PromptCategory.QUERY_GENERATION
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["generation", "example-based"]
    _temperature = 0.2

    def __init__(
        self,
        example_output: str,
        schema_context: str,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        **kwargs,
    ):
        super().__init__(
            example_output=example_output,
            schema_context=schema_context,
            dialect=dialect,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert SQL developer. Given an example of desired output data
and a database schema, you generate the SQL query that would produce that output.

# Guidelines
- Analyze the example output to understand the data structure
- Identify which tables and columns are needed
- Construct a query that would produce matching results
- Handle any necessary joins, aggregations, or transformations
- Ensure the query is efficient and correct
"""

    @property
    def user_prompt_template(self) -> str:
        return """Based on this example output, generate a query that would produce it:

Example Output:
{example_output}

Schema:
{schema_context}

Database: {dialect.display_name}

Provide the SQL query that would generate this output."""


# =============================================================================
# Query Optimization Prompts
# =============================================================================

@prompt_registry.register
class QueryOptimizationPrompt(Prompt):
    """Analyze and optimize a SQL query."""

    _name = "query_optimization"
    _description = "Analyze and optimize SQL queries for better performance"
    _category = PromptCategory.QUERY_OPTIMIZATION
    _role = PromptRole.PERFORMANCE_TUNER
    _version = PromptVersion(major=1, minor=1, patch=0)
    _tags = ["optimization", "performance", "core"]
    _recommended_model = AIModel.GPT4
    _temperature = 0.3

    def __init__(
        self,
        sql: str,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        schema_context: Optional[str] = None,
        execution_plan: Optional[str] = None,
        current_indexes: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            sql=sql,
            dialect=dialect,
            schema_context=schema_context or "",
            execution_plan=execution_plan or "",
            current_indexes=current_indexes or "",
            **kwargs,
        )
        self._harness = PerformanceHarness()
        self._context = HarnessContext(dialect=dialect, schema_context=schema_context)

    @property
    def system_prompt(self) -> str:
        return self._harness.build_system_prompt(self._context) + """

# Task: Query Optimization

Analyze the provided SQL query and suggest optimizations. Consider:

1. **Query Structure**: Join order, subquery vs. CTE, set operations
2. **Indexing**: Missing indexes, unused indexes, covering indexes
3. **Execution Plan**: If provided, identify expensive operations
4. **Statistics**: Cardinality issues, outdated statistics
5. **Anti-patterns**: SELECT *, implicit conversions, functions on indexed columns

# Output Format

## Analysis
<Your analysis of the current query's performance characteristics>

## Issues Found
1. <Issue 1 with severity: Critical/High/Medium/Low>
2. <Issue 2>
...

## Optimized Query
```sql
<Your optimized query>
```

## Recommended Indexes
```sql
<CREATE INDEX statements>
```

## Expected Improvement
<Quantified estimate of improvement where possible>
"""

    @property
    def user_prompt_template(self) -> str:
        return """Optimize this {dialect.display_name} query:

```sql
{sql}
```

Schema Context:
{schema_context}

Execution Plan:
{execution_plan}

Current Indexes:
{current_indexes}"""


# =============================================================================
# Query Explanation Prompts
# =============================================================================

@prompt_registry.register
class QueryExplanationPrompt(Prompt):
    """Explain what a SQL query does in plain language."""

    _name = "query_explanation"
    _description = "Explain SQL queries in plain language"
    _category = PromptCategory.QUERY_EXPLANATION
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["explanation", "documentation"]
    _temperature = 0.5

    def __init__(
        self,
        sql: str,
        detail_level: str = "standard",  # brief, standard, detailed
        audience: str = "technical",  # technical, business, beginner
        **kwargs,
    ):
        super().__init__(
            sql=sql,
            detail_level=detail_level,
            audience=audience,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert at explaining SQL queries to different audiences.
Adapt your explanation style based on the requested audience and detail level.

# Audience Styles
- **technical**: Use proper database terminology, discuss execution implications
- **business**: Focus on what data is retrieved and why it matters
- **beginner**: Explain concepts step-by-step, define SQL terms

# Detail Levels
- **brief**: One paragraph summary
- **standard**: Structured explanation with key points
- **detailed**: Line-by-line walkthrough with examples
"""

    @property
    def user_prompt_template(self) -> str:
        return """Explain this SQL query for a {audience} audience at {detail_level} detail:

```sql
{sql}
```

Provide:
1. A plain language summary
2. What tables and data are involved
3. Any filtering or transformations applied
4. The expected output structure"""


# =============================================================================
# Schema Analysis Prompts
# =============================================================================

@prompt_registry.register
class SchemaAnalysisPrompt(Prompt):
    """Analyze database schema for design issues and improvements."""

    _name = "schema_analysis"
    _description = "Analyze database schema for design patterns and issues"
    _category = PromptCategory.SCHEMA_ANALYSIS
    _role = PromptRole.DATA_ARCHITECT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["schema", "design", "architecture"]
    _temperature = 0.4

    def __init__(
        self,
        schema_ddl: str,
        analysis_focus: Optional[str] = None,  # normalization, performance, security
        **kwargs,
    ):
        super().__init__(
            schema_ddl=schema_ddl,
            analysis_focus=analysis_focus or "general",
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a database architect analyzing schema design. Evaluate:

# Design Principles
- Normalization level and appropriateness
- Referential integrity and constraints
- Data type selections
- Naming conventions
- Index strategy

# Analysis Areas
- **normalization**: Focus on normal forms, redundancy, dependencies
- **performance**: Focus on query patterns, indexing, denormalization needs
- **security**: Focus on access patterns, sensitive data, encryption needs
- **general**: Comprehensive review of all areas

Provide actionable recommendations with clear reasoning.
"""

    @property
    def user_prompt_template(self) -> str:
        return """Analyze this database schema with focus on {analysis_focus}:

```sql
{schema_ddl}
```

Provide:
1. Summary of the schema design
2. Issues found (categorized by severity)
3. Recommendations with implementation examples"""


# =============================================================================
# Code Review Prompts
# =============================================================================

@prompt_registry.register
class CodeReviewPrompt(Prompt):
    """Review SQL code for quality, security, and best practices."""

    _name = "code_review"
    _description = "Review SQL code for quality and best practices"
    _category = PromptCategory.CODE_REVIEW
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["review", "quality", "security"]
    _temperature = 0.3

    def __init__(
        self,
        sql_code: str,
        code_type: str = "query",  # query, procedure, function, trigger
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        **kwargs,
    ):
        super().__init__(
            sql_code=sql_code,
            code_type=code_type,
            dialect=dialect,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are a senior SQL developer conducting code review. Evaluate:

# Review Criteria

## Correctness
- Logic errors
- Edge case handling
- NULL handling
- Data type compatibility

## Security
- SQL injection vulnerabilities
- Privilege escalation risks
- Sensitive data exposure
- Input validation

## Performance
- Query efficiency
- Index usage
- Resource consumption
- Scalability concerns

## Maintainability
- Code clarity
- Comments and documentation
- Naming conventions
- Error handling

## Best Practices
- Dialect-specific conventions
- Transaction usage
- Error handling patterns
- Testing considerations

Rate issues as: Critical, High, Medium, Low, or Suggestion
"""

    @property
    def user_prompt_template(self) -> str:
        return """Review this {code_type} ({dialect.display_name}):

```sql
{sql_code}
```

Provide a structured review with:
1. Summary assessment
2. Issues found (with severity and line numbers)
3. Recommended fixes
4. Suggestions for improvement"""


# =============================================================================
# Compliance Check Prompts
# =============================================================================

@prompt_registry.register
class ComplianceCheckPrompt(Prompt):
    """Check SQL code or schema for compliance with regulatory frameworks."""

    _name = "compliance_check"
    _description = "Check for compliance with regulatory frameworks"
    _category = PromptCategory.COMPLIANCE_CHECK
    _role = PromptRole.COMPLIANCE_AUDITOR
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["compliance", "security", "audit"]
    _temperature = 0.2

    def __init__(
        self,
        sql_or_schema: str,
        frameworks: List[ComplianceFramework],
        check_type: str = "schema",  # schema, query, procedure
        **kwargs,
    ):
        framework_names = ", ".join(f.display_name for f in frameworks)
        super().__init__(
            sql_or_schema=sql_or_schema,
            frameworks=frameworks,
            framework_names=framework_names,
            check_type=check_type,
            **kwargs,
        )
        self._harness = ComplianceHarness()

    @property
    def system_prompt(self) -> str:
        frameworks = self.variables.get("frameworks", [])
        compliance_context = self._harness.get_compliance_context(frameworks)

        return f"""You are a database compliance specialist. Evaluate database objects
against regulatory requirements.

{compliance_context}

# Compliance Check Guidelines

For each finding, provide:
1. **Control Reference**: Specific framework control (e.g., HIPAA §164.312(b))
2. **Severity**: Critical, High, Medium, Low
3. **Description**: Clear explanation of the compliance gap
4. **Evidence**: Specific code/schema element causing the issue
5. **Remediation**: Specific steps to achieve compliance
6. **Verification**: How to confirm the issue is resolved

Focus on:
- Data protection and encryption requirements
- Access control and authentication
- Audit logging and monitoring
- Data classification and handling
- Retention and disposal requirements
"""

    @property
    def user_prompt_template(self) -> str:
        return """Check this {check_type} for compliance with {framework_names}:

```sql
{sql_or_schema}
```

Provide a compliance assessment with:
1. Compliance score (percentage)
2. Findings organized by framework
3. Prioritized remediation plan
4. Compliance evidence checklist"""


# =============================================================================
# Migration Prompts
# =============================================================================

@prompt_registry.register
class MigrationPrompt(Prompt):
    """Generate database migration scripts."""

    _name = "migration_generation"
    _description = "Generate database migration scripts"
    _category = PromptCategory.MIGRATION
    _role = PromptRole.MIGRATION_SPECIALIST
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["migration", "versioning", "deployment"]
    _temperature = 0.2

    def __init__(
        self,
        change_description: str,
        current_schema: Optional[str] = None,
        target_schema: Optional[str] = None,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        **kwargs,
    ):
        super().__init__(
            change_description=change_description,
            current_schema=current_schema or "",
            target_schema=target_schema or "",
            dialect=dialect,
            **kwargs,
        )
        self._harness = MigrationHarness()
        self._context = HarnessContext(dialect=dialect)

    @property
    def system_prompt(self) -> str:
        return self._harness.build_system_prompt(self._context) + """

# Task: Migration Script Generation

Generate safe, reversible migration scripts. Include:

1. **Pre-migration Checks**: Validation before applying changes
2. **UP Migration**: Forward migration script
3. **DOWN Migration**: Rollback script
4. **Post-migration Validation**: Verification queries

# Migration Patterns

Use these safe patterns:
- Add columns as nullable first, then add constraints
- Create new tables before dropping old ones
- Use transactions where supported
- Include progress logging for long operations
- Consider table size for lock duration

# Output Format

```sql
-- Pre-migration validation
<validation queries>

-- UP Migration
BEGIN TRANSACTION;
<forward migration>
COMMIT;

-- Post-migration validation
<verification queries>

-- DOWN Migration (Rollback)
BEGIN TRANSACTION;
<rollback migration>
COMMIT;
```
"""

    @property
    def user_prompt_template(self) -> str:
        return """Generate a migration for {dialect.display_name}:

Change Description:
{change_description}

Current Schema:
{current_schema}

Target Schema:
{target_schema}

Provide UP and DOWN migrations with validation steps."""


# =============================================================================
# Error Analysis Prompts
# =============================================================================

@prompt_registry.register
class ErrorAnalysisPrompt(Prompt):
    """Analyze SQL errors and provide solutions."""

    _name = "error_analysis"
    _description = "Analyze SQL errors and suggest fixes"
    _category = PromptCategory.ERROR_ANALYSIS
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["debugging", "errors", "troubleshooting"]
    _temperature = 0.3

    def __init__(
        self,
        error_message: str,
        sql_code: str,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        context: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(
            error_message=error_message,
            sql_code=sql_code,
            dialect=dialect,
            context=context or "",
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        return """You are an expert at diagnosing and fixing SQL errors. Your approach:

# Diagnosis Process
1. Parse the error message to identify the root cause
2. Locate the problematic code section
3. Understand the context and intent
4. Identify the fix and any related issues

# Common Error Categories
- Syntax errors: Missing keywords, incorrect structure
- Semantic errors: Invalid references, type mismatches
- Runtime errors: Constraint violations, conversion failures
- Permission errors: Access denied, insufficient privileges
- Resource errors: Deadlocks, timeouts, out of memory

# Response Format
1. **Error Explanation**: What the error means in plain language
2. **Root Cause**: The specific issue in the code
3. **Solution**: The corrected code with explanation
4. **Prevention**: How to avoid this error in the future
"""

    @property
    def user_prompt_template(self) -> str:
        return """Analyze this {dialect.display_name} error:

Error Message:
{error_message}

SQL Code:
```sql
{sql_code}
```

Additional Context:
{context}

Explain the error and provide a fix."""


# =============================================================================
# Stored Procedure Generation
# =============================================================================

@prompt_registry.register
class StoredProcedurePrompt(Prompt):
    """Generate stored procedures with proper patterns."""

    _name = "stored_procedure_generation"
    _description = "Generate stored procedures with best practices"
    _category = PromptCategory.QUERY_GENERATION
    _role = PromptRole.SQL_EXPERT
    _version = PromptVersion(major=1, minor=0, patch=0)
    _tags = ["generation", "procedures", "advanced"]
    _temperature = 0.3
    _max_tokens = 2000

    def __init__(
        self,
        description: str,
        schema_context: str,
        dialect: DatabaseDialect = DatabaseDialect.SQLSERVER,
        include_error_handling: bool = True,
        include_audit_logging: bool = False,
        include_transaction: bool = True,
        **kwargs,
    ):
        super().__init__(
            description=description,
            schema_context=schema_context,
            dialect=dialect,
            include_error_handling=include_error_handling,
            include_audit_logging=include_audit_logging,
            include_transaction=include_transaction,
            **kwargs,
        )

    @property
    def system_prompt(self) -> str:
        dialect = self.variables.get("dialect", DatabaseDialect.SQLSERVER)

        if dialect == DatabaseDialect.SQLSERVER:
            return """You are an expert T-SQL developer creating stored procedures.

# T-SQL Stored Procedure Patterns

## Standard Template
```sql
CREATE OR ALTER PROCEDURE [schema].[ProcedureName]
    @Param1 DataType,
    @Param2 DataType OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Main logic here

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH
END
```

## Best Practices
- Use SET NOCOUNT ON to reduce network traffic
- Use meaningful parameter names with @ prefix
- Include TRY...CATCH for error handling
- Return appropriate status codes
- Use OUTPUT parameters for return values
- Add header comments with author, date, description
- Consider using table-valued parameters for bulk operations
"""
        else:
            return """You are an expert PostgreSQL developer creating functions.

# PostgreSQL Function Patterns

## Standard Template
```sql
CREATE OR REPLACE FUNCTION schema.function_name(
    p_param1 data_type,
    p_param2 data_type
)
RETURNS return_type
LANGUAGE plpgsql
AS $$
DECLARE
    v_variable data_type;
BEGIN
    -- Main logic here

    RETURN result;
EXCEPTION
    WHEN OTHERS THEN
        RAISE;
END;
$$;
```

## Best Practices
- Use p_ prefix for parameters, v_ for variables
- Choose appropriate LANGUAGE (plpgsql, sql)
- Use RETURNS TABLE for set-returning functions
- Add SECURITY DEFINER if needed (with caution)
- Include COMMENT ON FUNCTION for documentation
"""

    @property
    def user_prompt_template(self) -> str:
        options = []
        if self.variables.get("include_error_handling"):
            options.append("error handling")
        if self.variables.get("include_audit_logging"):
            options.append("audit logging")
        if self.variables.get("include_transaction"):
            options.append("transaction management")

        options_str = ", ".join(options) if options else "standard implementation"

        return f"""Create a {{dialect.display_name}} stored procedure:

Description:
{{description}}

Schema Context:
{{schema_context}}

Include: {options_str}

Provide the complete procedure with:
1. Header comments
2. Parameter validation
3. Main logic
4. Error handling
5. Return values/status codes"""
