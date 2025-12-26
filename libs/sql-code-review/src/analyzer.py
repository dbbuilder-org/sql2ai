"""SQL code analyzers for security, performance, and style checking."""

import re
from typing import Optional
from dataclasses import dataclass, field

from models import (
    ReviewIssue,
    ReviewRule,
    ReviewResult,
    IssueCategory,
    Severity,
)


@dataclass
class AnalyzerConfig:
    """Configuration for code analyzers."""
    enabled_categories: list[IssueCategory] = field(default_factory=lambda: list(IssueCategory))
    min_severity: Severity = Severity.INFO
    custom_rules: list[ReviewRule] = field(default_factory=list)
    ignore_patterns: list[str] = field(default_factory=list)


class BaseAnalyzer:
    """Base class for SQL code analyzers."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        self.config = config or AnalyzerConfig()
        self.rules: list[ReviewRule] = []

    def analyze(self, code: str, file_path: Optional[str] = None) -> list[ReviewIssue]:
        """Analyze code and return issues."""
        raise NotImplementedError

    def _should_report(self, severity: Severity, category: IssueCategory) -> bool:
        """Check if issue should be reported based on config."""
        if category not in self.config.enabled_categories:
            return False

        severity_order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return severity_order.index(severity) >= severity_order.index(self.config.min_severity)

    def _get_line_number(self, code: str, match_start: int) -> int:
        """Get line number from character position."""
        return code[:match_start].count('\n') + 1

    def _get_code_snippet(self, code: str, line_number: int, context: int = 2) -> str:
        """Get code snippet around a line."""
        lines = code.split('\n')
        start = max(0, line_number - context - 1)
        end = min(len(lines), line_number + context)
        return '\n'.join(lines[start:end])


class SecurityAnalyzer(BaseAnalyzer):
    """Analyzer for SQL security vulnerabilities."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        super().__init__(config)
        self.rules = self._get_security_rules()

    def _get_security_rules(self) -> list[ReviewRule]:
        """Get security-related rules."""
        return [
            ReviewRule(
                id="SEC001",
                name="Dynamic SQL without parameterization",
                description="Dynamic SQL using EXEC() or EXECUTE() without sp_executesql may be vulnerable to SQL injection",
                category=IssueCategory.SECURITY,
                severity=Severity.CRITICAL,
                pattern=r"\bEXEC(?:UTE)?\s*\(\s*['\"]",
            ),
            ReviewRule(
                id="SEC002",
                name="String concatenation in dynamic SQL",
                description="Concatenating user input into SQL strings can lead to SQL injection",
                category=IssueCategory.SECURITY,
                severity=Severity.CRITICAL,
                pattern=r"EXEC(?:UTE)?\s*\([^)]*\+[^)]*@\w+",
            ),
            ReviewRule(
                id="SEC003",
                name="EXECUTE AS with unsafe context",
                description="EXECUTE AS OWNER or SELF may grant excessive privileges",
                category=IssueCategory.SECURITY,
                severity=Severity.HIGH,
                pattern=r"EXECUTE\s+AS\s+(OWNER|SELF)",
            ),
            ReviewRule(
                id="SEC004",
                name="xp_cmdshell usage",
                description="xp_cmdshell can execute operating system commands and is a security risk",
                category=IssueCategory.SECURITY,
                severity=Severity.CRITICAL,
                pattern=r"\bxp_cmdshell\b",
            ),
            ReviewRule(
                id="SEC005",
                name="OPENROWSET/OPENDATASOURCE usage",
                description="Ad-hoc remote access can expose sensitive data",
                category=IssueCategory.SECURITY,
                severity=Severity.HIGH,
                pattern=r"\b(OPENROWSET|OPENDATASOURCE)\b",
            ),
            ReviewRule(
                id="SEC006",
                name="Hardcoded credentials",
                description="Passwords or connection strings should not be hardcoded",
                category=IssueCategory.SECURITY,
                severity=Severity.CRITICAL,
                pattern=r"(PASSWORD|PWD)\s*=\s*['\"][^'\"]+['\"]",
            ),
            ReviewRule(
                id="SEC007",
                name="GRANT to PUBLIC",
                description="Granting permissions to PUBLIC affects all users",
                category=IssueCategory.SECURITY,
                severity=Severity.HIGH,
                pattern=r"\bGRANT\b[^;]*\bTO\s+PUBLIC\b",
            ),
            ReviewRule(
                id="SEC008",
                name="WITH ENCRYPTION missing for sensitive procedures",
                description="Sensitive stored procedures should use WITH ENCRYPTION",
                category=IssueCategory.SECURITY,
                severity=Severity.MEDIUM,
            ),
            ReviewRule(
                id="SEC009",
                name="TRUSTWORTHY database setting",
                description="TRUSTWORTHY should generally be OFF for security",
                category=IssueCategory.SECURITY,
                severity=Severity.HIGH,
                pattern=r"SET\s+TRUSTWORTHY\s+ON",
            ),
            ReviewRule(
                id="SEC010",
                name="Weak encryption algorithm",
                description="MD2, MD4, MD5, SHA, SHA1 are considered weak",
                category=IssueCategory.SECURITY,
                severity=Severity.MEDIUM,
                pattern=r"HASHBYTES\s*\(\s*['\"]?(MD2|MD4|MD5|SHA|SHA1)['\"]?",
            ),
        ]

    def analyze(self, code: str, file_path: Optional[str] = None) -> list[ReviewIssue]:
        """Analyze code for security issues."""
        issues = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            if not self._should_report(rule.severity, rule.category):
                continue

            if rule.pattern:
                for match in re.finditer(rule.pattern, code, re.IGNORECASE):
                    line_num = self._get_line_number(code, match.start())
                    issues.append(ReviewIssue(
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(code, line_num),
                        suggestion=self._get_suggestion(rule.id),
                        documentation_url=rule.documentation_url,
                    ))

        return issues

    def _get_suggestion(self, rule_id: str) -> Optional[str]:
        """Get fix suggestion for a rule."""
        suggestions = {
            "SEC001": "Use sp_executesql with parameters instead of EXEC()",
            "SEC002": "Use sp_executesql with @parameters to prevent SQL injection",
            "SEC003": "Consider using EXECUTE AS CALLER or a specific low-privilege user",
            "SEC004": "Remove xp_cmdshell usage or implement strict input validation",
            "SEC005": "Use linked servers with proper security configuration instead",
            "SEC006": "Store credentials in Azure Key Vault or use Windows Authentication",
            "SEC007": "Grant permissions to specific roles or users instead of PUBLIC",
            "SEC009": "Set TRUSTWORTHY OFF unless absolutely required",
            "SEC010": "Use SHA2_256 or SHA2_512 for secure hashing",
        }
        return suggestions.get(rule_id)


class PerformanceAnalyzer(BaseAnalyzer):
    """Analyzer for SQL performance anti-patterns."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        super().__init__(config)
        self.rules = self._get_performance_rules()

    def _get_performance_rules(self) -> list[ReviewRule]:
        """Get performance-related rules."""
        return [
            ReviewRule(
                id="PERF001",
                name="SELECT *",
                description="Using SELECT * retrieves all columns which may impact performance",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
                pattern=r"\bSELECT\s+\*\s+FROM\b",
            ),
            ReviewRule(
                id="PERF002",
                name="Cursor usage",
                description="Cursors are generally slower than set-based operations",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.HIGH,
                pattern=r"\bDECLARE\s+\w+\s+CURSOR\b",
            ),
            ReviewRule(
                id="PERF003",
                name="NOLOCK hint",
                description="NOLOCK can cause dirty reads and phantom records",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
                pattern=r"\bWITH\s*\(\s*NOLOCK\s*\)",
            ),
            ReviewRule(
                id="PERF004",
                name="Function in WHERE clause",
                description="Functions on columns in WHERE clauses prevent index usage",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.HIGH,
                pattern=r"\bWHERE\b[^;]*\b(CONVERT|CAST|ISNULL|COALESCE|DATEPART|YEAR|MONTH|DAY|LEFT|RIGHT|SUBSTRING)\s*\(\s*\[?\w+\]?",
            ),
            ReviewRule(
                id="PERF005",
                name="LIKE with leading wildcard",
                description="LIKE patterns starting with % cannot use indexes",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.HIGH,
                pattern=r"\bLIKE\s+['\"]%",
            ),
            ReviewRule(
                id="PERF006",
                name="Implicit conversion",
                description="Comparing different data types causes implicit conversion",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
            ),
            ReviewRule(
                id="PERF007",
                name="OR in WHERE clause",
                description="OR conditions may prevent index usage; consider UNION",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.LOW,
                pattern=r"\bWHERE\b[^;]*\bOR\b",
            ),
            ReviewRule(
                id="PERF008",
                name="Missing TOP or pagination",
                description="Queries without TOP or OFFSET-FETCH may return large result sets",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.LOW,
            ),
            ReviewRule(
                id="PERF009",
                name="Scalar UDF in SELECT",
                description="Scalar UDFs in SELECT can cause row-by-row execution",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.HIGH,
                pattern=r"\bSELECT\b[^;]*\bdbo\.\w+\s*\(",
            ),
            ReviewRule(
                id="PERF010",
                name="DISTINCT without need",
                description="DISTINCT requires sorting; ensure it's necessary",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.LOW,
                pattern=r"\bSELECT\s+DISTINCT\b",
            ),
            ReviewRule(
                id="PERF011",
                name="Nested subqueries",
                description="Deeply nested subqueries may be inefficient",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
            ),
            ReviewRule(
                id="PERF012",
                name="Missing transaction isolation",
                description="Consider explicit isolation level for consistent reads",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.LOW,
            ),
        ]

    def analyze(self, code: str, file_path: Optional[str] = None) -> list[ReviewIssue]:
        """Analyze code for performance issues."""
        issues = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            if not self._should_report(rule.severity, rule.category):
                continue

            if rule.pattern:
                for match in re.finditer(rule.pattern, code, re.IGNORECASE):
                    line_num = self._get_line_number(code, match.start())
                    issues.append(ReviewIssue(
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(code, line_num),
                        suggestion=self._get_suggestion(rule.id),
                    ))

        # Check for nested subqueries (special handling)
        nested_count = self._count_nested_subqueries(code)
        if nested_count > 3:
            issues.append(ReviewIssue(
                rule_id="PERF011",
                category=IssueCategory.PERFORMANCE,
                severity=Severity.MEDIUM,
                message=f"Found {nested_count} levels of nested subqueries",
                file_path=file_path,
                suggestion="Consider using CTEs or temp tables for better readability and potential performance",
            ))

        return issues

    def _count_nested_subqueries(self, code: str) -> int:
        """Count maximum nesting level of subqueries."""
        max_depth = 0
        current_depth = 0

        # Simple heuristic: count SELECT within parentheses
        in_string = False
        for i, char in enumerate(code):
            if char == "'" and (i == 0 or code[i-1] != "'"):
                in_string = not in_string
            if in_string:
                continue

            if char == '(':
                # Check if followed by SELECT
                remaining = code[i+1:i+20].strip().upper()
                if remaining.startswith('SELECT'):
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
            elif char == ')':
                if current_depth > 0:
                    current_depth -= 1

        return max_depth

    def _get_suggestion(self, rule_id: str) -> Optional[str]:
        """Get fix suggestion for a rule."""
        suggestions = {
            "PERF001": "Explicitly list only the columns needed",
            "PERF002": "Rewrite using set-based operations (UPDATE/INSERT from SELECT)",
            "PERF003": "Use READ COMMITTED SNAPSHOT or explicit transaction isolation instead",
            "PERF004": "Move the function to the right side or use computed columns",
            "PERF005": "If possible, use LIKE 'value%' or full-text search",
            "PERF007": "Consider rewriting as UNION of separate queries",
            "PERF009": "Convert scalar UDF to inline table-valued function",
            "PERF010": "Verify DISTINCT is needed; check for duplicate JOIN conditions",
        }
        return suggestions.get(rule_id)


class StyleAnalyzer(BaseAnalyzer):
    """Analyzer for SQL style and naming conventions."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        super().__init__(config)
        self.rules = self._get_style_rules()

    def _get_style_rules(self) -> list[ReviewRule]:
        """Get style-related rules."""
        return [
            ReviewRule(
                id="STYLE001",
                name="Inconsistent casing",
                description="SQL keywords should use consistent casing (uppercase recommended)",
                category=IssueCategory.STYLE,
                severity=Severity.INFO,
            ),
            ReviewRule(
                id="STYLE002",
                name="Missing schema prefix",
                description="Objects should be referenced with schema prefix (e.g., dbo.TableName)",
                category=IssueCategory.STYLE,
                severity=Severity.LOW,
                pattern=r"\bFROM\s+(?!\[?\w+\]?\.\[?\w+\]?)(\[?\w+\]?)\s",
            ),
            ReviewRule(
                id="STYLE003",
                name="Procedure naming convention",
                description="Stored procedures should use usp_ prefix",
                category=IssueCategory.STYLE,
                severity=Severity.LOW,
                pattern=r"CREATE\s+(?:OR\s+ALTER\s+)?PROC(?:EDURE)?\s+\[?\w+\]?\.\[?(?!usp_)\w+\]?",
            ),
            ReviewRule(
                id="STYLE004",
                name="Missing SET NOCOUNT ON",
                description="Stored procedures should include SET NOCOUNT ON",
                category=IssueCategory.STYLE,
                severity=Severity.LOW,
            ),
            ReviewRule(
                id="STYLE005",
                name="sp_ prefix usage",
                description="Avoid sp_ prefix as it searches master database first",
                category=IssueCategory.STYLE,
                severity=Severity.MEDIUM,
                pattern=r"CREATE\s+(?:OR\s+ALTER\s+)?PROC(?:EDURE)?\s+\[?\w+\]?\.\[?sp_\w+\]?",
            ),
            ReviewRule(
                id="STYLE006",
                name="Hungarian notation in names",
                description="Avoid Hungarian notation (tbl, vw, fn prefixes)",
                category=IssueCategory.STYLE,
                severity=Severity.INFO,
                pattern=r"\b(tbl_|vw_|fn_|sp_|udf_)\w+",
            ),
            ReviewRule(
                id="STYLE007",
                name="Deprecated syntax",
                description="Avoid deprecated syntax like *= or =* for outer joins",
                category=IssueCategory.STYLE,
                severity=Severity.HIGH,
                pattern=r"(\*=|=\*)",
            ),
            ReviewRule(
                id="STYLE008",
                name="Missing semicolons",
                description="Statements should end with semicolons",
                category=IssueCategory.STYLE,
                severity=Severity.INFO,
            ),
        ]

    def analyze(self, code: str, file_path: Optional[str] = None) -> list[ReviewIssue]:
        """Analyze code for style issues."""
        issues = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            if not self._should_report(rule.severity, rule.category):
                continue

            if rule.pattern:
                for match in re.finditer(rule.pattern, code, re.IGNORECASE):
                    line_num = self._get_line_number(code, match.start())
                    issues.append(ReviewIssue(
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(code, line_num),
                    ))

        # Check for SET NOCOUNT ON in procedures
        if re.search(r"CREATE\s+(?:OR\s+ALTER\s+)?PROC", code, re.IGNORECASE):
            if not re.search(r"SET\s+NOCOUNT\s+ON", code, re.IGNORECASE):
                issues.append(ReviewIssue(
                    rule_id="STYLE004",
                    category=IssueCategory.STYLE,
                    severity=Severity.LOW,
                    message="Stored procedure is missing SET NOCOUNT ON",
                    file_path=file_path,
                    suggestion="Add 'SET NOCOUNT ON;' at the beginning of the procedure",
                ))

        return issues


class BestPracticeAnalyzer(BaseAnalyzer):
    """Analyzer for SQL best practices."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        super().__init__(config)
        self.rules = self._get_best_practice_rules()

    def _get_best_practice_rules(self) -> list[ReviewRule]:
        """Get best practice rules."""
        return [
            ReviewRule(
                id="BP001",
                name="Missing error handling",
                description="Stored procedures should include TRY-CATCH error handling",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.MEDIUM,
            ),
            ReviewRule(
                id="BP002",
                name="Transaction without error handling",
                description="BEGIN TRANSACTION should be paired with error handling",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.HIGH,
                pattern=r"BEGIN\s+TRAN(?:SACTION)?(?![^;]*TRY)",
            ),
            ReviewRule(
                id="BP003",
                name="@@IDENTITY usage",
                description="Use SCOPE_IDENTITY() instead of @@IDENTITY",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.HIGH,
                pattern=r"@@IDENTITY\b",
            ),
            ReviewRule(
                id="BP004",
                name="INSERT without column list",
                description="INSERT should explicitly list columns",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.MEDIUM,
                pattern=r"INSERT\s+INTO\s+\[?\w+\]?\s*VALUES",
            ),
            ReviewRule(
                id="BP005",
                name="NULL comparison",
                description="Use IS NULL or IS NOT NULL instead of = NULL",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.HIGH,
                pattern=r"[=!<>]\s*NULL\b",
            ),
            ReviewRule(
                id="BP006",
                name="GOTO statement",
                description="Avoid GOTO statements; use structured flow control",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.MEDIUM,
                pattern=r"\bGOTO\b",
            ),
            ReviewRule(
                id="BP007",
                name="Missing NOT NULL constraints",
                description="Columns should explicitly specify NULL or NOT NULL",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.LOW,
            ),
            ReviewRule(
                id="BP008",
                name="VARCHAR without length",
                description="Always specify length for VARCHAR/NVARCHAR",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.MEDIUM,
                pattern=r"\b(N?VARCHAR)\s*(?!\s*\()",
            ),
            ReviewRule(
                id="BP009",
                name="Float for money",
                description="Use DECIMAL or MONEY types for currency, not FLOAT",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.HIGH,
            ),
            ReviewRule(
                id="BP010",
                name="Hardcoded dates",
                description="Avoid hardcoded date strings; use date functions",
                category=IssueCategory.BEST_PRACTICE,
                severity=Severity.LOW,
                pattern=r"['\"](\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})['\"]",
            ),
        ]

    def analyze(self, code: str, file_path: Optional[str] = None) -> list[ReviewIssue]:
        """Analyze code for best practice issues."""
        issues = []

        for rule in self.rules:
            if not rule.enabled:
                continue

            if not self._should_report(rule.severity, rule.category):
                continue

            if rule.pattern:
                for match in re.finditer(rule.pattern, code, re.IGNORECASE):
                    line_num = self._get_line_number(code, match.start())
                    issues.append(ReviewIssue(
                        rule_id=rule.id,
                        category=rule.category,
                        severity=rule.severity,
                        message=rule.description,
                        file_path=file_path,
                        line_number=line_num,
                        code_snippet=self._get_code_snippet(code, line_num),
                        suggestion=self._get_suggestion(rule.id),
                    ))

        # Check for missing error handling in procedures
        if re.search(r"CREATE\s+(?:OR\s+ALTER\s+)?PROC", code, re.IGNORECASE):
            if not re.search(r"BEGIN\s+TRY", code, re.IGNORECASE):
                issues.append(ReviewIssue(
                    rule_id="BP001",
                    category=IssueCategory.BEST_PRACTICE,
                    severity=Severity.MEDIUM,
                    message="Stored procedure is missing TRY-CATCH error handling",
                    file_path=file_path,
                    suggestion="Wrap the procedure body in BEGIN TRY...END TRY BEGIN CATCH...END CATCH",
                ))

        return issues

    def _get_suggestion(self, rule_id: str) -> Optional[str]:
        """Get fix suggestion for a rule."""
        suggestions = {
            "BP003": "Use SCOPE_IDENTITY() to get the last identity value in the current scope",
            "BP004": "Add explicit column list: INSERT INTO table (col1, col2) VALUES...",
            "BP005": "Use 'column IS NULL' or 'column IS NOT NULL' instead",
            "BP006": "Refactor using IF/ELSE, WHILE, or RETURN statements",
            "BP008": "Specify length: VARCHAR(50), NVARCHAR(MAX), etc.",
            "BP010": "Use GETDATE(), DATEADD(), or parameter values instead",
        }
        return suggestions.get(rule_id)


class SQLCodeReviewer:
    """Main code reviewer that combines all analyzers."""

    def __init__(self, config: Optional[AnalyzerConfig] = None):
        """Initialize with configuration."""
        self.config = config or AnalyzerConfig()
        self.analyzers = [
            SecurityAnalyzer(config),
            PerformanceAnalyzer(config),
            StyleAnalyzer(config),
            BestPracticeAnalyzer(config),
        ]

    def review(
        self,
        code: str,
        file_path: Optional[str] = None,
    ) -> ReviewResult:
        """Review SQL code and return results."""
        import time
        start_time = time.time()

        all_issues = []
        rules_checked = 0

        for analyzer in self.analyzers:
            issues = analyzer.analyze(code, file_path)
            all_issues.extend(issues)
            rules_checked += len(analyzer.rules)

        duration_ms = int((time.time() - start_time) * 1000)
        lines_of_code = len(code.split('\n'))

        return ReviewResult(
            file_path=file_path,
            code=code,
            issues=all_issues,
            duration_ms=duration_ms,
            rules_checked=rules_checked,
            lines_of_code=lines_of_code,
        )

    def get_all_rules(self) -> list[ReviewRule]:
        """Get all rules from all analyzers."""
        rules = []
        for analyzer in self.analyzers:
            rules.extend(analyzer.rules)
        return rules
