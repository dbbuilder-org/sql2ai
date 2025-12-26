"""Data models for SQL Compliance."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""

    SOC2 = "SOC2"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI-DSS"
    GDPR = "GDPR"
    FERPA = "FERPA"
    CCPA = "CCPA"


class ComplianceStatus(str, Enum):
    """Status of a compliance check."""

    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIAL = "partial"
    NOT_APPLICABLE = "not_applicable"
    ERROR = "error"


class PIIType(str, Enum):
    """Types of PII/PHI data."""

    # Personal identifiers
    SSN = "SSN"
    PASSPORT = "PASSPORT"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"

    # Contact info
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    ADDRESS = "ADDRESS"

    # Financial
    CREDIT_CARD = "CREDIT_CARD"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    IBAN = "IBAN"

    # Health (PHI)
    MEDICAL_RECORD = "MEDICAL_RECORD"
    HEALTH_INSURANCE_ID = "HEALTH_INSURANCE_ID"
    DIAGNOSIS = "DIAGNOSIS"
    PRESCRIPTION = "PRESCRIPTION"

    # Other
    DATE_OF_BIRTH = "DATE_OF_BIRTH"
    IP_ADDRESS = "IP_ADDRESS"
    PERSON_NAME = "PERSON_NAME"
    LOCATION = "LOCATION"


class Severity(str, Enum):
    """Severity of compliance issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class PIIFinding:
    """A PII/PHI finding in data."""

    table_name: str
    column_name: str
    pii_type: PIIType
    confidence: float
    sample_count: int
    total_rows_scanned: int
    detection_method: str = "presidio"
    remediation: Optional[str] = None

    @property
    def affected_percentage(self) -> float:
        """Percentage of rows containing PII."""
        if self.total_rows_scanned == 0:
            return 0
        return (self.sample_count / self.total_rows_scanned) * 100

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "column_name": self.column_name,
            "pii_type": self.pii_type.value,
            "confidence": self.confidence,
            "sample_count": self.sample_count,
            "total_rows_scanned": self.total_rows_scanned,
            "affected_percentage": self.affected_percentage,
            "detection_method": self.detection_method,
            "remediation": self.remediation,
        }


@dataclass
class ComplianceCheck:
    """A compliance check definition."""

    id: str
    name: str
    description: str
    framework: ComplianceFramework
    category: str
    severity: Severity
    check_query: Optional[str] = None
    remediation: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "framework": self.framework.value,
            "category": self.category,
            "severity": self.severity.value,
            "remediation": self.remediation,
        }


@dataclass
class ComplianceResult:
    """Result of a compliance check."""

    check_id: str
    check_name: str
    framework: ComplianceFramework
    status: ComplianceStatus
    message: str
    severity: Severity
    details: dict[str, Any] = field(default_factory=dict)
    remediation: Optional[str] = None
    evidence: Optional[str] = None
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "check_name": self.check_name,
            "framework": self.framework.value,
            "status": self.status.value,
            "message": self.message,
            "severity": self.severity.value,
            "details": self.details,
            "remediation": self.remediation,
            "evidence": self.evidence,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class AccessControlFinding:
    """Finding from access control analysis."""

    principal_name: str
    principal_type: str  # user, role, group
    permission: str
    object_name: str
    object_type: str
    is_excessive: bool = False
    recommendation: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "principal_name": self.principal_name,
            "principal_type": self.principal_type,
            "permission": self.permission,
            "object_name": self.object_name,
            "object_type": self.object_type,
            "is_excessive": self.is_excessive,
            "recommendation": self.recommendation,
        }


@dataclass
class EncryptionStatus:
    """Encryption status for a database."""

    tde_enabled: bool = False
    tde_algorithm: Optional[str] = None
    tls_enforced: bool = False
    tls_version: Optional[str] = None
    backup_encryption: bool = False
    column_encryption: bool = False
    always_encrypted_columns: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "tde_enabled": self.tde_enabled,
            "tde_algorithm": self.tde_algorithm,
            "tls_enforced": self.tls_enforced,
            "tls_version": self.tls_version,
            "backup_encryption": self.backup_encryption,
            "column_encryption": self.column_encryption,
            "always_encrypted_columns": self.always_encrypted_columns,
        }


@dataclass
class ComplianceReport:
    """Complete compliance report."""

    connection_id: str
    database_name: str
    frameworks: list[ComplianceFramework]
    scanned_at: datetime = field(default_factory=datetime.utcnow)
    duration_ms: int = 0

    # Results
    check_results: list[ComplianceResult] = field(default_factory=list)
    pii_findings: list[PIIFinding] = field(default_factory=list)
    access_findings: list[AccessControlFinding] = field(default_factory=list)
    encryption_status: Optional[EncryptionStatus] = None

    # Summary
    overall_status: ComplianceStatus = ComplianceStatus.COMPLIANT
    compliant_checks: int = 0
    non_compliant_checks: int = 0
    total_checks: int = 0

    def calculate_status(self):
        """Calculate overall compliance status."""
        self.total_checks = len(self.check_results)
        self.compliant_checks = sum(
            1 for r in self.check_results if r.status == ComplianceStatus.COMPLIANT
        )
        self.non_compliant_checks = sum(
            1 for r in self.check_results if r.status == ComplianceStatus.NON_COMPLIANT
        )

        # Critical findings mean non-compliant
        critical = any(
            r.status == ComplianceStatus.NON_COMPLIANT and r.severity == Severity.CRITICAL
            for r in self.check_results
        )
        if critical:
            self.overall_status = ComplianceStatus.NON_COMPLIANT
        elif self.non_compliant_checks > 0:
            self.overall_status = ComplianceStatus.PARTIAL
        else:
            self.overall_status = ComplianceStatus.COMPLIANT

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        self.calculate_status()

        return {
            "connection_id": self.connection_id,
            "database_name": self.database_name,
            "frameworks": [f.value for f in self.frameworks],
            "scanned_at": self.scanned_at.isoformat(),
            "duration_ms": self.duration_ms,
            "summary": {
                "overall_status": self.overall_status.value,
                "compliant_checks": self.compliant_checks,
                "non_compliant_checks": self.non_compliant_checks,
                "total_checks": self.total_checks,
                "pii_findings_count": len(self.pii_findings),
                "access_findings_count": len(self.access_findings),
            },
            "check_results": [r.to_dict() for r in self.check_results],
            "pii_findings": [f.to_dict() for f in self.pii_findings],
            "access_findings": [f.to_dict() for f in self.access_findings],
            "encryption_status": self.encryption_status.to_dict() if self.encryption_status else None,
        }


@dataclass
class DataClassification:
    """Classification of data sensitivity."""

    table_name: str
    column_name: str
    classification: str  # public, internal, confidential, restricted
    pii_types: list[PIIType] = field(default_factory=list)
    frameworks_affected: list[ComplianceFramework] = field(default_factory=list)
    encryption_required: bool = False
    masking_required: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "table_name": self.table_name,
            "column_name": self.column_name,
            "classification": self.classification,
            "pii_types": [p.value for p in self.pii_types],
            "frameworks_affected": [f.value for f in self.frameworks_affected],
            "encryption_required": self.encryption_required,
            "masking_required": self.masking_required,
        }
