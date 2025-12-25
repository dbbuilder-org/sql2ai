# SQL Code Review

**Module 4 of 8** | **Status:** Planned | **Priority:** P1

## Overview

SQL Code Review provides automated code review, AI-powered data dictionary generation ("Swagger for Databases"), and release notes automation. It documents your database with the same rigor as modern API documentation.

## Problems Solved

| Problem | Current State | SQL Code Review Solution |
|---------|---------------|--------------------------|
| No SQL code review | Manual eyeballing | Automated analysis |
| Outdated documentation | Stale Word docs | Auto-generated, always current |
| Missing column descriptions | "What is col_x?" | AI-inferred descriptions |
| Manual release notes | Copy-paste chaos | Auto-generated from changes |
| No API-style DB docs | Scattered knowledge | Swagger-like documentation |

## Features

### 1. Automated Code Review

When SQL code changes, automatic analysis detects:

**Security Issues**
- SQL injection vulnerabilities
- Excessive permissions
- Hardcoded credentials
- Missing encryption

**Performance Issues**
- Table scans without indexes
- Cursor usage (suggest set-based)
- Implicit conversions
- Missing NOCOUNT
- SELECT *

**Best Practices**
- Naming conventions
- Error handling patterns
- Transaction management
- Parameter validation
- Schema qualification

### 2. AI Data Dictionary

Like Swagger/OpenAPI for your database:

```yaml
# Auto-generated data dictionary
# SQL2.AI Code Review v1.0

database: OrderManagement
description: "Core e-commerce order processing database"
generated: 2024-12-24T10:30:00Z

tables:
  Customers:
    description: "Customer master records for billing, shipping, and CRM"
    row_count: 1,247,832
    size_mb: 342.5
    columns:
      CustomerID:
        type: int
        nullable: false
        primary_key: true
        description: "Unique customer identifier, auto-incremented"
        pii: false

      Email:
        type: nvarchar(255)
        nullable: false
        description: "Primary email for order confirmations and marketing"
        pii: true
        gdpr_category: contact_info
        examples: ["user@example.com"]

      LoyaltyTier:
        type: nvarchar(50)
        nullable: true
        description: "Customer loyalty program tier"
        allowed_values: ["Bronze", "Silver", "Gold", "Platinum"]
        default: "Bronze"

    relationships:
      - target: Orders
        type: one_to_many
        foreign_key: CustomerID

    indexes:
      - name: IX_Customers_Email
        columns: [Email]
        unique: true
        description: "Ensures email uniqueness for login"

procedures:
  sp_ProcessOrder:
    description: "Processes a new order with inventory check and payment"
    parameters:
      - name: "@OrderID"
        type: int
        direction: input
        description: "Order to process"
      - name: "@Success"
        type: bit
        direction: output
        description: "Returns 1 on success, 0 on failure"
    returns: "Result set of order details"
    side_effects:
      - "Updates Inventory table"
      - "Inserts into PaymentLog"
    example: |
      DECLARE @Result BIT;
      EXEC sp_ProcessOrder @OrderID = 12345, @Success = @Result OUTPUT;
```

### 3. Interactive Documentation Portal

Web-based documentation explorer:

```
┌─────────────────────────────────────────────────────────────┐
│  OrderManagement Database Documentation                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Search: [________________] [🔍]                            │
│                                                              │
│  ┌──────────────┐  ┌─────────────────────────────────────┐  │
│  │ Tables       │  │ Customers                           │  │
│  │ ├─ Customers │  │                                     │  │
│  │ ├─ Orders    │  │ Customer master records for         │  │
│  │ ├─ Products  │  │ billing, shipping, and CRM          │  │
│  │ └─ ...       │  │                                     │  │
│  │              │  │ Columns:                            │  │
│  │ Views        │  │ ┌────────────┬──────────┬────────┐  │  │
│  │ ├─ vw_Active │  │ │ Name       │ Type     │ PII    │  │  │
│  │ └─ ...       │  │ ├────────────┼──────────┼────────┤  │  │
│  │              │  │ │ CustomerID │ int      │ No     │  │  │
│  │ Procedures   │  │ │ Email      │ nvarchar │ Yes    │  │  │
│  │ └─ ...       │  │ │ Name       │ nvarchar │ Yes    │  │  │
│  └──────────────┘  │ └────────────┴──────────┴────────┘  │  │
│                    │                                     │  │
│                    │ [View Schema] [View Data Sample]    │  │
│                    └─────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4. Release Notes Generation

Automatic release notes from migrations:

```markdown
# Release Notes - v2.4.0
Generated: 2024-12-24

## Breaking Changes
- `Orders.Status` column expanded from NVARCHAR(20) to NVARCHAR(50)
  - **Impact**: Applications reading this column may need updates
  - **Migration**: Automatic, no data loss

## New Features
- Added `Customers.LoyaltyTier` column for loyalty program
- New procedure `sp_CalculateLoyaltyPoints`
- New view `vw_CustomerLoyaltySummary`

## Improvements
- `sp_ProcessOrder` now handles international tax rates
- Added index `IX_Orders_CustomerID_Date` for reporting queries

## Bug Fixes
- Fixed null handling in `fn_CalculateTax`

## Performance
- Query time for order history reduced by 65%
- New covering index eliminates key lookups

## Security
- Removed hardcoded connection string from `sp_SyncInventory`
- Added parameter validation to prevent injection
```

## Code Review Rules

### Built-in Rules

```yaml
rules:
  security:
    - id: SEC001
      name: "SQL Injection Risk"
      severity: critical
      pattern: "EXEC.*\\+.*@"
      message: "Dynamic SQL with string concatenation detected"

    - id: SEC002
      name: "Hardcoded Password"
      severity: critical
      pattern: "password\\s*=\\s*['\"][^'\"]+['\"]"

  performance:
    - id: PERF001
      name: "Missing NOCOUNT"
      severity: warning
      pattern: "CREATE PROC.*BEGIN(?!.*SET NOCOUNT)"
      message: "SET NOCOUNT ON recommended for procedures"

    - id: PERF002
      name: "SELECT * Usage"
      severity: info
      pattern: "SELECT\\s+\\*"
      message: "Specify column names for better performance"

  style:
    - id: STYLE001
      name: "Naming Convention"
      severity: info
      pattern: "CREATE TABLE (?!dbo\\.)"
      message: "Always specify schema (dbo.TableName)"
```

### Custom Rules

```yaml
# custom-rules.yaml
rules:
  custom:
    - id: CUSTOM001
      name: "Audit Logging Required"
      severity: error
      applies_to: procedures
      condition: "modifies_table('Customers') AND NOT inserts_to('AuditLog')"
      message: "Procedures modifying Customers must log to AuditLog"
```

## AI Features

### Column Description Inference

Using LLM to infer descriptions:

```
Input: Column "cust_dob" (DATE, nullable)
Context: Table "Customers" with columns: cust_id, cust_name, cust_email, cust_dob

AI Output: "Customer date of birth, used for age verification and birthday promotions"
```

### PII Detection

```
Column: "phone_number" (nvarchar(20))
AI Analysis:
  - Classification: PII
  - GDPR Category: Contact Information
  - Recommendation: Consider encryption at rest
  - Compliance: Requires consent for marketing use
```

## API Endpoints

```
POST   /api/code-review/analyze         # Analyze SQL code
GET    /api/code-review/rules           # List rules
POST   /api/code-review/rules           # Add custom rule

GET    /api/docs/dictionary             # Get data dictionary
GET    /api/docs/dictionary/{table}     # Get table documentation
POST   /api/docs/generate               # Generate documentation
GET    /api/docs/export                 # Export (markdown, html, openapi)

POST   /api/releases/generate           # Generate release notes
GET    /api/releases                    # List releases
GET    /api/releases/{version}          # Get specific release
```

## CLI Commands

```bash
sql2ai review analyze --file migration.sql
sql2ai review analyze --directory ./procedures
sql2ai review report --format html

sql2ai docs generate --connection "..."
sql2ai docs export --format openapi
sql2ai docs serve --port 3000

sql2ai release generate --from v2.3 --to v2.4
sql2ai release publish --version v2.4.0
```

## Implementation Status

- [ ] Core library structure (libs/code-review)
- [ ] Rule engine
- [ ] Built-in security rules
- [ ] Built-in performance rules
- [ ] Built-in style rules
- [ ] Custom rule support
- [ ] AI column description inference
- [ ] AI PII detection
- [ ] Data dictionary generator
- [ ] Documentation portal
- [ ] Release notes generator
- [ ] API routers
- [ ] CLI commands
