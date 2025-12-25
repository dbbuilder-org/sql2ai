# SQL Compliance

**Module 8 of 8** | **Status:** Planned | **Priority:** P1

## Overview

SQL Compliance provides automated compliance checking at the database level for SOC 2, HIPAA, PCI-DSS, GDPR, and FERPA. Unlike application-level tools, it checks where data is most vulnerable: the database, where data is often unencrypted, unprotected, and unobfuscated.

## Why Database-Level Compliance?

```
Application Layer: "We encrypt PII in the UI"
                        ↓
API Layer: "We mask SSN in responses"
                        ↓
Database Layer: ⚠ DATA STORED IN PLAIN TEXT
                   No encryption at rest
                   No column-level encryption
                   No data masking
                   No access controls
                   Full SSN visible to DBAs
```

SQL Compliance checks the actual data storage, not just the access layer.

## Supported Frameworks

### SOC 2 Type I & II

**Trust Service Criteria Covered:**
- CC6.1: Logical and physical access controls
- CC6.2: Prior to issuing credentials
- CC6.3: Authorization to access
- CC6.6: Restrictions on access
- CC6.7: Removal of access
- CC6.8: Security incidents

### HIPAA

**Technical Safeguards (164.312):**
- Access Control (164.312(a)(1))
- Audit Controls (164.312(b))
- Integrity (164.312(c)(1))
- Transmission Security (164.312(e)(1))

**PHI Categories Detected:**
- Patient names
- Medical record numbers
- Health conditions
- Treatment information
- Insurance IDs

### PCI-DSS v4.0

**Requirements Covered:**
- Req 3: Protect stored account data
- Req 7: Restrict access to system components
- Req 8: Identify users and authenticate access
- Req 10: Log and monitor all access

**Data Elements Detected:**
- Primary Account Number (PAN)
- Card expiration dates
- CVV/CVC codes
- Cardholder names

### GDPR

**Articles Covered:**
- Article 5: Data processing principles
- Article 17: Right to erasure
- Article 25: Data protection by design
- Article 32: Security of processing

**Personal Data Categories:**
- Contact information
- Identification numbers
- Financial data
- Location data
- Online identifiers

### FERPA

**Requirements Covered:**
- Student records protection
- Directory information controls
- Third-party access restrictions

## Check Categories

### 1. Configuration Checks

**Encryption at Rest (TDE)**
```
Check: TDE_ENABLED
Status: ⚠ FAIL

Database: CustomerDB
TDE Status: Not Enabled

Impact:
- Data files readable if stolen
- Backup files unprotected
- Non-compliant with SOC2 CC6.1, HIPAA 164.312(e)(1)

Remediation:
USE master;
CREATE DATABASE ENCRYPTION KEY
WITH ALGORITHM = AES_256
ENCRYPTION BY SERVER CERTIFICATE TDECert;

ALTER DATABASE CustomerDB SET ENCRYPTION ON;

[Apply Fix] [Show Full Script] [Schedule]
```

**Encryption in Transit (TLS)**
```
Check: TLS_REQUIRED
Status: ✓ PASS

Server: SQLPROD01
Force Encryption: Enabled
Certificate: Valid until 2025-06-15
Protocol: TLS 1.2
```

**Audit Configuration**
```
Check: AUDIT_ENABLED
Status: ⚠ PARTIAL

SQL Server Audit: Enabled
Audit Specification: Configured

Missing Audits:
- SELECT on sensitive tables (Customers, Payments)
- EXECUTE on stored procedures
- Schema changes (DDL)

Remediation Script:
CREATE SERVER AUDIT SPECIFICATION AuditSensitiveAccess
FOR SERVER AUDIT MainAudit
ADD (SELECT ON dbo.Customers BY public),
ADD (EXECUTE ON dbo.sp_ProcessPayment BY public);

[Apply Fix] [Customize]
```

### 2. Access Control Checks

**Excessive Permissions**
```
Check: LEAST_PRIVILEGE
Status: ⚠ FAIL

Findings:
1. webapp_user has db_owner role (12 databases)
   - Should use: Specific object permissions

2. etl_service has sysadmin role
   - Should use: db_datareader, db_datawriter on specific DBs

3. 47 logins have not been used in 90+ days
   - Action: Disable or remove

Compliance Impact:
- SOC2 CC6.1, CC6.3: Non-compliant
- HIPAA 164.312(a)(1): Non-compliant
- PCI-DSS Req 7.1: Non-compliant

[Generate Remediation Script] [Export Report]
```

**Orphaned Users**
```
Check: ORPHANED_USERS
Status: ⚠ WARNING

Orphaned Users Found:
- OldDevUser (Database: CustomerDB)
- TempAdmin (Database: ReportingDB)
- Test_Account (Database: CustomerDB)

These users have no corresponding login and could
potentially be hijacked for unauthorized access.

Remediation:
DROP USER [OldDevUser];
-- or --
ALTER USER [OldDevUser] WITH LOGIN = [ValidLogin];

[Remove All] [Review Each]
```

### 3. Data-Level Checks (Presidio Integration)

**PII/PHI Detection**
```
Check: DATA_PII_SCAN
Status: ⚠ FAIL

Scan Results (Sample: 1,000 rows per table)

Table: dbo.Customers
┌─────────────┬──────────────┬────────────┬────────────┐
│ Column      │ PII Type     │ Confidence │ Count      │
├─────────────┼──────────────┼────────────┼────────────┤
│ SSN         │ US_SSN       │ 98%        │ 1,000      │
│ Email       │ EMAIL        │ 99%        │ 1,000      │
│ Phone       │ PHONE_NUMBER │ 95%        │ 892        │
│ Notes       │ PERSON       │ 72%        │ 234        │
└─────────────┴──────────────┴────────────┴────────────┘

⚠ SSN column contains unencrypted Social Security Numbers
⚠ Notes column contains names mentioned in free text

Recommendations:
1. Encrypt SSN column using Always Encrypted
2. Implement data masking for non-privileged users
3. Review Notes column for PII scrubbing

[Show Encryption Script] [Show Masking Script]
```

**Cardholder Data Detection (PCI)**
```
Check: PCI_CARDHOLDER_DATA
Status: ⚠ CRITICAL

CRITICAL: Unencrypted cardholder data detected!

Table: dbo.Payments
Column: CardNumber
Sample: 4532************ (PAN detected)
Count: 145,678 rows

This is a PCI-DSS violation. Card numbers must be:
- Encrypted with strong cryptography
- Access restricted to need-to-know
- Masked when displayed (show last 4 only)

Immediate Actions Required:
1. Encrypt CardNumber column
2. Truncate/tokenize historical data
3. Implement access logging

[Emergency Remediation] [Export for QSA]
```

### 4. Python/Presidio Integration

```python
# libs/compliance-scanner/src/scanner.py

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
import pyodbc

class DataComplianceScanner:
    def __init__(self, connection_string: str):
        self.connection = pyodbc.connect(connection_string)
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()

        # Add custom recognizers
        self.add_custom_patterns()

    def add_custom_patterns(self):
        """Add custom patterns for healthcare, financial data"""
        # MRN (Medical Record Number) pattern
        # Custom employee ID patterns
        # Internal account number formats
        pass

    def scan_table(self, table_name: str, sample_size: int = 1000):
        """Scan a table for PII/PHI"""
        cursor = self.connection.cursor()

        # Get column info
        cursor.execute(f"""
            SELECT COLUMN_NAME, DATA_TYPE
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = ?
        """, table_name)
        columns = cursor.fetchall()

        # Sample data
        cursor.execute(f"""
            SELECT TOP {sample_size} *
            FROM {table_name}
            ORDER BY NEWID()
        """)
        rows = cursor.fetchall()

        findings = []
        for col_idx, (col_name, data_type) in enumerate(columns):
            if data_type not in ('varchar', 'nvarchar', 'char', 'text'):
                continue

            for row in rows:
                value = str(row[col_idx]) if row[col_idx] else ""
                results = self.analyzer.analyze(
                    text=value,
                    entities=[
                        "US_SSN",
                        "CREDIT_CARD",
                        "EMAIL_ADDRESS",
                        "PHONE_NUMBER",
                        "PERSON",
                        "LOCATION",
                        "MEDICAL_LICENSE",
                        "US_DRIVER_LICENSE"
                    ],
                    language="en"
                )

                for result in results:
                    findings.append({
                        "table": table_name,
                        "column": col_name,
                        "entity_type": result.entity_type,
                        "confidence": result.score,
                        "sample": self.redact(value, result)
                    })

        return self.aggregate_findings(findings)

    def scan_database(self, excluded_tables: list = None):
        """Scan entire database for PII/PHI"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_TYPE = 'BASE TABLE'
        """)
        tables = [row[0] for row in cursor.fetchall()]

        all_findings = {}
        for table in tables:
            if excluded_tables and table in excluded_tables:
                continue
            all_findings[table] = self.scan_table(table)

        return all_findings

    def generate_compliance_report(self, framework: str):
        """Generate framework-specific compliance report"""
        findings = self.scan_database()
        config_checks = self.check_configuration()
        access_checks = self.check_access_controls()

        return {
            "framework": framework,
            "generated_at": datetime.utcnow().isoformat(),
            "status": self.calculate_status(findings, config_checks, access_checks),
            "data_findings": findings,
            "config_findings": config_checks,
            "access_findings": access_checks,
            "remediation_priority": self.prioritize_remediation()
        }
```

## Evidence Collection

For auditors, SQL Compliance automatically collects:

```
Evidence Package for SOC 2 Audit

Generated: 2024-12-24
Period: 2024-01-01 to 2024-12-24

Contents:
├── CC6.1_Access_Controls/
│   ├── login_inventory.csv
│   ├── permission_matrix.csv
│   ├── role_memberships.csv
│   └── access_change_log.csv
│
├── CC6.2_Credential_Management/
│   ├── password_policy.json
│   ├── mfa_status.csv
│   └── service_accounts.csv
│
├── CC6.6_System_Boundaries/
│   ├── firewall_rules.csv
│   ├── network_config.json
│   └── encryption_status.csv
│
├── Audit_Logs/
│   ├── authentication_log.csv
│   ├── authorization_changes.csv
│   └── data_access_log.csv
│
└── Remediation_Tracking/
    ├── open_findings.csv
    ├── remediation_history.csv
    └── exception_approvals.csv
```

## API Endpoints

```
GET    /api/compliance/status             # Overall compliance status
GET    /api/compliance/status/{framework} # Framework-specific status

POST   /api/compliance/scan               # Run compliance scan
GET    /api/compliance/scan/{id}          # Get scan results

GET    /api/compliance/findings           # All findings
GET    /api/compliance/findings/{id}      # Specific finding
POST   /api/compliance/findings/{id}/remediate

GET    /api/compliance/evidence           # Evidence packages
POST   /api/compliance/evidence/generate  # Generate evidence package

GET    /api/compliance/reports            # Compliance reports
POST   /api/compliance/reports/generate   # Generate report
```

## CLI Commands

```bash
sql2ai compliance scan --framework soc2
sql2ai compliance scan --framework hipaa --include-data
sql2ai compliance scan --framework pci --tables Payments,Cards

sql2ai compliance status --framework all
sql2ai compliance findings --severity critical
sql2ai compliance remediate --finding F001

sql2ai compliance evidence --framework soc2 --period 2024
sql2ai compliance report --framework hipaa --format pdf
```

## Implementation Status

- [ ] Core library structure (libs/compliance-scanner - Python)
- [ ] Presidio integration
- [ ] Configuration checks
- [ ] Access control checks
- [ ] Data-level PII scanning
- [ ] SOC 2 control mappings
- [ ] HIPAA control mappings
- [ ] PCI-DSS control mappings
- [ ] GDPR control mappings
- [ ] FERPA control mappings
- [ ] Evidence collection
- [ ] Report generation
- [ ] Remediation tracking
- [ ] API routers
- [ ] CLI commands
