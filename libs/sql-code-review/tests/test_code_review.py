"""Tests for SQL Code Review module."""

import pytest
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_code_review.py', '/src'))

from models import (
    ReviewIssue,
    IssueSeverity,
    IssueCategory,
    ReviewResult,
    ReleaseNote,
    ReleaseNoteType,
    DataDictionaryEntry,
    ColumnDocumentation,
)
from analyzer import (
    SecurityAnalyzer,
    PerformanceAnalyzer,
    StyleAnalyzer,
    BestPracticeAnalyzer,
    SQLCodeReviewer,
)
from release_notes import ReleaseNotesGenerator
from data_dictionary import DataDictionaryGenerator


class TestReviewIssue:
    """Test ReviewIssue model."""

    def test_create_issue(self):
        issue = ReviewIssue(
            rule_id="SEC001",
            category=IssueCategory.SECURITY,
            severity=IssueSeverity.CRITICAL,
            message="Potential SQL injection vulnerability",
            line_number=15,
            code_snippet="EXEC('SELECT * FROM Users WHERE Id = ' + @Id)",
            suggestion="Use parameterized queries instead",
        )
        assert issue.rule_id == "SEC001"
        assert issue.severity == IssueSeverity.CRITICAL


class TestSecurityAnalyzer:
    """Test SecurityAnalyzer."""

    def test_detect_sql_injection(self):
        analyzer = SecurityAnalyzer()
        code = """
        CREATE PROCEDURE GetUser @Id VARCHAR(10)
        AS
        BEGIN
            EXEC('SELECT * FROM Users WHERE Id = ' + @Id)
        END
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "SEC001" for i in issues)
        assert any("injection" in i.message.lower() for i in issues)

    def test_detect_xp_cmdshell(self):
        analyzer = SecurityAnalyzer()
        code = """
        EXEC xp_cmdshell 'dir C:\\'
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "SEC002" for i in issues)
        assert any("xp_cmdshell" in i.message.lower() for i in issues)

    def test_detect_hardcoded_credentials(self):
        analyzer = SecurityAnalyzer()
        code = """
        DECLARE @Password NVARCHAR(50) = 'mysecretpassword123'
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "SEC003" for i in issues)

    def test_no_issues_for_clean_code(self):
        analyzer = SecurityAnalyzer()
        code = """
        CREATE PROCEDURE GetUser @Id INT
        AS
        BEGIN
            SELECT * FROM Users WHERE Id = @Id
        END
        """

        issues = analyzer.analyze(code)
        # Should have no critical security issues
        assert not any(i.severity == IssueSeverity.CRITICAL for i in issues)


class TestPerformanceAnalyzer:
    """Test PerformanceAnalyzer."""

    def test_detect_select_star(self):
        analyzer = PerformanceAnalyzer()
        code = "SELECT * FROM Users"

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "PERF001" for i in issues)
        assert any("SELECT *" in i.message for i in issues)

    def test_detect_cursor_usage(self):
        analyzer = PerformanceAnalyzer()
        code = """
        DECLARE cur CURSOR FOR SELECT Id FROM Users
        OPEN cur
        FETCH NEXT FROM cur
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "PERF002" for i in issues)
        assert any("cursor" in i.message.lower() for i in issues)

    def test_detect_nolock_hint(self):
        analyzer = PerformanceAnalyzer()
        code = "SELECT * FROM Users WITH (NOLOCK)"

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "PERF003" for i in issues)

    def test_detect_scalar_udf_in_select(self):
        analyzer = PerformanceAnalyzer()
        code = "SELECT dbo.fn_GetFullName(FirstName, LastName) FROM Users"

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "PERF004" for i in issues)


class TestStyleAnalyzer:
    """Test StyleAnalyzer."""

    def test_detect_naming_convention_violation(self):
        analyzer = StyleAnalyzer()
        code = """
        CREATE TABLE tblUsers (
            user_id INT
        )
        """

        issues = analyzer.analyze(code)
        # Should detect Hungarian notation or inconsistent naming
        assert any(i.category == IssueCategory.STYLE for i in issues)

    def test_detect_deprecated_syntax(self):
        analyzer = StyleAnalyzer()
        code = "SELECT * FROM Users, Orders WHERE Users.Id = Orders.UserId"

        issues = analyzer.analyze(code)
        # Should detect old-style join
        assert any("join" in i.message.lower() for i in issues)


class TestBestPracticeAnalyzer:
    """Test BestPracticeAnalyzer."""

    def test_detect_missing_set_nocount(self):
        analyzer = BestPracticeAnalyzer()
        code = """
        CREATE PROCEDURE GetUsers
        AS
        BEGIN
            SELECT * FROM Users
        END
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "BP001" for i in issues)
        assert any("SET NOCOUNT ON" in i.message for i in issues)

    def test_detect_identity_usage(self):
        analyzer = BestPracticeAnalyzer()
        code = """
        INSERT INTO Users (Email) VALUES ('test@example.com')
        SELECT @@IDENTITY
        """

        issues = analyzer.analyze(code)
        assert any(i.rule_id == "BP002" for i in issues)
        assert any("SCOPE_IDENTITY" in i.suggestion for i in issues)


class TestSQLCodeReviewer:
    """Test SQLCodeReviewer main class."""

    def test_full_review(self):
        reviewer = SQLCodeReviewer()
        code = """
        CREATE PROCEDURE GetUserData @UserId VARCHAR(50)
        AS
        BEGIN
            SELECT * FROM Users WHERE Id = @UserId
        END
        """

        result = reviewer.review(code)
        assert isinstance(result, ReviewResult)
        assert result.total_issues >= 0

    def test_review_with_severity_filter(self):
        reviewer = SQLCodeReviewer()
        code = """
        EXEC('SELECT * FROM Users WHERE Id = ' + @Id)
        """

        result = reviewer.review(code, min_severity=IssueSeverity.WARNING)
        critical_issues = [i for i in result.issues if i.severity == IssueSeverity.CRITICAL]
        assert len(critical_issues) > 0


class TestReleaseNotesGenerator:
    """Test ReleaseNotesGenerator."""

    def test_generate_release_notes(self):
        generator = ReleaseNotesGenerator()

        changes = [
            {
                "type": "CREATE",
                "object_type": "TABLE",
                "object_name": "dbo.Orders",
            },
            {
                "type": "ALTER",
                "object_type": "PROCEDURE",
                "object_name": "dbo.GetCustomers",
                "description": "Added pagination support",
            },
            {
                "type": "DROP",
                "object_type": "VIEW",
                "object_name": "dbo.vw_OldReport",
            },
        ]

        notes = generator.generate(changes, version="1.2.0")

        assert "1.2.0" in notes.version
        assert any(n.note_type == ReleaseNoteType.FEATURE for n in notes.entries)
        assert any(n.note_type == ReleaseNoteType.BREAKING for n in notes.entries)

    def test_categorize_changes(self):
        generator = ReleaseNotesGenerator()

        changes = [
            {"type": "CREATE", "object_type": "INDEX", "object_name": "idx_email"},
            {"type": "ALTER", "object_type": "TABLE", "object_name": "Users", "description": "Fixed column type"},
        ]

        notes = generator.generate(changes, version="1.0.1")
        assert any(n.note_type == ReleaseNoteType.FIX for n in notes.entries) or \
               any(n.note_type == ReleaseNoteType.IMPROVEMENT for n in notes.entries)


class TestDataDictionaryGenerator:
    """Test DataDictionaryGenerator."""

    def test_generate_table_documentation(self):
        generator = DataDictionaryGenerator()

        table_schema = {
            "name": "Customers",
            "columns": [
                {"name": "Id", "type": "INT", "nullable": False, "is_primary_key": True},
                {"name": "Email", "type": "NVARCHAR(255)", "nullable": False},
                {"name": "CreatedAt", "type": "DATETIME2", "nullable": False},
            ],
        }

        with patch.object(generator, '_generate_ai_description') as mock_ai:
            mock_ai.side_effect = [
                "Primary customer identifier",
                "Customer's email address for communications",
                "Timestamp when customer record was created",
            ]

            entry = generator.generate_for_table(table_schema)

            assert isinstance(entry, DataDictionaryEntry)
            assert entry.table_name == "Customers"
            assert len(entry.columns) == 3
            assert all(isinstance(c, ColumnDocumentation) for c in entry.columns)

    def test_generate_openapi_schema(self):
        generator = DataDictionaryGenerator()

        table_schema = {
            "name": "Products",
            "columns": [
                {"name": "id", "type": "INT", "nullable": False},
                {"name": "name", "type": "NVARCHAR(100)", "nullable": False},
                {"name": "price", "type": "DECIMAL(18,2)", "nullable": False},
                {"name": "description", "type": "NVARCHAR(MAX)", "nullable": True},
            ],
        }

        openapi = generator.to_openapi_schema(table_schema)

        assert "Product" in openapi
        assert "properties" in openapi["Product"]
        assert "id" in openapi["Product"]["properties"]
        assert openapi["Product"]["properties"]["price"]["type"] == "number"

    def test_detect_pii_columns(self):
        generator = DataDictionaryGenerator()

        table_schema = {
            "name": "Users",
            "columns": [
                {"name": "id", "type": "INT", "nullable": False},
                {"name": "email", "type": "NVARCHAR(255)", "nullable": False},
                {"name": "ssn", "type": "CHAR(11)", "nullable": True},
                {"name": "phone_number", "type": "VARCHAR(20)", "nullable": True},
            ],
        }

        entry = generator.generate_for_table(table_schema)
        pii_columns = [c for c in entry.columns if c.is_pii]

        assert len(pii_columns) >= 2  # email, ssn, phone_number
