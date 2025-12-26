"""Tests for SQL Writer module."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_writer.py', '/src'))

from models import (
    TableDefinition,
    ColumnDefinition,
    DataType,
    ConstraintType,
    StoredProcedureDefinition,
    ViewDefinition,
    FunctionDefinition,
    TriggerDefinition,
    TriggerEvent,
)
from generators import (
    TableGenerator,
    StoredProcedureGenerator,
    ViewGenerator,
    FunctionGenerator,
    TriggerGenerator,
    CRUDGenerator,
)
from writer import SQLWriter


class TestColumnDefinition:
    """Test ColumnDefinition model."""

    def test_create_column(self):
        col = ColumnDefinition(
            name="email",
            data_type=DataType.NVARCHAR,
            length=255,
            nullable=False,
            is_primary_key=False,
        )
        assert col.name == "email"
        assert col.data_type == DataType.NVARCHAR
        assert col.length == 255

    def test_column_with_default(self):
        col = ColumnDefinition(
            name="created_at",
            data_type=DataType.DATETIME2,
            nullable=False,
            default_value="GETUTCDATE()",
        )
        assert col.default_value == "GETUTCDATE()"


class TestTableDefinition:
    """Test TableDefinition model."""

    def test_create_table_definition(self):
        table = TableDefinition(
            schema_name="dbo",
            table_name="Users",
            columns=[
                ColumnDefinition(
                    name="Id",
                    data_type=DataType.INT,
                    nullable=False,
                    is_primary_key=True,
                    is_identity=True,
                ),
                ColumnDefinition(
                    name="Email",
                    data_type=DataType.NVARCHAR,
                    length=255,
                    nullable=False,
                ),
            ],
        )
        assert table.table_name == "Users"
        assert len(table.columns) == 2


class TestTableGenerator:
    """Test TableGenerator."""

    def test_generate_simple_table(self):
        generator = TableGenerator()

        table = TableDefinition(
            schema_name="dbo",
            table_name="Products",
            columns=[
                ColumnDefinition(
                    name="Id",
                    data_type=DataType.INT,
                    nullable=False,
                    is_primary_key=True,
                    is_identity=True,
                ),
                ColumnDefinition(
                    name="Name",
                    data_type=DataType.NVARCHAR,
                    length=100,
                    nullable=False,
                ),
                ColumnDefinition(
                    name="Price",
                    data_type=DataType.DECIMAL,
                    precision=18,
                    scale=2,
                    nullable=False,
                ),
            ],
        )

        sql = generator.generate(table)
        assert "CREATE TABLE [dbo].[Products]" in sql
        assert "[Id] INT" in sql
        assert "IDENTITY" in sql
        assert "[Name] NVARCHAR(100)" in sql
        assert "[Price] DECIMAL(18,2)" in sql

    def test_generate_table_with_constraints(self):
        generator = TableGenerator()

        table = TableDefinition(
            schema_name="dbo",
            table_name="Orders",
            columns=[
                ColumnDefinition(
                    name="Id",
                    data_type=DataType.INT,
                    nullable=False,
                    is_primary_key=True,
                ),
                ColumnDefinition(
                    name="CustomerId",
                    data_type=DataType.INT,
                    nullable=False,
                    foreign_key_table="Customers",
                    foreign_key_column="Id",
                ),
            ],
        )

        sql = generator.generate(table)
        assert "FOREIGN KEY" in sql or "REFERENCES" in sql


class TestStoredProcedureGenerator:
    """Test StoredProcedureGenerator."""

    def test_generate_simple_procedure(self):
        generator = StoredProcedureGenerator()

        sp = StoredProcedureDefinition(
            schema_name="dbo",
            procedure_name="GetCustomers",
            parameters=[],
            body="SELECT * FROM Customers WHERE IsActive = 1",
        )

        sql = generator.generate(sp)
        assert "CREATE PROCEDURE [dbo].[GetCustomers]" in sql
        assert "SELECT * FROM Customers" in sql

    def test_generate_procedure_with_parameters(self):
        generator = StoredProcedureGenerator()

        sp = StoredProcedureDefinition(
            schema_name="dbo",
            procedure_name="GetCustomerById",
            parameters=[
                {"name": "@CustomerId", "type": "INT", "direction": "IN"},
            ],
            body="SELECT * FROM Customers WHERE Id = @CustomerId",
        )

        sql = generator.generate(sp)
        assert "@CustomerId INT" in sql

    def test_generate_procedure_with_error_handling(self):
        generator = StoredProcedureGenerator(include_error_handling=True)

        sp = StoredProcedureDefinition(
            schema_name="dbo",
            procedure_name="InsertCustomer",
            parameters=[
                {"name": "@Email", "type": "NVARCHAR(255)", "direction": "IN"},
            ],
            body="INSERT INTO Customers (Email) VALUES (@Email)",
        )

        sql = generator.generate(sp)
        assert "BEGIN TRY" in sql
        assert "BEGIN CATCH" in sql
        assert "THROW" in sql or "RAISERROR" in sql


class TestViewGenerator:
    """Test ViewGenerator."""

    def test_generate_simple_view(self):
        generator = ViewGenerator()

        view = ViewDefinition(
            schema_name="dbo",
            view_name="vw_ActiveCustomers",
            select_statement="SELECT Id, Email, Name FROM Customers WHERE IsActive = 1",
        )

        sql = generator.generate(view)
        assert "CREATE VIEW [dbo].[vw_ActiveCustomers]" in sql
        assert "SELECT Id, Email, Name FROM Customers" in sql

    def test_generate_view_with_schemabinding(self):
        generator = ViewGenerator(with_schemabinding=True)

        view = ViewDefinition(
            schema_name="dbo",
            view_name="vw_CustomerCount",
            select_statement="SELECT COUNT(*) AS CustomerCount FROM dbo.Customers",
        )

        sql = generator.generate(view)
        assert "WITH SCHEMABINDING" in sql


class TestFunctionGenerator:
    """Test FunctionGenerator."""

    def test_generate_scalar_function(self):
        generator = FunctionGenerator()

        func = FunctionDefinition(
            schema_name="dbo",
            function_name="fn_GetAge",
            parameters=[
                {"name": "@BirthDate", "type": "DATE"},
            ],
            return_type="INT",
            body="RETURN DATEDIFF(YEAR, @BirthDate, GETDATE())",
            is_deterministic=True,
        )

        sql = generator.generate(func)
        assert "CREATE FUNCTION [dbo].[fn_GetAge]" in sql
        assert "RETURNS INT" in sql
        assert "DATEDIFF" in sql

    def test_generate_table_valued_function(self):
        generator = FunctionGenerator()

        func = FunctionDefinition(
            schema_name="dbo",
            function_name="fn_GetCustomerOrders",
            parameters=[
                {"name": "@CustomerId", "type": "INT"},
            ],
            return_type="TABLE",
            body="RETURN SELECT * FROM Orders WHERE CustomerId = @CustomerId",
            is_table_valued=True,
        )

        sql = generator.generate(func)
        assert "RETURNS TABLE" in sql or "RETURNS @" in sql


class TestTriggerGenerator:
    """Test TriggerGenerator."""

    def test_generate_insert_trigger(self):
        generator = TriggerGenerator()

        trigger = TriggerDefinition(
            schema_name="dbo",
            trigger_name="trg_Customers_Insert",
            table_name="Customers",
            events=[TriggerEvent.INSERT],
            body="INSERT INTO AuditLog (TableName, Action) VALUES ('Customers', 'INSERT')",
        )

        sql = generator.generate(trigger)
        assert "CREATE TRIGGER [dbo].[trg_Customers_Insert]" in sql
        assert "AFTER INSERT" in sql or "FOR INSERT" in sql

    def test_generate_update_trigger(self):
        generator = TriggerGenerator()

        trigger = TriggerDefinition(
            schema_name="dbo",
            trigger_name="trg_Customers_Update",
            table_name="Customers",
            events=[TriggerEvent.UPDATE],
            body="INSERT INTO AuditLog (TableName, Action) VALUES ('Customers', 'UPDATE')",
        )

        sql = generator.generate(trigger)
        assert "AFTER UPDATE" in sql or "FOR UPDATE" in sql


class TestCRUDGenerator:
    """Test CRUDGenerator."""

    def test_generate_crud_procedures(self):
        generator = CRUDGenerator()

        table = TableDefinition(
            schema_name="dbo",
            table_name="Products",
            columns=[
                ColumnDefinition(
                    name="Id",
                    data_type=DataType.INT,
                    nullable=False,
                    is_primary_key=True,
                    is_identity=True,
                ),
                ColumnDefinition(
                    name="Name",
                    data_type=DataType.NVARCHAR,
                    length=100,
                    nullable=False,
                ),
                ColumnDefinition(
                    name="Price",
                    data_type=DataType.DECIMAL,
                    precision=18,
                    scale=2,
                    nullable=False,
                ),
            ],
        )

        crud = generator.generate(table)

        assert "sp_Products_Create" in crud or "Products_Insert" in crud
        assert "sp_Products_Read" in crud or "Products_GetById" in crud
        assert "sp_Products_Update" in crud or "Products_Update" in crud
        assert "sp_Products_Delete" in crud or "Products_Delete" in crud


class TestSQLWriter:
    """Test SQLWriter main class."""

    def test_generate_table_from_description(self):
        writer = SQLWriter()

        with patch.object(writer, '_call_ai') as mock_ai:
            mock_ai.return_value = """
            CREATE TABLE [dbo].[Users] (
                [Id] INT IDENTITY(1,1) PRIMARY KEY,
                [Email] NVARCHAR(255) NOT NULL,
                [CreatedAt] DATETIME2 NOT NULL DEFAULT GETUTCDATE()
            )
            """

            sql = writer.generate_from_prompt(
                "Create a users table with id, email, and created timestamp"
            )

            assert "CREATE TABLE" in sql
            assert "Users" in sql

    def test_generate_procedure_from_description(self):
        writer = SQLWriter()

        with patch.object(writer, '_call_ai') as mock_ai:
            mock_ai.return_value = """
            CREATE PROCEDURE [dbo].[sp_TransferFunds]
                @FromAccountId INT,
                @ToAccountId INT,
                @Amount DECIMAL(18,2)
            AS
            BEGIN
                SET NOCOUNT ON;
                BEGIN TRY
                    BEGIN TRANSACTION;
                    UPDATE Accounts SET Balance = Balance - @Amount WHERE Id = @FromAccountId;
                    UPDATE Accounts SET Balance = Balance + @Amount WHERE Id = @ToAccountId;
                    COMMIT TRANSACTION;
                END TRY
                BEGIN CATCH
                    ROLLBACK TRANSACTION;
                    THROW;
                END CATCH
            END
            """

            sql = writer.generate_from_prompt(
                "Create a stored procedure to transfer funds between accounts with proper transaction handling"
            )

            assert "CREATE PROCEDURE" in sql
            assert "BEGIN TRY" in sql
            assert "TRANSACTION" in sql

    def test_validate_generated_sql(self):
        writer = SQLWriter()

        valid_sql = "CREATE TABLE Test (Id INT PRIMARY KEY)"
        assert writer.validate_syntax(valid_sql) is True

        # Should detect basic issues
        invalid_sql = "CREATE TABEL Test (Id INT)"  # typo
        assert writer.validate_syntax(invalid_sql) is False
