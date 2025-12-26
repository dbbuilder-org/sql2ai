"""AI-powered SQL Writer for DDL and programmable object generation."""

import json
import re
from typing import Optional, Callable, Awaitable, Any

from models import (
    ObjectType,
    GenerationRequest,
    GenerationResult,
    ColumnDefinition,
    TableDefinition,
    StoredProcedureDefinition,
    ViewDefinition,
    FunctionDefinition,
    TriggerDefinition,
    ParameterDefinition,
    CRUDGenerationRequest,
    CRUDGenerationResult,
    TransactionIsolation,
    ErrorHandlingStyle,
    FunctionType,
    TriggerType,
)
from generators import (
    TableGenerator,
    IndexGenerator,
    StoredProcedureGenerator,
    ViewGenerator,
    FunctionGenerator,
    TriggerGenerator,
    CRUDGenerator,
)


# Type for AI completion function
AICompletionFunc = Callable[[str, str], Awaitable[str]]


class SQLWriter:
    """AI-powered SQL Writer for generating DDL and programmable objects."""

    def __init__(
        self,
        ai_completion: Optional[AICompletionFunc] = None,
        default_schema: str = "dbo",
    ):
        """Initialize SQLWriter.

        Args:
            ai_completion: Async function that takes (system_prompt, user_prompt) and returns AI response
            default_schema: Default schema name for generated objects
        """
        self.ai_completion = ai_completion
        self.default_schema = default_schema

        # Initialize generators
        self.table_generator = TableGenerator()
        self.index_generator = IndexGenerator()
        self.sp_generator = StoredProcedureGenerator()
        self.view_generator = ViewGenerator()
        self.function_generator = FunctionGenerator()
        self.trigger_generator = TriggerGenerator()

    async def generate_from_prompt(
        self,
        request: GenerationRequest,
    ) -> GenerationResult:
        """Generate SQL code from natural language prompt using AI.

        Args:
            request: Generation request with prompt and parameters

        Returns:
            Generated SQL code result
        """
        if not self.ai_completion:
            raise ValueError("AI completion function not configured")

        system_prompt = self._build_system_prompt(request)
        user_prompt = self._build_user_prompt(request)

        response = await self.ai_completion(system_prompt, user_prompt)

        return self._parse_ai_response(response, request.object_type)

    def _build_system_prompt(self, request: GenerationRequest) -> str:
        """Build system prompt for AI generation."""
        prompt = """You are an expert SQL Server database developer. Generate production-ready SQL code that follows best practices.

Guidelines:
1. Use proper error handling with TRY/CATCH blocks for stored procedures
2. Include transaction management where appropriate
3. Use parameterized queries to prevent SQL injection
4. Follow naming conventions: PK_ for primary keys, FK_ for foreign keys, IX_ for indexes, usp_ for stored procedures
5. Include helpful comments
6. Generate rollback scripts when applicable
7. Consider performance implications

Security requirements:
"""
        for req in request.security_requirements:
            prompt += f"- {req}\n"

        prompt += "\nPerformance hints:\n"
        for hint in request.performance_hints:
            prompt += f"- {hint}\n"

        if request.context_schema:
            prompt += f"\nExisting schema context:\n{request.context_schema}\n"

        prompt += """
Output format:
```sql
-- Main SQL script
<your generated code here>
```

```rollback
-- Rollback script (if applicable)
<rollback code here>
```

```warnings
- Any warnings or considerations
```

```security
- Security notes
```

```performance
- Performance notes
```
"""
        return prompt

    def _build_user_prompt(self, request: GenerationRequest) -> str:
        """Build user prompt for AI generation."""
        prompt = f"Generate a {request.object_type.value}:\n\n{request.prompt}"

        if request.context_tables:
            prompt += f"\n\nRelated tables: {', '.join(request.context_tables)}"

        if request.include_error_handling:
            prompt += "\n\nInclude proper error handling."

        if request.include_audit_logging:
            prompt += "\n\nInclude audit logging for all data modifications."

        if request.include_comments:
            prompt += "\n\nInclude descriptive comments."

        return prompt

    def _parse_ai_response(
        self,
        response: str,
        object_type: ObjectType,
    ) -> GenerationResult:
        """Parse AI response into GenerationResult."""
        # Extract SQL code
        sql_match = re.search(r"```sql\n(.*?)```", response, re.DOTALL)
        sql_script = sql_match.group(1).strip() if sql_match else response

        # Extract rollback
        rollback_match = re.search(r"```rollback\n(.*?)```", response, re.DOTALL)
        rollback_script = rollback_match.group(1).strip() if rollback_match else None

        # Extract warnings
        warnings_match = re.search(r"```warnings\n(.*?)```", response, re.DOTALL)
        warnings = []
        if warnings_match:
            warnings = [w.strip("- ").strip() for w in warnings_match.group(1).strip().split("\n") if w.strip()]

        # Extract security notes
        security_match = re.search(r"```security\n(.*?)```", response, re.DOTALL)
        security_notes = []
        if security_match:
            security_notes = [s.strip("- ").strip() for s in security_match.group(1).strip().split("\n") if s.strip()]

        # Extract performance notes
        perf_match = re.search(r"```performance\n(.*?)```", response, re.DOTALL)
        performance_notes = []
        if perf_match:
            performance_notes = [p.strip("- ").strip() for p in perf_match.group(1).strip().split("\n") if p.strip()]

        # Try to extract object name from SQL
        object_name = self._extract_object_name(sql_script, object_type)

        return GenerationResult(
            object_type=object_type,
            object_name=object_name,
            sql_script=sql_script,
            rollback_script=rollback_script,
            warnings=warnings,
            security_notes=security_notes,
            performance_notes=performance_notes,
        )

    def _extract_object_name(self, sql: str, object_type: ObjectType) -> str:
        """Extract object name from SQL script."""
        patterns = {
            ObjectType.TABLE: r"CREATE\s+TABLE\s+\[?(\w+)\]?\.\[?(\w+)\]?",
            ObjectType.VIEW: r"CREATE\s+(?:OR\s+ALTER\s+)?VIEW\s+\[?(\w+)\]?\.\[?(\w+)\]?",
            ObjectType.STORED_PROCEDURE: r"CREATE\s+(?:OR\s+ALTER\s+)?PROC(?:EDURE)?\s+\[?(\w+)\]?\.\[?(\w+)\]?",
            ObjectType.FUNCTION: r"CREATE\s+(?:OR\s+ALTER\s+)?FUNCTION\s+\[?(\w+)\]?\.\[?(\w+)\]?",
            ObjectType.TRIGGER: r"CREATE\s+(?:OR\s+ALTER\s+)?TRIGGER\s+\[?(\w+)\]?\.\[?(\w+)\]?",
            ObjectType.INDEX: r"CREATE\s+(?:UNIQUE\s+)?(?:CLUSTERED\s+|NONCLUSTERED\s+)?INDEX\s+\[?(\w+)\]?",
        }

        pattern = patterns.get(object_type)
        if pattern:
            match = re.search(pattern, sql, re.IGNORECASE)
            if match:
                if object_type == ObjectType.INDEX:
                    return match.group(1)
                return f"{match.group(1)}.{match.group(2)}"

        return "unknown"

    # Direct generation methods (without AI)

    def generate_table(self, table: TableDefinition) -> GenerationResult:
        """Generate CREATE TABLE statement from definition."""
        return self.table_generator.generate(table)

    def generate_stored_procedure(
        self,
        sp: StoredProcedureDefinition,
    ) -> GenerationResult:
        """Generate stored procedure from definition."""
        return self.sp_generator.generate(sp)

    def generate_view(self, view: ViewDefinition) -> GenerationResult:
        """Generate view from definition."""
        return self.view_generator.generate(view)

    def generate_function(self, func: FunctionDefinition) -> GenerationResult:
        """Generate function from definition."""
        return self.function_generator.generate(func)

    def generate_trigger(self, trigger: TriggerDefinition) -> GenerationResult:
        """Generate trigger from definition."""
        return self.trigger_generator.generate(trigger)

    def generate_crud_procedures(
        self,
        table_columns: list[ColumnDefinition],
        request: CRUDGenerationRequest,
    ) -> CRUDGenerationResult:
        """Generate CRUD stored procedures for a table."""
        crud_gen = CRUDGenerator(table_columns)
        return crud_gen.generate(request)

    # Convenience methods for common patterns

    def generate_audit_trigger(
        self,
        table_name: str,
        audit_table_name: str,
        schema_name: str = "dbo",
        columns_to_track: Optional[list[str]] = None,
    ) -> GenerationResult:
        """Generate an audit trigger for tracking changes.

        Args:
            table_name: Source table to audit
            audit_table_name: Destination audit table
            schema_name: Schema name
            columns_to_track: Specific columns to track (None = all)

        Returns:
            Generated trigger result
        """
        cols_select = "*" if not columns_to_track else ", ".join(f"[{c}]" for c in columns_to_track)

        body = f"""-- Track inserts
IF EXISTS (SELECT 1 FROM inserted) AND NOT EXISTS (SELECT 1 FROM deleted)
BEGIN
    INSERT INTO [{schema_name}].[{audit_table_name}] (
        AuditAction,
        AuditTimestamp,
        AuditUser,
        {cols_select if cols_select != "*" else "-- All columns from source table"}
    )
    SELECT
        'INSERT',
        GETUTCDATE(),
        SYSTEM_USER,
        {cols_select}
    FROM inserted;
END

-- Track updates
IF EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
BEGIN
    INSERT INTO [{schema_name}].[{audit_table_name}] (
        AuditAction,
        AuditTimestamp,
        AuditUser,
        {cols_select if cols_select != "*" else "-- All columns from source table"}
    )
    SELECT
        'UPDATE',
        GETUTCDATE(),
        SYSTEM_USER,
        {cols_select}
    FROM inserted;
END

-- Track deletes
IF NOT EXISTS (SELECT 1 FROM inserted) AND EXISTS (SELECT 1 FROM deleted)
BEGIN
    INSERT INTO [{schema_name}].[{audit_table_name}] (
        AuditAction,
        AuditTimestamp,
        AuditUser,
        {cols_select if cols_select != "*" else "-- All columns from source table"}
    )
    SELECT
        'DELETE',
        GETUTCDATE(),
        SYSTEM_USER,
        {cols_select}
    FROM deleted;
END"""

        trigger = TriggerDefinition(
            name=f"trg_{table_name}_Audit",
            table_name=table_name,
            schema_name=schema_name,
            trigger_type=TriggerType.AFTER_INSERT,  # Will handle all DML
            body=body,
            description=f"Audit trigger for {table_name}",
        )

        # Modify to handle all DML operations
        result = self.trigger_generator.generate(trigger)
        result.sql_script = result.sql_script.replace(
            "AFTER INSERT",
            "AFTER INSERT, UPDATE, DELETE"
        )

        return result

    def generate_soft_delete_trigger(
        self,
        table_name: str,
        archive_table_name: str,
        schema_name: str = "dbo",
    ) -> GenerationResult:
        """Generate a trigger that archives deleted records instead of removing them.

        Args:
            table_name: Source table
            archive_table_name: Archive table for deleted records
            schema_name: Schema name

        Returns:
            Generated trigger result
        """
        body = f"""-- Move deleted records to archive
INSERT INTO [{schema_name}].[{archive_table_name}]
SELECT
    *,
    GETUTCDATE() AS ArchivedAt,
    SYSTEM_USER AS ArchivedBy
FROM deleted;"""

        trigger = TriggerDefinition(
            name=f"trg_{table_name}_Archive",
            table_name=table_name,
            schema_name=schema_name,
            trigger_type=TriggerType.AFTER_DELETE,
            body=body,
            description=f"Archive trigger - moves deleted {table_name} records to {archive_table_name}",
        )

        return self.trigger_generator.generate(trigger)

    def generate_validation_trigger(
        self,
        table_name: str,
        schema_name: str = "dbo",
        validations: Optional[list[tuple[str, str]]] = None,
    ) -> GenerationResult:
        """Generate a trigger with data validation rules.

        Args:
            table_name: Table to validate
            schema_name: Schema name
            validations: List of (condition, error_message) tuples

        Returns:
            Generated trigger result
        """
        validations = validations or []

        validation_checks = []
        for condition, error_msg in validations:
            validation_checks.append(f"""
IF EXISTS (SELECT 1 FROM inserted WHERE NOT ({condition}))
BEGIN
    RAISERROR('{error_msg}', 16, 1);
    ROLLBACK TRANSACTION;
    RETURN;
END""")

        body = "\n".join(validation_checks) if validation_checks else "-- Add validation logic here"

        trigger = TriggerDefinition(
            name=f"trg_{table_name}_Validate",
            table_name=table_name,
            schema_name=schema_name,
            trigger_type=TriggerType.AFTER_INSERT,
            body=body,
            description=f"Validation trigger for {table_name}",
        )

        result = self.trigger_generator.generate(trigger)
        result.sql_script = result.sql_script.replace(
            "AFTER INSERT",
            "AFTER INSERT, UPDATE"
        )

        return result


class SQLWriterTemplates:
    """Pre-built templates for common SQL patterns."""

    @staticmethod
    def funds_transfer_procedure(
        source_table: str = "Accounts",
        schema_name: str = "dbo",
    ) -> StoredProcedureDefinition:
        """Template for fund transfer with proper locking and audit."""
        return StoredProcedureDefinition(
            name="usp_TransferFunds",
            schema_name=schema_name,
            parameters=[
                ParameterDefinition("FromAccountId", "INT"),
                ParameterDefinition("ToAccountId", "INT"),
                ParameterDefinition("Amount", "DECIMAL(18, 2)"),
                ParameterDefinition("TransactionId", "UNIQUEIDENTIFIER", "OUT"),
            ],
            body=f"""SET @TransactionId = NEWID();

-- Validate accounts exist and have sufficient funds
DECLARE @FromBalance DECIMAL(18, 2);

SELECT @FromBalance = Balance
FROM [{schema_name}].[{source_table}] WITH (UPDLOCK, HOLDLOCK)
WHERE AccountId = @FromAccountId;

IF @FromBalance IS NULL
BEGIN
    RAISERROR('Source account not found', 16, 1);
    RETURN;
END

IF @FromBalance < @Amount
BEGIN
    RAISERROR('Insufficient funds', 16, 1);
    RETURN;
END

-- Perform transfer
UPDATE [{schema_name}].[{source_table}]
SET Balance = Balance - @Amount
WHERE AccountId = @FromAccountId;

UPDATE [{schema_name}].[{source_table}]
SET Balance = Balance + @Amount
WHERE AccountId = @ToAccountId;

-- Audit trail
INSERT INTO [{schema_name}].[TransactionLog] (
    TransactionId,
    FromAccountId,
    ToAccountId,
    Amount,
    TransactionDate,
    ProcessedBy
)
VALUES (
    @TransactionId,
    @FromAccountId,
    @ToAccountId,
    @Amount,
    GETUTCDATE(),
    SYSTEM_USER
);""",
            description="Transfer funds between accounts with proper locking, validation, and audit",
            isolation_level=TransactionIsolation.SERIALIZABLE,
            uses_transaction=True,
            error_handling=ErrorHandlingStyle.TRY_CATCH,
        )

    @staticmethod
    def upsert_procedure(
        table_name: str,
        key_columns: list[str],
        schema_name: str = "dbo",
    ) -> StoredProcedureDefinition:
        """Template for UPSERT (MERGE) operation."""
        key_match = " AND ".join(f"target.[{c}] = source.[{c}]" for c in key_columns)

        return StoredProcedureDefinition(
            name=f"usp_{table_name}_Upsert",
            schema_name=schema_name,
            parameters=[
                ParameterDefinition("Data", f"{table_name}Type", description="Table-valued parameter"),
            ],
            body=f"""MERGE [{schema_name}].[{table_name}] AS target
USING @Data AS source
ON ({key_match})
WHEN MATCHED THEN
    UPDATE SET
        -- Add column assignments here
        ModifiedDate = GETUTCDATE()
WHEN NOT MATCHED BY TARGET THEN
    INSERT (/* columns */)
    VALUES (/* values */);

SELECT @@ROWCOUNT AS RowsAffected;""",
            description=f"Upsert records into {table_name} using MERGE",
            uses_transaction=True,
        )

    @staticmethod
    def pagination_function(
        table_name: str,
        schema_name: str = "dbo",
        order_column: str = "Id",
    ) -> FunctionDefinition:
        """Template for pagination inline table function."""
        return FunctionDefinition(
            name=f"fn_{table_name}_Page",
            schema_name=schema_name,
            function_type=FunctionType.INLINE_TABLE,
            parameters=[
                ParameterDefinition("PageNumber", "INT"),
                ParameterDefinition("PageSize", "INT"),
            ],
            body=f"""SELECT *
FROM [{schema_name}].[{table_name}]
ORDER BY [{order_column}]
OFFSET (@PageNumber - 1) * @PageSize ROWS
FETCH NEXT @PageSize ROWS ONLY""",
            description=f"Pagination function for {table_name}",
            is_schema_bound=True,
        )
