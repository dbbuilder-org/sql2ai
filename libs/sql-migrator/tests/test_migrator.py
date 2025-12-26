"""Tests for SQL Migrator module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_migrator.py', '/src'))

from models import (
    Migration,
    MigrationStep,
    MigrationStatus,
    StepType,
    BreakingChange,
    BreakingChangeSeverity,
)
from generator import MigrationGenerator
from codegen import DapperCodeGenerator, TypeScriptCodeGenerator, ZodCodeGenerator
from executor import MigrationExecutor


class TestMigration:
    """Test Migration model."""

    def test_create_migration(self):
        migration = Migration(
            id="mig_001",
            name="Add users table",
            description="Create users table with basic columns",
            steps=[],
            created_at=datetime.utcnow(),
        )
        assert migration.id == "mig_001"
        assert migration.status == MigrationStatus.PENDING

    def test_migration_with_steps(self):
        steps = [
            MigrationStep(
                order=1,
                step_type=StepType.CREATE_TABLE,
                object_name="users",
                sql="CREATE TABLE users (id INT PRIMARY KEY)",
            ),
            MigrationStep(
                order=2,
                step_type=StepType.CREATE_INDEX,
                object_name="idx_users_email",
                sql="CREATE INDEX idx_users_email ON users(email)",
            ),
        ]
        migration = Migration(
            id="mig_002",
            name="Create users with index",
            steps=steps,
        )
        assert len(migration.steps) == 2
        assert migration.steps[0].order == 1


class TestMigrationStep:
    """Test MigrationStep model."""

    def test_create_step(self):
        step = MigrationStep(
            order=1,
            step_type=StepType.ALTER_TABLE,
            object_name="users",
            sql="ALTER TABLE users ADD COLUMN age INT",
            rollback_sql="ALTER TABLE users DROP COLUMN age",
        )
        assert step.step_type == StepType.ALTER_TABLE
        assert step.rollback_sql is not None


class TestBreakingChange:
    """Test BreakingChange model."""

    def test_breaking_change_detection(self):
        change = BreakingChange(
            severity=BreakingChangeSeverity.HIGH,
            object_type="COLUMN",
            object_name="users.email",
            change_type="DROP",
            description="Dropping email column will break dependent views",
            affected_objects=["vw_user_emails", "sp_get_user_by_email"],
        )
        assert change.severity == BreakingChangeSeverity.HIGH
        assert len(change.affected_objects) == 2


class TestMigrationGenerator:
    """Test MigrationGenerator."""

    def test_generate_create_table_migration(self):
        generator = MigrationGenerator()

        old_schema = {"tables": {}}
        new_schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False, "is_primary_key": True},
                        {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
                        {"name": "created_at", "type": "DATETIME2", "nullable": False},
                    ]
                }
            }
        }

        migration = generator.generate(old_schema, new_schema, "Add users table")
        assert migration is not None
        assert len(migration.steps) > 0
        assert any(step.step_type == StepType.CREATE_TABLE for step in migration.steps)

    def test_generate_add_column_migration(self):
        generator = MigrationGenerator()

        old_schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False},
                    ]
                }
            }
        }
        new_schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False},
                        {"name": "email", "type": "NVARCHAR(255)", "nullable": True},
                    ]
                }
            }
        }

        migration = generator.generate(old_schema, new_schema, "Add email column")
        assert migration is not None
        assert any(step.step_type == StepType.ALTER_TABLE for step in migration.steps)

    def test_detect_breaking_changes(self):
        generator = MigrationGenerator()

        old_schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False},
                        {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
                    ]
                }
            }
        }
        new_schema = {
            "tables": {
                "users": {
                    "columns": [
                        {"name": "id", "type": "INT", "nullable": False},
                        # email column removed - breaking change
                    ]
                }
            }
        }

        migration = generator.generate(old_schema, new_schema, "Remove email")
        assert len(migration.breaking_changes) > 0


class TestDapperCodeGenerator:
    """Test Dapper C# code generation."""

    def test_generate_model(self):
        generator = DapperCodeGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "Id", "type": "INT", "nullable": False, "is_primary_key": True},
                {"name": "Email", "type": "NVARCHAR(255)", "nullable": False},
                {"name": "CreatedAt", "type": "DATETIME2", "nullable": False},
                {"name": "DeletedAt", "type": "DATETIME2", "nullable": True},
            ]
        }

        code = generator.generate_model(table_schema)
        assert "public class User" in code
        assert "public int Id { get; set; }" in code
        assert "public string Email { get; set; }" in code
        assert "public DateTime? DeletedAt { get; set; }" in code

    def test_generate_repository(self):
        generator = DapperCodeGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "Id", "type": "INT", "nullable": False, "is_primary_key": True},
                {"name": "Email", "type": "NVARCHAR(255)", "nullable": False},
            ]
        }

        code = generator.generate_repository(table_schema)
        assert "public class UserRepository" in code
        assert "GetByIdAsync" in code
        assert "InsertAsync" in code
        assert "UpdateAsync" in code
        assert "DeleteAsync" in code


class TestTypeScriptCodeGenerator:
    """Test TypeScript code generation."""

    def test_generate_interface(self):
        generator = TypeScriptCodeGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "id", "type": "INT", "nullable": False},
                {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
                {"name": "age", "type": "INT", "nullable": True},
                {"name": "is_active", "type": "BIT", "nullable": False},
            ]
        }

        code = generator.generate_interface(table_schema)
        assert "export interface User {" in code
        assert "id: number;" in code
        assert "email: string;" in code
        assert "age: number | null;" in code or "age?: number;" in code
        assert "isActive: boolean;" in code or "is_active: boolean;" in code

    def test_generate_api_types(self):
        generator = TypeScriptCodeGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "id", "type": "INT", "nullable": False, "is_primary_key": True},
                {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
            ]
        }

        code = generator.generate_api_types(table_schema)
        assert "CreateUserRequest" in code or "UserCreate" in code
        assert "UpdateUserRequest" in code or "UserUpdate" in code


class TestZodCodeGenerator:
    """Test Zod schema generation."""

    def test_generate_schema(self):
        generator = ZodCodeGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "id", "type": "INT", "nullable": False},
                {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
                {"name": "age", "type": "INT", "nullable": True},
            ]
        }

        code = generator.generate_schema(table_schema)
        assert "z.object" in code
        assert "z.number()" in code
        assert "z.string()" in code
        assert ".nullable()" in code or ".optional()" in code


class TestMigrationExecutor:
    """Test MigrationExecutor."""

    @pytest.mark.asyncio
    async def test_execute_migration(self):
        executor = MigrationExecutor()
        connection = MagicMock()
        connection.execute = MagicMock(return_value=None)
        connection.begin_transaction = MagicMock()
        connection.commit = MagicMock()
        connection.rollback = MagicMock()

        migration = Migration(
            id="mig_001",
            name="Test migration",
            steps=[
                MigrationStep(
                    order=1,
                    step_type=StepType.CREATE_TABLE,
                    object_name="test_table",
                    sql="CREATE TABLE test_table (id INT)",
                ),
            ],
        )

        result = await executor.execute(migration, connection)
        assert result.status == MigrationStatus.COMPLETED
        connection.execute.assert_called()

    @pytest.mark.asyncio
    async def test_rollback_migration(self):
        executor = MigrationExecutor()
        connection = MagicMock()
        connection.execute = MagicMock(return_value=None)

        migration = Migration(
            id="mig_001",
            name="Test migration",
            status=MigrationStatus.COMPLETED,
            steps=[
                MigrationStep(
                    order=1,
                    step_type=StepType.CREATE_TABLE,
                    object_name="test_table",
                    sql="CREATE TABLE test_table (id INT)",
                    rollback_sql="DROP TABLE test_table",
                ),
            ],
        )

        result = await executor.rollback(migration, connection)
        assert result.status == MigrationStatus.ROLLED_BACK

    def test_dry_run(self):
        executor = MigrationExecutor()

        migration = Migration(
            id="mig_001",
            name="Test migration",
            steps=[
                MigrationStep(
                    order=1,
                    step_type=StepType.CREATE_TABLE,
                    object_name="test_table",
                    sql="CREATE TABLE test_table (id INT)",
                ),
            ],
        )

        script = executor.generate_script(migration)
        assert "CREATE TABLE test_table" in script
        assert "-- Migration: mig_001" in script or "mig_001" in script
