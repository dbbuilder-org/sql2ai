"""API endpoints for SQL Compliance."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Add compliance library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-compliance/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class ScanRequest(BaseModel):
    """Request for compliance scan."""

    frameworks: Optional[list[str]] = Field(
        None, description="Frameworks to check: SOC2, HIPAA, PCI-DSS, GDPR, FERPA, CCPA"
    )
    include_pii_scan: bool = Field(True, description="Include PII data scanning")
    pii_sample_size: int = Field(1000, ge=100, le=10000, description="Rows to sample per column")


class PIIFindingResponse(BaseModel):
    """Response for a PII finding."""

    table_name: str
    column_name: str
    pii_type: str
    confidence: float
    sample_count: int
    affected_percentage: float
    remediation: Optional[str]


class ComplianceResultResponse(BaseModel):
    """Response for a compliance check result."""

    check_id: str
    check_name: str
    framework: str
    status: str
    message: str
    severity: str
    remediation: Optional[str]


class EncryptionStatusResponse(BaseModel):
    """Response for encryption status."""

    tde_enabled: bool
    tde_algorithm: Optional[str]
    tls_enforced: bool
    tls_version: Optional[str]
    backup_encryption: bool
    column_encryption: bool


class ComplianceReportResponse(BaseModel):
    """Response for compliance report."""

    connection_id: str
    database_name: str
    frameworks: list[str]
    overall_status: str
    duration_ms: int
    summary: dict
    check_results: list[ComplianceResultResponse]
    pii_findings: list[PIIFindingResponse]
    encryption_status: Optional[EncryptionStatusResponse]


class QuickStatusResponse(BaseModel):
    """Response for quick compliance status."""

    connection_id: str
    timestamp: str
    frameworks: dict


# Endpoints

@router.post(
    "/connections/{connection_id}/scan",
    response_model=ComplianceReportResponse,
)
async def scan_compliance(
    connection_id: str,
    request: ScanRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Run comprehensive compliance scan.

    Checks encryption, audit configuration, access controls,
    and optionally scans for PII/PHI data.
    """
    from compliance import SQLCompliance
    from models import ComplianceFramework

    # Parse frameworks
    frameworks = None
    if request.frameworks:
        try:
            frameworks = [ComplianceFramework(f.upper()) for f in request.frameworks]
        except ValueError as e:
            valid = [f.value for f in ComplianceFramework]
            raise HTTPException(
                status_code=400,
                detail=f"Invalid framework. Must be one of: {valid}"
            )

    # In production, get actual connection
    async def mock_provider(conn_id):
        raise HTTPException(status_code=501, detail="Requires live database connection")

    compliance = SQLCompliance(
        connection_provider=mock_provider,
        pii_sample_size=request.pii_sample_size,
    )

    try:
        report = await compliance.scan(
            connection_id=connection_id,
            frameworks=frameworks,
            include_pii_scan=request.include_pii_scan,
        )
        return _report_to_response(report)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/connections/{connection_id}/scan/{framework}",
    response_model=ComplianceReportResponse,
)
async def scan_framework(
    connection_id: str,
    framework: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Run compliance scan for a specific framework.

    Runs all checks applicable to the specified compliance framework.
    """
    from compliance import SQLCompliance
    from models import ComplianceFramework

    try:
        fw = ComplianceFramework(framework.upper())
    except ValueError:
        valid = [f.value for f in ComplianceFramework]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid framework. Must be one of: {valid}"
        )

    async def mock_provider(conn_id):
        raise HTTPException(status_code=501, detail="Requires live database connection")

    compliance = SQLCompliance(connection_provider=mock_provider)

    try:
        report = await compliance.scan_framework(connection_id, fw)
        return _report_to_response(report)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/connections/{connection_id}/status",
    response_model=QuickStatusResponse,
)
async def get_quick_status(
    connection_id: str,
    frameworks: Optional[str] = Query(None, description="Comma-separated frameworks"),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """Get quick compliance status without full scan.

    Returns quick checks for TDE, audit, etc. without data scanning.
    """
    from compliance import SQLCompliance
    from models import ComplianceFramework

    fw_list = None
    if frameworks:
        try:
            fw_list = [ComplianceFramework(f.strip().upper()) for f in frameworks.split(",")]
        except ValueError:
            pass

    async def mock_provider(conn_id):
        raise HTTPException(status_code=501, detail="Requires live database connection")

    compliance = SQLCompliance(connection_provider=mock_provider)

    try:
        status = await compliance.get_quick_status(connection_id, fw_list)
        return QuickStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/connections/{connection_id}/evidence/{framework}",
)
async def generate_evidence(
    connection_id: str,
    framework: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Generate compliance evidence for auditors.

    Generates a comprehensive evidence package for the specified
    compliance framework audit.
    """
    from compliance import SQLCompliance
    from models import ComplianceFramework

    try:
        fw = ComplianceFramework(framework.upper())
    except ValueError:
        valid = [f.value for f in ComplianceFramework]
        raise HTTPException(
            status_code=400,
            detail=f"Invalid framework. Must be one of: {valid}"
        )

    async def mock_provider(conn_id):
        raise HTTPException(status_code=501, detail="Requires live database connection")

    compliance = SQLCompliance(connection_provider=mock_provider)

    try:
        evidence = await compliance.generate_evidence(connection_id, fw)
        return evidence
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections/{connection_id}/pii")
async def scan_pii_only(
    connection_id: str,
    sample_size: int = Query(1000, ge=100, le=10000),
    confidence_threshold: float = Query(0.7, ge=0.5, le=1.0),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_SCAN])
    ),
):
    """Scan for PII/PHI data only.

    Scans all text columns for personal identifiable information
    using Presidio NLP engine.
    """
    from scanner import PIIScanner

    scanner = PIIScanner(
        sample_size=sample_size,
        confidence_threshold=confidence_threshold,
    )

    # In production, get actual connection and scan
    return {
        "connection_id": connection_id,
        "message": "PII scan requires live database connection",
        "findings": [],
    }


@router.get("/connections/{connection_id}/encryption")
async def get_encryption_status(
    connection_id: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """Get encryption configuration status.

    Returns TDE, TLS, backup encryption, and Always Encrypted status.
    """
    from scanner import EncryptionScanner

    scanner = EncryptionScanner()

    # In production, get actual connection and check
    return {
        "connection_id": connection_id,
        "message": "Encryption check requires live database connection",
        "status": None,
    }


@router.get("/frameworks")
async def list_frameworks(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.COMPLIANCE_READ])
    ),
):
    """List available compliance frameworks.

    Returns all supported compliance frameworks and their check counts.
    """
    from compliance import FRAMEWORK_CHECKS
    from models import ComplianceFramework

    return {
        "frameworks": [
            {
                "id": fw.value,
                "name": fw.value,
                "checks": len(FRAMEWORK_CHECKS.get(fw, [])),
            }
            for fw in ComplianceFramework
        ]
    }


# Helper functions

def _report_to_response(report) -> ComplianceReportResponse:
    """Convert ComplianceReport to response model."""
    return ComplianceReportResponse(
        connection_id=report.connection_id,
        database_name=report.database_name,
        frameworks=[f.value for f in report.frameworks],
        overall_status=report.overall_status.value,
        duration_ms=report.duration_ms,
        summary={
            "compliant_checks": report.compliant_checks,
            "non_compliant_checks": report.non_compliant_checks,
            "total_checks": report.total_checks,
            "pii_findings_count": len(report.pii_findings),
        },
        check_results=[
            ComplianceResultResponse(
                check_id=r.check_id,
                check_name=r.check_name,
                framework=r.framework.value,
                status=r.status.value,
                message=r.message,
                severity=r.severity.value,
                remediation=r.remediation,
            )
            for r in report.check_results
        ],
        pii_findings=[
            PIIFindingResponse(
                table_name=f.table_name,
                column_name=f.column_name,
                pii_type=f.pii_type.value,
                confidence=f.confidence,
                sample_count=f.sample_count,
                affected_percentage=f.affected_percentage,
                remediation=f.remediation,
            )
            for f in report.pii_findings
        ],
        encryption_status=EncryptionStatusResponse(
            tde_enabled=report.encryption_status.tde_enabled,
            tde_algorithm=report.encryption_status.tde_algorithm,
            tls_enforced=report.encryption_status.tls_enforced,
            tls_version=report.encryption_status.tls_version,
            backup_encryption=report.encryption_status.backup_encryption,
            column_encryption=report.encryption_status.column_encryption,
        ) if report.encryption_status else None,
    )
