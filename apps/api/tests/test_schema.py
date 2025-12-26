"""Tests for schema service and endpoints."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from fastapi import HTTPException
from fastapi.testclient import TestClient


class TestSchemaModels:
    """Tests for schema data models."""

    def test_column_info(self):
        """Test ColumnInfo model."""
        # Import here to test the import works
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from models import ColumnInfo, DataType

        col = ColumnInfo(
            name="CustomerId",
            data_type="int",
            data_type_normalized=DataType.INT,
            is_nullable=False,
            is_identity=True,
            is_primary_key=True,
            ordinal_position=1,
        )

        assert col.name == "CustomerId"
        assert col.data_type_normalized == DataType.INT
        assert col.is_primary_key is True

    def test_table_info(self):
        """Test TableInfo model."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from models import TableInfo, ColumnInfo, DataType

        table = TableInfo(
            name="Customers",
            schema="dbo",
            columns=[
                ColumnInfo(
                    name="Id",
                    data_type="int",
                    data_type_normalized=DataType.INT,
                    is_primary_key=True,
                    ordinal_position=1,
                ),
                ColumnInfo(
                    name="Email",
                    data_type="nvarchar",
                    data_type_normalized=DataType.NVARCHAR,
                    ordinal_position=2,
                ),
            ],
            primary_key_columns=["Id"],
        )

        assert table.full_name == "dbo.Customers"
        assert len(table.columns) == 2
        assert table.get_column("Id") is not None
        assert table.get_column("NonExistent") is None

    def test_database_schema(self):
        """Test DatabaseSchema model."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from models import DatabaseSchema, TableInfo

        schema = DatabaseSchema(
            database_name="TestDB",
            server_name="localhost",
            tables=[
                TableInfo(name="Users", schema="dbo"),
                TableInfo(name="Orders", schema="dbo"),
            ],
        )

        assert schema.database_name == "TestDB"
        assert schema.table_count == 2
        assert schema.get_table("Users", "dbo") is not None

    def test_schema_to_dict(self):
        """Test schema serialization to dict."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from models import DatabaseSchema, TableInfo, ColumnInfo, DataType

        schema = DatabaseSchema(
            database_name="TestDB",
            tables=[
                TableInfo(
                    name="Test",
                    schema="dbo",
                    columns=[
                        ColumnInfo(
                            name="Id",
                            data_type="int",
                            data_type_normalized=DataType.INT,
                            ordinal_position=1,
                        )
                    ],
                )
            ],
        )

        result = schema.to_dict()

        assert result["database_name"] == "TestDB"
        assert len(result["tables"]) == 1
        assert result["summary"]["table_count"] == 1


class TestSchemaAnalyzer:
    """Tests for schema analyzer."""

    def test_pii_detection(self):
        """Test PII column detection."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from analyzer import SchemaAnalyzer
        from models import ColumnInfo, DataType

        analyzer = SchemaAnalyzer()

        # Test various PII patterns
        email_col = ColumnInfo(
            name="EmailAddress",
            data_type="nvarchar",
            data_type_normalized=DataType.NVARCHAR,
            ordinal_position=1,
        )
        assert analyzer._detect_pii(email_col) == "email"

        phone_col = ColumnInfo(
            name="PhoneNumber",
            data_type="varchar",
            data_type_normalized=DataType.VARCHAR,
            ordinal_position=2,
        )
        assert analyzer._detect_pii(phone_col) == "phone"

        ssn_col = ColumnInfo(
            name="SSN",
            data_type="char",
            data_type_normalized=DataType.CHAR,
            ordinal_position=3,
        )
        assert analyzer._detect_pii(ssn_col) == "ssn"

        # Non-PII column
        id_col = ColumnInfo(
            name="CustomerId",
            data_type="int",
            data_type_normalized=DataType.INT,
            ordinal_position=4,
        )
        assert analyzer._detect_pii(id_col) is None

    def test_infer_table_purpose(self):
        """Test table purpose inference."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from analyzer import SchemaAnalyzer
        from models import TableInfo

        analyzer = SchemaAnalyzer()

        # Audit table
        audit_table = TableInfo(name="AuditLog", schema="dbo")
        purpose = analyzer._infer_table_purpose(audit_table)
        assert "audit" in purpose.lower() or "log" in purpose.lower()

        # User table
        user_table = TableInfo(name="Users", schema="dbo")
        purpose = analyzer._infer_table_purpose(user_table)
        assert "user" in purpose.lower()

    def test_naming_convention_check(self):
        """Test naming convention validation."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from analyzer import SchemaAnalyzer

        analyzer = SchemaAnalyzer(preferred_convention="pascal_case")

        assert analyzer._matches_convention("CustomerName") is True
        assert analyzer._matches_convention("customer_name") is False

        analyzer_snake = SchemaAnalyzer(preferred_convention="snake_case")
        assert analyzer_snake._matches_convention("customer_name") is True
        assert analyzer_snake._matches_convention("CustomerName") is False


class TestSchemaDiffer:
    """Tests for schema differ."""

    def test_compare_tables_added(self):
        """Test detecting added tables."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from differ import SchemaDiffer
        from models import DatabaseSchema, TableInfo

        source = DatabaseSchema(
            database_name="DB",
            tables=[TableInfo(name="Users", schema="dbo")],
        )

        target = DatabaseSchema(
            database_name="DB",
            tables=[
                TableInfo(name="Users", schema="dbo"),
                TableInfo(name="Orders", schema="dbo"),
            ],
        )

        differ = SchemaDiffer()
        diff = differ.compare(source, target)

        assert diff.tables_added == 1
        assert any(
            d.object_name == "dbo.Orders" and d.change_type == "added"
            for d in diff.differences
        )

    def test_compare_tables_removed(self):
        """Test detecting removed tables."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from differ import SchemaDiffer
        from models import DatabaseSchema, TableInfo

        source = DatabaseSchema(
            database_name="DB",
            tables=[
                TableInfo(name="Users", schema="dbo"),
                TableInfo(name="OldTable", schema="dbo"),
            ],
        )

        target = DatabaseSchema(
            database_name="DB",
            tables=[TableInfo(name="Users", schema="dbo")],
        )

        differ = SchemaDiffer()
        diff = differ.compare(source, target)

        assert diff.tables_removed == 1
        removed = next(
            d for d in diff.differences
            if d.object_name == "dbo.OldTable"
        )
        assert removed.change_type == "removed"
        assert removed.breaking_change is True

    def test_compare_columns_modified(self):
        """Test detecting column modifications."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from differ import SchemaDiffer
        from models import DatabaseSchema, TableInfo, ColumnInfo, DataType

        source = DatabaseSchema(
            database_name="DB",
            tables=[
                TableInfo(
                    name="Users",
                    schema="dbo",
                    columns=[
                        ColumnInfo(
                            name="Name",
                            data_type="varchar(50)",
                            data_type_normalized=DataType.VARCHAR,
                            max_length=50,
                            is_nullable=True,
                            ordinal_position=1,
                        )
                    ],
                )
            ],
        )

        target = DatabaseSchema(
            database_name="DB",
            tables=[
                TableInfo(
                    name="Users",
                    schema="dbo",
                    columns=[
                        ColumnInfo(
                            name="Name",
                            data_type="varchar(100)",
                            data_type_normalized=DataType.VARCHAR,
                            max_length=100,  # Changed
                            is_nullable=False,  # Changed
                            ordinal_position=1,
                        )
                    ],
                )
            ],
        )

        differ = SchemaDiffer()
        diff = differ.compare(source, target)

        assert diff.columns_modified == 1
        modified = next(
            d for d in diff.differences
            if d.object_type == "column" and d.change_type == "modified"
        )
        assert "max_length" in modified.details or "is_nullable" in modified.details

    def test_breaking_change_detection(self):
        """Test breaking change detection."""
        import sys
        sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/schema-engine/src")

        from differ import SchemaDiffer
        from models import DatabaseSchema, TableInfo, ColumnInfo, DataType

        source = DatabaseSchema(
            database_name="DB",
            tables=[
                TableInfo(
                    name="Users",
                    schema="dbo",
                    columns=[
                        ColumnInfo(
                            name="Email",
                            data_type="varchar",
                            data_type_normalized=DataType.VARCHAR,
                            ordinal_position=1,
                        )
                    ],
                )
            ],
        )

        # Remove a column - breaking change
        target = DatabaseSchema(
            database_name="DB",
            tables=[TableInfo(name="Users", schema="dbo", columns=[])],
        )

        differ = SchemaDiffer()
        diff = differ.compare(source, target)

        assert diff.has_breaking_changes is True


class TestSchemaEndpoints:
    """Tests for schema API endpoints."""

    @pytest.fixture
    def mock_user(self):
        """Create mock authenticated user."""
        from sql2ai_api.dependencies.auth import AuthenticatedUser, UserRole, Permission

        return AuthenticatedUser(
            id="user_123",
            tenant_id="tenant_456",
            role=UserRole.ADMIN,
            permissions=[Permission.SCHEMA_READ, Permission.SCHEMA_EXPORT],
        )

    def test_extract_schema_unauthorized(self, client: TestClient):
        """Test schema extraction without auth returns 401."""
        response = client.post("/api/schemas/conn_123/extract", json={})
        assert response.status_code == 401

    def test_list_snapshots_unauthorized(self, client: TestClient):
        """Test listing snapshots without auth returns 401."""
        response = client.get("/api/schemas/")
        assert response.status_code == 401
