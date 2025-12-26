"""API endpoints for SQL Code Review."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

# Add code review library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-code-review/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class ReviewRequest(BaseModel):
    """Request to review SQL code."""

    code: str = Field(..., description="SQL code to review")
    file_path: Optional[str] = Field(None, description="Optional file path for context")
    categories: Optional[list[str]] = Field(
        None,
        description="Categories to check: security, performance, style, best_practice"
    )
    min_severity: str = Field("info", description="Minimum severity: info, low, medium, high, critical")


class ReviewIssueResponse(BaseModel):
    """Response for a single review issue."""

    rule_id: str
    category: str
    severity: str
    message: str
    line_number: Optional[int]
    code_snippet: Optional[str]
    suggestion: Optional[str]


class ReviewResultResponse(BaseModel):
    """Response for code review."""

    passed: bool
    issues: list[ReviewIssueResponse]
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    rules_checked: int
    lines_of_code: int
    duration_ms: int


class ReleaseNotesRequest(BaseModel):
    """Request to generate release notes."""

    version: str = Field(..., description="Release version")
    diffs: list[dict] = Field(..., description="Schema differences")


class DataDictionaryRequest(BaseModel):
    """Request to generate data dictionary."""

    connection_id: str = Field(..., description="Database connection ID")
    include_ai_descriptions: bool = Field(True, description="Generate AI descriptions")


class ColumnDocResponse(BaseModel):
    """Response for column documentation."""

    name: str
    data_type: str
    nullable: bool
    description: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    foreign_key_reference: Optional[str] = None
    is_pii: bool = False


class ObjectDocResponse(BaseModel):
    """Response for object documentation."""

    name: str
    schema_name: str
    category: str
    description: str
    columns: list[ColumnDocResponse] = []
    parameters: list[dict] = []


# Endpoints

@router.post("/review", response_model=ReviewResultResponse)
async def review_code(
    request: ReviewRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_REVIEW])
    ),
):
    """Review SQL code for issues.

    Analyzes SQL code for security vulnerabilities, performance
    anti-patterns, style issues, and best practice violations.
    """
    from analyzer import SQLCodeReviewer, AnalyzerConfig, IssueCategory, Severity

    # Map categories
    category_map = {
        "security": IssueCategory.SECURITY,
        "performance": IssueCategory.PERFORMANCE,
        "style": IssueCategory.STYLE,
        "best_practice": IssueCategory.BEST_PRACTICE,
        "maintainability": IssueCategory.MAINTAINABILITY,
        "correctness": IssueCategory.CORRECTNESS,
    }

    severity_map = {
        "info": Severity.INFO,
        "low": Severity.LOW,
        "medium": Severity.MEDIUM,
        "high": Severity.HIGH,
        "critical": Severity.CRITICAL,
    }

    # Build config
    enabled_categories = list(IssueCategory)
    if request.categories:
        enabled_categories = [
            category_map[c.lower()]
            for c in request.categories
            if c.lower() in category_map
        ]

    min_severity = severity_map.get(request.min_severity.lower(), Severity.INFO)

    config = AnalyzerConfig(
        enabled_categories=enabled_categories,
        min_severity=min_severity,
    )

    reviewer = SQLCodeReviewer(config)
    result = reviewer.review(request.code, request.file_path)

    # Count by severity
    severity_counts = {
        "critical": 0, "high": 0, "medium": 0, "low": 0
    }
    for issue in result.issues:
        if issue.severity.value in severity_counts:
            severity_counts[issue.severity.value] += 1

    return ReviewResultResponse(
        passed=result.passed,
        issues=[
            ReviewIssueResponse(
                rule_id=i.rule_id,
                category=i.category.value,
                severity=i.severity.value,
                message=i.message,
                line_number=i.line_number,
                code_snippet=i.code_snippet,
                suggestion=i.suggestion,
            )
            for i in result.issues
        ],
        critical_count=severity_counts["critical"],
        high_count=severity_counts["high"],
        medium_count=severity_counts["medium"],
        low_count=severity_counts["low"],
        rules_checked=result.rules_checked,
        lines_of_code=result.lines_of_code,
        duration_ms=result.duration_ms,
    )


@router.get("/rules")
async def list_rules(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_REVIEW])
    ),
):
    """List all code review rules.

    Returns all available rules organized by category.
    """
    from analyzer import SQLCodeReviewer

    reviewer = SQLCodeReviewer()
    rules = reviewer.get_all_rules()

    # Group by category
    grouped = {}
    for rule in rules:
        category = rule.category.value
        if category not in grouped:
            grouped[category] = []

        grouped[category].append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "severity": rule.severity.value,
            "enabled": rule.enabled,
        })

    return {"rules": grouped}


@router.post("/release-notes")
async def generate_release_notes(
    request: ReleaseNotesRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_REVIEW])
    ),
):
    """Generate release notes from schema changes.

    Creates formatted release notes with breaking changes,
    features, fixes, and migration notes.
    """
    from release_notes import ReleaseNotesGenerator, SchemaDiff
    from datetime import datetime

    generator = ReleaseNotesGenerator()

    # Convert diffs
    diffs = [
        SchemaDiff(
            object_type=d["object_type"],
            object_name=d["object_name"],
            change_type=d["change_type"],
            old_definition=d.get("old_definition"),
            new_definition=d.get("new_definition"),
            changes=d.get("changes", []),
        )
        for d in request.diffs
    ]

    notes = await generator.generate(
        diffs=diffs,
        version=request.version,
        release_date=datetime.utcnow(),
    )

    return {
        "version": notes.version,
        "release_date": notes.release_date.isoformat(),
        "summary": notes.summary,
        "markdown": notes.to_markdown(),
        "breaking_changes_count": len(notes.breaking_changes),
        "changes_count": len(notes.changes),
        "migration_sql": notes.migration_sql,
        "rollback_sql": notes.rollback_sql,
    }


@router.post("/connections/{connection_id}/data-dictionary")
async def generate_data_dictionary(
    connection_id: str,
    include_ai_descriptions: bool = True,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Generate data dictionary for a database.

    Creates comprehensive documentation including tables,
    views, procedures, and relationships.
    """
    from data_dictionary import DataDictionaryGenerator

    # In production, would get actual connection
    async def mock_query(sql):
        raise HTTPException(
            status_code=501,
            detail="Data dictionary requires live database connection"
        )

    generator = DataDictionaryGenerator(
        db_query=mock_query,
        ai_completion=None,  # Would configure AI in production
    )

    try:
        dictionary = await generator.generate(
            database_name=f"database_{connection_id}",
            include_ai_descriptions=include_ai_descriptions,
        )

        return {
            "database_name": dictionary.database_name,
            "generated_at": dictionary.generated_at.isoformat(),
            "version": dictionary.version,
            "description": dictionary.description,
            "object_count": len(dictionary.objects),
            "relationship_count": len(dictionary.relationships),
            "markdown": dictionary.to_markdown(),
            "openapi_schema": dictionary.to_openapi_schema(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}/data-dictionary/objects")
async def list_documented_objects(
    connection_id: str,
    category: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """List documented objects.

    Returns summary of all documented database objects.
    """
    # In production, would retrieve from stored dictionary
    return {
        "connection_id": connection_id,
        "message": "Data dictionary requires generation first",
        "objects": [],
    }


@router.post("/review/batch")
async def batch_review(
    files: list[dict],
    min_severity: str = "medium",
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.AI_REVIEW])
    ),
):
    """Review multiple SQL files.

    Analyzes multiple files and returns aggregated results.
    """
    from analyzer import SQLCodeReviewer, AnalyzerConfig, Severity

    severity_map = {
        "info": Severity.INFO,
        "low": Severity.LOW,
        "medium": Severity.MEDIUM,
        "high": Severity.HIGH,
        "critical": Severity.CRITICAL,
    }

    config = AnalyzerConfig(
        min_severity=severity_map.get(min_severity.lower(), Severity.MEDIUM),
    )

    reviewer = SQLCodeReviewer(config)

    results = []
    total_issues = 0
    files_with_issues = 0

    for file_info in files:
        file_path = file_info.get("path", "unknown")
        code = file_info.get("code", "")

        result = reviewer.review(code, file_path)
        total_issues += len(result.issues)

        if result.issues:
            files_with_issues += 1

        results.append({
            "file_path": file_path,
            "passed": result.passed,
            "issue_count": len(result.issues),
            "critical_count": result.critical_count,
            "high_count": result.high_count,
        })

    return {
        "files_reviewed": len(files),
        "files_with_issues": files_with_issues,
        "total_issues": total_issues,
        "results": results,
    }
