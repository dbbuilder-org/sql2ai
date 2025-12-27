"""API endpoints for SQL Orchestrator."""

import sys
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Try to import orchestrator library (may not be available in all environments)
_ORCHESTRATOR_AVAILABLE = False
try:
    # Check multiple possible paths
    orchestrator_paths = [
        "/Users/admin/dev2/sql2ai/libs/sql-orchestrator/src",
        "/app/libs/sql-orchestrator/src",
        os.path.join(os.path.dirname(__file__), "../../../../libs/sql-orchestrator/src"),
    ]
    for path in orchestrator_paths:
        if os.path.exists(path):
            sys.path.insert(0, path)
            break

    from models import CheckCategory, CheckExecution, CheckStatus, DatabaseHealth
    from checks import CheckDefinition
    _ORCHESTRATOR_AVAILABLE = True
except ImportError:
    # Stub classes for when library is not available
    CheckCategory = None
    CheckExecution = None
    CheckStatus = None
    DatabaseHealth = None
    CheckDefinition = None

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
    get_current_user,
)

router = APIRouter()


def _check_orchestrator_available():
    """Raise 501 if orchestrator library is not available."""
    if not _ORCHESTRATOR_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="SQL Orchestrator functionality not available in this deployment"
        )


# Request/Response models

class RunChecksRequest(BaseModel):
    """Request to run checks."""

    check_ids: Optional[list[str]] = Field(
        None, description="Specific check IDs to run (None = all applicable)"
    )
    category: Optional[str] = Field(
        None, description="Filter by category (performance, security, compliance)"
    )
    framework: Optional[str] = Field(
        None, description="Filter by compliance framework (SOC2, HIPAA, PCI-DSS, GDPR)"
    )
    capture_snapshot: bool = Field(
        False, description="Capture schema snapshot before checks"
    )


class ScheduleCheckRequest(BaseModel):
    """Request to schedule checks."""

    cron_expression: str = Field(..., description="Cron expression for schedule")
    check_ids: list[str] = Field(..., description="Check IDs to run")
    connection_ids: Optional[list[str]] = Field(
        None, description="Connections to check (None = all)"
    )


class DeploymentCheckRequest(BaseModel):
    """Request to run deployment checks."""

    deployment_id: str = Field(..., description="Unique deployment identifier")
    phase: str = Field(..., description="'before' or 'after'")


class CheckResultResponse(BaseModel):
    """Response for a single check result."""

    check_id: str
    check_name: str
    category: str
    severity: str
    status: str
    message: str
    details: dict
    remediation: Optional[str]
    affected_objects: list[str]
    duration_ms: int


class ExecutionResponse(BaseModel):
    """Response for a check execution."""

    id: str
    connection_id: str
    trigger_type: str
    status: str
    started_at: str
    completed_at: Optional[str]
    duration_ms: int
    summary: dict
    results: list[CheckResultResponse]


class HealthResponse(BaseModel):
    """Response for database health."""

    connection_id: str
    connection_name: str
    overall_status: str
    last_check: str
    checks_passed: int
    checks_failed: int
    checks_warning: int
    scores: dict
    critical_issues: list[CheckResultResponse]


class CheckDefinitionResponse(BaseModel):
    """Response for a check definition."""

    id: str
    name: str
    description: str
    category: str
    default_severity: str
    frameworks: list[str]
    tags: list[str]
    enabled: bool


# Placeholder for orchestrator instance
# In production, this would be initialized with proper dependencies
_orchestrator = None


def get_orchestrator():
    """Get the orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not initialized"
        )
    return _orchestrator


# Endpoints

@router.get("/checks", response_model=list[CheckDefinitionResponse])
async def list_available_checks(
    category: Optional[str] = Query(None, description="Filter by category"),
    framework: Optional[str] = Query(None, description="Filter by framework"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """List all available checks.

    Returns definitions of checks that can be run, optionally filtered
    by category or compliance framework.
    """
    from checks import CheckRegistry

    registry = CheckRegistry()

    cat = CheckCategory(category) if category else None
    definitions = registry.list_checks(category=cat, framework=framework)

    return [
        CheckDefinitionResponse(
            id=d.id,
            name=d.name,
            description=d.description,
            category=d.category.value,
            default_severity=d.default_severity.value,
            frameworks=d.frameworks,
            tags=d.tags,
            enabled=d.enabled,
        )
        for d in definitions
    ]


@router.post(
    "/connections/{connection_id}/run",
    response_model=ExecutionResponse,
)
async def run_checks(
    connection_id: str,
    request: RunChecksRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Run checks on a database connection.

    Executes the specified checks (or all applicable checks) against
    the database connection and returns results.
    """
    orchestrator = get_orchestrator()

    cat = CheckCategory(request.category) if request.category else None

    execution = await orchestrator.run_checks(
        connection_id=connection_id,
        check_ids=request.check_ids,
        category=cat,
        framework=request.framework,
        capture_before_snapshot=request.capture_snapshot,
    )

    return _execution_to_response(execution)


@router.post(
    "/connections/{connection_id}/audit/{framework}",
    response_model=ExecutionResponse,
)
async def run_framework_audit(
    connection_id: str,
    framework: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Run a compliance framework audit.

    Executes all checks associated with a specific compliance framework
    (e.g., SOC2, HIPAA, PCI-DSS, GDPR).
    """
    orchestrator = get_orchestrator()

    valid_frameworks = ["SOC2", "HIPAA", "PCI-DSS", "GDPR", "FERPA"]
    if framework.upper() not in valid_frameworks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid framework. Must be one of: {valid_frameworks}"
        )

    execution = await orchestrator.run_framework_audit(
        connection_id=connection_id,
        framework=framework.upper(),
    )

    return _execution_to_response(execution)


@router.post(
    "/connections/{connection_id}/deployment",
    response_model=ExecutionResponse,
)
async def run_deployment_checks(
    connection_id: str,
    request: DeploymentCheckRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Run deployment-related checks.

    Executes checks before or after a database deployment to capture
    before/after state and detect issues.
    """
    if request.phase not in ("before", "after"):
        raise HTTPException(
            status_code=400,
            detail="Phase must be 'before' or 'after'"
        )

    orchestrator = get_orchestrator()

    execution = await orchestrator.run_deployment_checks(
        connection_id=connection_id,
        deployment_id=request.deployment_id,
        phase=request.phase,
    )

    return _execution_to_response(execution)


@router.get(
    "/connections/{connection_id}/health",
    response_model=HealthResponse,
)
async def get_connection_health(
    connection_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """Get health status for a database connection.

    Returns the cached health status from the most recent check execution.
    """
    orchestrator = get_orchestrator()

    health = orchestrator.get_health(connection_id)
    if not health:
        raise HTTPException(
            status_code=404,
            detail="No health data available for this connection"
        )

    return _health_to_response(health)


@router.get("/health", response_model=list[HealthResponse])
async def get_all_health(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """Get health status for all monitored connections.

    Returns cached health status for all database connections
    that have been checked.
    """
    orchestrator = get_orchestrator()
    healths = orchestrator.get_all_health()

    return [_health_to_response(h) for h in healths]


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """Get a specific check execution by ID.

    Returns detailed results for a previous check execution.
    """
    orchestrator = get_orchestrator()

    execution = orchestrator.get_execution(execution_id)
    if not execution:
        raise HTTPException(
            status_code=404,
            detail="Execution not found"
        )

    return _execution_to_response(execution)


@router.get("/executions", response_model=list[ExecutionResponse])
async def list_executions(
    connection_id: Optional[str] = Query(None, description="Filter by connection"),
    limit: int = Query(10, ge=1, le=100, description="Maximum results"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """List recent check executions.

    Returns recent check executions, optionally filtered by connection.
    """
    orchestrator = get_orchestrator()

    executions = orchestrator.get_recent_executions(
        connection_id=connection_id,
        limit=limit,
    )

    return [_execution_to_response(e) for e in executions]


@router.post("/schedules")
async def create_schedule(
    request: ScheduleCheckRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.ADMIN_SETTINGS])
    ),
):
    """Create a scheduled check.

    Sets up a recurring schedule for running checks on specified connections.
    """
    orchestrator = get_orchestrator()

    trigger = orchestrator.add_scheduled_check(
        cron_expression=request.cron_expression,
        check_ids=request.check_ids,
    )

    return {
        "message": "Schedule created",
        "cron_expression": request.cron_expression,
        "check_ids": request.check_ids,
        "next_run": trigger.get_next_run().isoformat(),
    }


# Helper functions

def _execution_to_response(execution: CheckExecution) -> ExecutionResponse:
    """Convert CheckExecution to response model."""
    return ExecutionResponse(
        id=execution.id,
        connection_id=execution.connection_id,
        trigger_type=execution.trigger_type,
        status=execution.status.value,
        started_at=execution.started_at.isoformat(),
        completed_at=execution.completed_at.isoformat() if execution.completed_at else None,
        duration_ms=execution.duration_ms,
        summary={
            "total": len(execution.results),
            "passed": execution.passed_count,
            "failed": execution.failed_count,
            "warnings": execution.warning_count,
        },
        results=[
            CheckResultResponse(
                check_id=r.check_id,
                check_name=r.check_name,
                category=r.category.value,
                severity=r.severity.value,
                status=r.status.value,
                message=r.message,
                details=r.details,
                remediation=r.remediation,
                affected_objects=r.affected_objects,
                duration_ms=r.duration_ms,
            )
            for r in execution.results
        ],
    )


def _health_to_response(health: DatabaseHealth) -> HealthResponse:
    """Convert DatabaseHealth to response model."""
    return HealthResponse(
        connection_id=health.connection_id,
        connection_name=health.connection_name,
        overall_status=health.overall_status.value,
        last_check=health.last_check.isoformat(),
        checks_passed=health.checks_passed,
        checks_failed=health.checks_failed,
        checks_warning=health.checks_warning,
        scores={
            "performance": health.performance_score,
            "security": health.security_score,
            "compliance": health.compliance_score,
        },
        critical_issues=[
            CheckResultResponse(
                check_id=r.check_id,
                check_name=r.check_name,
                category=r.category.value,
                severity=r.severity.value,
                status=r.status.value,
                message=r.message,
                details=r.details,
                remediation=r.remediation,
                affected_objects=r.affected_objects,
                duration_ms=r.duration_ms,
            )
            for r in health.critical_issues
        ],
    )
