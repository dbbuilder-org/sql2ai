# SQL Anonymize

**Secure Data Clean Room Platform**

## Overview

SQL Anonymize consolidates data from private sources into secure "clean room" environments where developers can work with realistic data that bears no qualifiable or quantifiable resemblance to the source. It enables code development, testing, and analysis with production-like data while maintaining complete privacy.

## The Problem

### Current Data Privacy Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Dev/Test Data | Masked production copy | Re-identification possible |
| Data Sharing | Manual anonymization | Inconsistent, error-prone |
| Analytics | Aggregate only | Limited usefulness |
| ML Training | Synthetic or nothing | Poor model quality |
| Compliance | Delete sensitive fields | Unrealistic test scenarios |

## SQL Anonymize Solution

### Clean Room Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION ENVIRONMENT                        │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│    │ CustomerDB  │  │  OrdersDB   │  │  HealthDB   │            │
│    │ (PII/PHI)   │  │ (Financial) │  │   (HIPAA)   │            │
│    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
└───────────┼────────────────┼────────────────┼───────────────────┘
            │                │                │
            ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL ANONYMIZE ENGINE                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Extract        - Pull data with referential integrity  │ │
│  │  2. Analyze        - Detect PII/PHI automatically          │ │
│  │  3. Transform      - Apply anonymization strategies        │ │
│  │  4. Validate       - Ensure no re-identification possible  │ │
│  │  5. Load           - Populate clean room                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
            │                │                │
            ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CLEAN ROOM ENVIRONMENT                        │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│    │ CustomerDB  │  │  OrdersDB   │  │  HealthDB   │            │
│    │ (Anonymized)│  │ (Anonymized)│  │ (Anonymized)│            │
│    └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
│    ✓ No PII/PHI    ✓ Realistic patterns   ✓ Full FK integrity   │
└─────────────────────────────────────────────────────────────────┘
```

## Anonymization Strategies

### 1. Name Anonymization

```yaml
columns:
  FirstName:
    strategy: fake_name
    locale: en_US
    consistency: email  # Same person gets same fake name

  LastName:
    strategy: fake_name
    type: last_name
    consistency: email

  FullName:
    strategy: computed
    formula: "{FirstName} {LastName}"
```

**Before → After:**
```
John Smith      →  Marcus Johnson
Jane Doe        →  Sarah Williams
Robert Johnson  →  David Chen
```

### 2. Email Anonymization

```yaml
columns:
  Email:
    strategy: email_hash
    domain: "@example.anonymized.com"
    preserve_format: true

  # OR
  Email:
    strategy: fake_email
    consistency: customer_id
```

**Before → After:**
```
john.smith@gmail.com    →  user_7f3d2a@example.anonymized.com
jane.doe@company.com    →  user_a2b4c1@example.anonymized.com
```

### 3. Address Anonymization

```yaml
columns:
  StreetAddress:
    strategy: fake_address
    preserve_format: true

  City:
    strategy: fake_city
    same_state: true  # Keep geographic distribution

  ZipCode:
    strategy: generalize
    precision: 3  # 12345 → 123XX
```

**Before → After:**
```
123 Main Street, Boston, MA 02101
→ 456 Oak Avenue, Cambridge, MA 021XX
```

### 4. Financial Data Anonymization

```yaml
columns:
  CreditCardNumber:
    strategy: tokenize
    preserve_last_4: true
    preserve_type: true  # Visa stays Visa

  AccountNumber:
    strategy: hash_consistent
    salt: $SECRET

  TransactionAmount:
    strategy: noise
    variance: 0.1  # ±10% random adjustment
    preserve_sum: true  # Aggregate totals unchanged
```

**Before → After:**
```
4532-1234-5678-9012  →  4532-XXXX-XXXX-9012
$1,234.56            →  $1,198.23 (within 10%)
```

### 5. Date Anonymization

```yaml
columns:
  DateOfBirth:
    strategy: shift
    range_days: 30  # ±30 days random shift
    preserve_age_bracket: true  # 25-34 stays 25-34

  AppointmentDate:
    strategy: shift
    consistent_shift: patient_id  # Same shift per patient
```

### 6. Free Text Anonymization

```yaml
columns:
  Notes:
    strategy: nlp_redact
    entities: [PERSON, PHONE, EMAIL, SSN, ADDRESS]
    replacement: "[REDACTED]"

  # OR
  Notes:
    strategy: nlp_replace
    entities: [PERSON]
    with: fake_name
```

**Before → After:**
```
"Patient John Smith called from 555-123-4567
about prescription refill. Lives at 123 Main St."

→ "Patient [PERSON] called from [PHONE]
about prescription refill. Lives at [ADDRESS]."

# OR with replacement:
→ "Patient Marcus Johnson called from 555-987-6543
about prescription refill. Lives at 456 Oak Ave."
```

## Consistency & Referential Integrity

### Cross-Table Consistency

```yaml
consistency_groups:
  customer_identity:
    key: CustomerId
    columns:
      - table: Customers, column: FirstName
      - table: Customers, column: LastName
      - table: Customers, column: Email
      - table: Orders, column: CustomerEmail
      - table: Support, column: ContactName

# Same customer gets same fake identity everywhere
```

### Foreign Key Preservation

```yaml
referential_integrity:
  mode: preserve  # All FKs maintained

  orphan_handling:
    strategy: create_fake_parent
    # If child references non-existent parent, create one
```

## Re-Identification Prevention

### K-Anonymity Validation

```yaml
validation:
  k_anonymity:
    k: 5  # Each record indistinguishable from 4 others
    quasi_identifiers: [Age, ZipCode, Gender]

  l_diversity:
    l: 3
    sensitive_attribute: Diagnosis

  differential_privacy:
    epsilon: 0.1
    apply_to: [aggregate_queries]
```

### Uniqueness Detection

```
╔══════════════════════════════════════════════════════════════════╗
║              RE-IDENTIFICATION RISK ANALYSIS                     ║
╠══════════════════════════════════════════════════════════════════╣
║ UNIQUE VALUE DETECTION                                           ║
║ ─────────────────────────────────────────────────────────────── ║
║ ⚠ Phone column has 99.2% unique values                          ║
║   Risk: High re-identification potential                         ║
║   Recommendation: Use consistent fake phones or tokenize         ║
║                                                                  ║
║ ⚠ Combination (ZipCode, BirthYear, Gender) is unique for 23%    ║
║   Risk: Quasi-identifier re-identification                       ║
║   Recommendation: Generalize ZipCode to 3-digit                  ║
╠══════════════════════════════════════════════════════════════════╣
║ K-ANONYMITY CHECK                                                ║
║ ─────────────────────────────────────────────────────────────── ║
║ Current K-value: 3 (target: 5)                                   ║
║ Records below threshold: 1,247                                   ║
║ Recommendation: Apply additional generalization                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## Clean Room Access Control

```yaml
clean_room:
  name: "dev-testing"

  access:
    developers:
      - team: engineering
        permissions: [SELECT, INSERT, UPDATE, DELETE]

    analysts:
      - team: data-science
        permissions: [SELECT]

  data_export:
    allowed: false  # No bulk export
    audit: true

  session_timeout: 8h

  watermarking:
    enabled: true  # Track data origin
```

## CLI Commands

```bash
# Analyze source for PII/PHI
sql2ai anonymize analyze --source "..."

# Generate anonymization config
sql2ai anonymize init --template hipaa

# Run anonymization
sql2ai anonymize run --config anon.yaml --target clean-room

# Validate anonymization quality
sql2ai anonymize validate --check k-anonymity --k 5

# Refresh clean room with new data
sql2ai anonymize refresh --incremental
```

## Configuration Example

```yaml
# sql2ai-anonymize.yaml
source:
  connection: "sqlserver://prod/HealthcareDB"

target:
  connection: "postgresql://clean-room/HealthcareDB"

tables:
  Patients:
    columns:
      PatientId: preserve  # Keep for FK
      FirstName: fake_name
      LastName: fake_name
      SSN: redact
      DateOfBirth: shift(30)
      Email: fake_email
      Phone: fake_phone
      Address: fake_address

  Diagnoses:
    columns:
      DiagnosisId: preserve
      PatientId: preserve  # FK maintained
      DiagnosisCode: preserve  # Medical codes kept
      DiagnosisDate: shift(30, consistent: PatientId)
      Notes: nlp_redact

  Prescriptions:
    columns:
      MedicationName: preserve  # Drug names kept
      Dosage: preserve
      PrescribingDoctor: fake_name(consistent: DoctorId)
```

## Integration Points

- **SQL Comply**: Validate HIPAA/GDPR compliance
- **SQL Simulate**: Generate additional synthetic data
- **SQL Test**: Use anonymized data for testing
- **SQL Centralize**: Distribute anonymized data to teams
