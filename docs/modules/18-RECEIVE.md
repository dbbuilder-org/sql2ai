# SQL Receive

**Secure Inbound Data Gateway**

## Overview

SQL Receive provides unified readers for files, APIs, and emails, ingesting data into a common endpoint with comprehensive security validation. All inbound data is checked for viral/malware content, integrity issues, data leaks, SQL injection attempts, and other threats before being processed.

## The Problem

### Current Inbound Data Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Malware in files | Separate antivirus | Inconsistent scanning |
| SQL injection | Ad-hoc validation | Database compromise |
| Data leaks | No inbound PII check | Compliance violations |
| Multiple sources | Separate integrations | Fragmented security |
| File integrity | Trust-based | Corrupted data |
| Email parsing | Custom code | Inconsistent handling |

## SQL Receive Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INBOUND SOURCES                               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌───────────┐ │
│  │   Files     │ │    APIs     │ │   Emails    │ │  Webhooks │ │
│  │  (SFTP/S3)  │ │  (REST/WS)  │ │ (IMAP/POP)  │ │  (HTTP)   │ │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └─────┬─────┘ │
└─────────┼───────────────┼───────────────┼───────────────┼───────┘
          │               │               │               │
          ▼               ▼               ▼               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL RECEIVE GATEWAY                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    SECURITY PIPELINE                        │ │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │ │
│  │  │ Malware │ │ Integr- │ │  Data   │ │   SQL   │          │ │
│  │  │  Scan   │→│  ity    │→│  Leak   │→│Injection│          │ │
│  │  │         │ │  Check  │ │  Detect │ │  Check  │          │ │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    PROCESSING PIPELINE                      │ │
│  │  Parse → Validate → Transform → Stage → Process             │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE / DATA LAKE                          │
│    Validated, sanitized, and audited inbound data                │
└─────────────────────────────────────────────────────────────────┘
```

## Security Checks

### 1. Malware & Virus Scanning

```yaml
malware_scanning:
  enabled: true
  providers:
    - type: clamav
      endpoint: http://clamav:3310

    - type: windows_defender
      enabled: ${IS_WINDOWS}

    - type: virustotal
      api_key: ${VT_API_KEY}
      for_files_larger_than: 10MB

  actions:
    on_threat:
      quarantine: true
      alert: security_team
      reject: true
```

**Scan Report:**
```
╔══════════════════════════════════════════════════════════════════╗
║ 🔴 MALWARE DETECTED                                              ║
╠══════════════════════════════════════════════════════════════════╣
║ File: invoice_2024.xlsx                                          ║
║ Source: SFTP upload from vendor@partner.com                      ║
║ Threat: Trojan.MSOffice.Agent.gen                                ║
║ Detection: ClamAV, VirusTotal (47/72 engines)                    ║
║                                                                  ║
║ ACTION TAKEN:                                                    ║
║ ├── File quarantined                                             ║
║ ├── Source IP blocked temporarily                                ║
║ ├── Security team notified                                       ║
║ └── Audit log created                                            ║
╚══════════════════════════════════════════════════════════════════╝
```

### 2. File Integrity Validation

```yaml
integrity_checks:
  enabled: true

  checksums:
    verify: true
    algorithms: [SHA-256, MD5]  # Accept either
    source: header  # Or companion .sha256 file

  file_structure:
    validate_headers: true
    check_magic_bytes: true
    detect_file_type_mismatch: true  # .exe renamed to .xlsx

  size_limits:
    max_file_size: 100MB
    max_total_batch: 1GB

  format_validation:
    csv:
      delimiter_detection: true
      quote_handling: strict
      encoding: [UTF-8, UTF-16, ISO-8859-1]

    json:
      schema_validation: true
      max_depth: 10

    xml:
      dtd_validation: optional
      xxe_prevention: true  # Block XML External Entity attacks
```

### 3. Data Leak / PII Detection

```yaml
data_leak_prevention:
  enabled: true
  scan_content: true

  sensitive_data:
    - type: CREDIT_CARD
      action: reject
      message: "Credit card data not allowed in this channel"

    - type: US_SSN
      action: flag
      requires_approval: true

    - type: EMAIL_ADDRESS
      action: log  # Allow but log

  patterns:
    - name: internal_document_id
      regex: "INTERNAL-[A-Z]{3}-[0-9]{6}"
      action: flag
      message: "Internal document reference detected"
```

### 4. SQL Injection Prevention

```yaml
sql_injection_prevention:
  enabled: true
  scan_all_text_fields: true

  patterns:
    - "'.*--"
    - "'; DROP"
    - "1=1"
    - "UNION SELECT"
    - "xp_cmdshell"
    - "EXEC sp_"

  actions:
    on_detection:
      reject: true
      alert: true
      log_payload: true  # For forensics

  safe_processing:
    parameterize_all_queries: true
    escape_special_characters: true
```

**Detection Example:**
```
╔══════════════════════════════════════════════════════════════════╗
║ 🔴 SQL INJECTION ATTEMPT BLOCKED                                 ║
╠══════════════════════════════════════════════════════════════════╣
║ Source: API /api/import/customers                                ║
║ Client IP: 203.0.113.42                                          ║
║ User Agent: Python/3.9                                           ║
║                                                                  ║
║ Detected Payload:                                                ║
║ {                                                                ║
║   "customer_name": "John'; DROP TABLE Customers; --",            ║
║   "email": "john@example.com"                                    ║
║ }                                                                ║
║                                                                  ║
║ Pattern Matched: "'; DROP"                                       ║
║ Confidence: 99.8%                                                ║
║                                                                  ║
║ ACTION: Request rejected, IP flagged for monitoring              ║
╚══════════════════════════════════════════════════════════════════╝
```

## Inbound Channels

### File Sources

```yaml
file_sources:
  sftp:
    - name: vendor_uploads
      host: sftp.vendor.com
      path: /outgoing/*.csv
      schedule: "*/15 * * * *"  # Every 15 minutes
      archive_after_processing: true

  s3:
    - name: partner_data
      bucket: partner-data-bucket
      prefix: incoming/
      event_driven: true  # S3 event notifications

  azure_blob:
    - name: customer_files
      container: imports
      connection_string: ${AZURE_STORAGE}

  local:
    - name: file_drop
      path: /data/incoming/
      watch: true
```

### API Sources

```yaml
api_sources:
  rest:
    - name: crm_sync
      url: https://api.crm.com/contacts
      method: GET
      schedule: "0 * * * *"  # Hourly
      authentication:
        type: oauth2
        client_id: ${CRM_CLIENT_ID}
        client_secret: ${CRM_CLIENT_SECRET}

  webhooks:
    - name: payment_notifications
      path: /webhooks/payments
      validation:
        signature_header: X-Signature
        secret: ${WEBHOOK_SECRET}

  graphql:
    - name: inventory_updates
      url: https://api.supplier.com/graphql
      query_file: queries/inventory.graphql
```

### Email Sources

```yaml
email_sources:
  imap:
    - name: orders_inbox
      server: imap.company.com
      mailbox: orders@company.com
      folder: INBOX
      schedule: "*/5 * * * *"
      processing:
        extract_attachments: true
        parse_body: true
        attachment_types: [.csv, .xlsx, .pdf]
```

## Processing Pipeline

```yaml
processing:
  stages:
    - name: parse
      handlers:
        csv: sql2ai.parsers.CsvParser
        json: sql2ai.parsers.JsonParser
        xml: sql2ai.parsers.XmlParser
        xlsx: sql2ai.parsers.ExcelParser
        email: sql2ai.parsers.EmailParser

    - name: validate
      schema_registry: ./schemas/
      fail_fast: false  # Collect all errors

    - name: transform
      mappings_file: ./mappings/
      custom_transforms: ./transforms/

    - name: stage
      table: sql2ai.InboundStaging
      deduplicate: true
      dedup_key: [source, external_id]

    - name: process
      stored_procedure: dbo.ProcessInboundData
      batch_size: 1000
```

## Staging & Processing

```sql
-- Staging table structure
CREATE TABLE sql2ai.InboundStaging (
    StagingId BIGINT IDENTITY PRIMARY KEY,
    Source NVARCHAR(100),
    SourceFile NVARCHAR(500),
    ExternalId NVARCHAR(200),
    ReceivedAt DATETIME2 DEFAULT GETUTCDATE(),
    Status NVARCHAR(20) DEFAULT 'pending',
    Payload NVARCHAR(MAX),  -- JSON
    ValidationErrors NVARCHAR(MAX),  -- JSON array
    ProcessedAt DATETIME2,
    ProcessedBy NVARCHAR(100)
);

-- Processing example
CREATE PROCEDURE dbo.ProcessInboundData
AS
BEGIN
    -- Process validated staging records
    INSERT INTO Customers (ExternalId, Name, Email)
    SELECT
        JSON_VALUE(Payload, '$.external_id'),
        JSON_VALUE(Payload, '$.name'),
        JSON_VALUE(Payload, '$.email')
    FROM sql2ai.InboundStaging
    WHERE Status = 'validated'
      AND ProcessedAt IS NULL;

    -- Update staging status
    UPDATE sql2ai.InboundStaging
    SET Status = 'processed',
        ProcessedAt = GETUTCDATE()
    WHERE Status = 'validated'
      AND ProcessedAt IS NULL;
END;
```

## Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║                    SQL RECEIVE DASHBOARD                         ║
╠══════════════════════════════════════════════════════════════════╣
║ INBOUND ACTIVITY (Today)                                         ║
║ ─────────────────────────────────────────────────────────────── ║
║ Files Received:     247   │ API Calls:          4,721            ║
║ Emails Processed:   89    │ Webhooks:           1,204            ║
╠══════════════════════════════════════════════════════════════════╣
║ SECURITY STATUS                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ Malware Scanned:    6,261                                      ║
║ 🔴 Threats Blocked:   3                                          ║
║ 🟡 PII Flagged:       47 (pending review)                        ║
║ 🔴 SQL Injection:     12 attempts blocked                        ║
╠══════════════════════════════════════════════════════════════════╣
║ PROCESSING PIPELINE                                              ║
║ ─────────────────────────────────────────────────────────────── ║
║ Staging Queue:      156   │ Processing:         23               ║
║ Validated:          4,892 │ Failed Validation:  67               ║
║ Processed Today:    4,721 │ Error Rate:         1.4%             ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Initialize receivers
sql2ai receive init --config receive.yaml

# Test file source
sql2ai receive test --source vendor_uploads

# Process pending files
sql2ai receive process --source all

# View staging status
sql2ai receive status

# Retry failed items
sql2ai receive retry --status failed
```

## Integration Points

- **SQL Audit**: Log all inbound data activity
- **SQL Comply**: Ensure data handling compliance
- **SQL Orchestrate**: Schedule processing jobs
- **SQL Monitor**: Dashboard for inbound metrics
