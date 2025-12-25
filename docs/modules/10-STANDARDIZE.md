# SQL Standardize

**Database Standards Enforcement Engine**

## Overview

SQL Standardize enforces consistent naming conventions, coding standards, structural patterns, and best practices across all SQL Server and PostgreSQL entities. It analyzes existing databases against configurable rule sets and provides automated remediation to bring databases into compliance.

## The Problem

### Common Standardization Issues

| Issue | Example | Impact |
|-------|---------|--------|
| Inconsistent naming | `tblCustomer`, `Customers`, `customer_data` | Confusion, maintenance burden |
| Mixed casing | `CustomerID`, `customerId`, `customer_id` | Query errors, join mistakes |
| No schema usage | All objects in `dbo` | Security, organization issues |
| Inconsistent prefixes | `sp_`, `usp_`, `proc_`, none | Discoverability problems |
| Table variables vs temp tables | Inconsistent usage | Performance variations |
| Views vs tables | Unclear data sources | Maintenance confusion |
| Function vs procedure | Wrong choice for use case | Performance, transaction issues |

## SQL Standardize Solution

### Configurable Rule Engine

```yaml
# .sql2ai/standards.yaml
naming:
  tables:
    pattern: "^[A-Z][a-zA-Z]+$"  # PascalCase
    plural: true                  # Customers, Orders
    prefixes:
      forbidden: ["tbl", "t_"]

  columns:
    pattern: "^[A-Z][a-zA-Z]+$"  # PascalCase
    primary_key: "{TableSingular}Id"  # CustomerId
    foreign_key: "{ReferencedTable}Id"

  stored_procedures:
    pattern: "^[A-Z][a-zA-Z]+_[A-Z][a-zA-Z]+$"  # Entity_Action
    examples: ["Customer_Create", "Order_GetById"]
    prefixes:
      forbidden: ["sp_"]  # Reserved for system

  functions:
    scalar_pattern: "^fn[A-Z][a-zA-Z]+$"  # fnCalculateTax
    table_pattern: "^tvf[A-Z][a-zA-Z]+$"  # tvfGetCustomerOrders

  views:
    pattern: "^vw[A-Z][a-zA-Z]+$"  # vwActiveCustomers

  indexes:
    clustered: "PK_{TableName}"
    nonclustered: "IX_{TableName}_{Columns}"
    unique: "UX_{TableName}_{Columns}"

coding:
  procedures:
    require_set_nocount: true
    require_error_handling: true
    require_transaction: "when_modifying"
    max_parameters: 15
    require_parameter_prefix: "@"

  formatting:
    keywords: "UPPERCASE"
    identifiers: "PascalCase"
    indent_size: 4
    max_line_length: 120

structure:
  normalization:
    minimum_form: "3NF"
    allow_denormalization: "with_comment"

  schemas:
    required: true
    default: "dbo"
    application_schemas: ["app", "api", "internal"]

  types:
    prefer_table_types: true
    prefer_temp_tables_over_variables: "for_large_datasets"
```

## Rule Categories

### 1. Naming Conventions

```
VIOLATION: Table 'tblCustomers' uses forbidden prefix 'tbl'
LOCATION:  dbo.tblCustomers
SEVERITY:  Warning
RULE:      naming.tables.prefixes.forbidden

SUGGESTED FIX:
  EXEC sp_rename 'dbo.tblCustomers', 'Customers';
  -- Update all references (47 found)
```

### 2. Coding Standards

```sql
-- VIOLATION: Missing SET NOCOUNT ON
CREATE PROCEDURE dbo.GetCustomer
    @CustomerId INT
AS
BEGIN
    SELECT * FROM Customers WHERE CustomerId = @CustomerId;
END;

-- COMPLIANT VERSION:
CREATE PROCEDURE dbo.Customer_GetById
    @CustomerId INT
AS
BEGIN
    SET NOCOUNT ON;

    SELECT CustomerId, CustomerName, Email, CreatedDate
    FROM dbo.Customers
    WHERE CustomerId = @CustomerId;
END;
```

### 3. Structural Standards

**View vs Table Analysis:**
```
FINDING: Table 'CustomerSummary' appears to be derived data
EVIDENCE:
  - No direct inserts in last 90 days
  - Only updated via scheduled job
  - Data derivable from Customers + Orders

RECOMMENDATION: Convert to indexed view
  CREATE VIEW dbo.vwCustomerSummary
  WITH SCHEMABINDING
  AS
  SELECT
      c.CustomerId,
      c.CustomerName,
      COUNT_BIG(*) AS OrderCount,
      SUM(o.Total) AS TotalSpent
  FROM dbo.Customers c
  JOIN dbo.Orders o ON c.CustomerId = o.CustomerId
  GROUP BY c.CustomerId, c.CustomerName;

  CREATE UNIQUE CLUSTERED INDEX IX_vwCustomerSummary
  ON dbo.vwCustomerSummary (CustomerId);
```

**Function vs Procedure Analysis:**
```
FINDING: Function 'fnUpdateCustomerStatus' performs DML
PROBLEM: Scalar functions cannot modify data
EVIDENCE: Contains UPDATE statement (line 15)

RECOMMENDATION: Convert to stored procedure
  - Rename to Customer_UpdateStatus
  - Change RETURNS to OUTPUT parameter
  - Update 12 calling procedures
```

### 4. Type Standards

**Table Variables vs Temp Tables:**
```
FINDING: Table variable @LargeDataset has 50,000+ rows
LOCATION: dbo.ProcessLargeOrders, line 34
PROBLEM: Table variables don't have statistics

RECOMMENDATION: Use temp table for large datasets
  -- Before
  DECLARE @Orders TABLE (OrderId INT, Total DECIMAL(18,2));
  INSERT INTO @Orders SELECT ...;  -- 50,000 rows

  -- After
  CREATE TABLE #Orders (OrderId INT, Total DECIMAL(18,2));
  INSERT INTO #Orders SELECT ...;
  CREATE INDEX IX_Orders ON #Orders (OrderId);
```

### 5. Normalization Analysis

```
FINDING: Denormalization detected in dbo.Orders
COLUMNS: CustomerName, CustomerEmail (duplicated from Customers)
SEVERITY: Warning (3NF violation)

OPTIONS:
  1. Remove duplicate columns (recommended)
     - Update 23 queries to JOIN Customers
     - Saves 2.4GB storage

  2. Add computed column
     - Maintain for read performance
     - Add trigger for sync

  3. Accept with documentation
     - Add comment explaining rationale
     - Mark as intentional denormalization
```

## Analysis Report

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL STANDARDIZE ANALYSIS REPORT                     ║
║              Database: ProductionDB                              ║
║              Standard: enterprise-strict.yaml                    ║
╠══════════════════════════════════════════════════════════════════╣
║ COMPLIANCE SCORE: 67/100                                         ║
╠══════════════════════════════════════════════════════════════════╣
║ FINDINGS BY CATEGORY                                             ║
║ ─────────────────────────────────────────────────────────────── ║
║ Naming Conventions:        43 violations (12 critical)           ║
║ Coding Standards:          28 violations (5 critical)            ║
║ Structural Issues:         15 findings (3 critical)              ║
║ Type Usage:                 8 findings (1 critical)              ║
║ Normalization:              4 findings (0 critical)              ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP ISSUES                                                       ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. 23 tables using 'tbl' prefix                                  ║
║ 2. 18 procedures missing error handling                          ║
║ 3. 12 procedures using 'sp_' prefix                              ║
║ 4. 8 functions performing DML (should be procedures)             ║
║ 5. 5 large table variables (should be temp tables)               ║
╠══════════════════════════════════════════════════════════════════╣
║ AUTO-FIX AVAILABLE                                               ║
║ ─────────────────────────────────────────────────────────────── ║
║ 71 violations can be auto-fixed                                  ║
║ Run: sql2ai standardize fix --auto                               ║
╚══════════════════════════════════════════════════════════════════╝
```

## Pre-built Standards

### Enterprise Standard
```yaml
# Strict naming, full documentation, comprehensive error handling
extends: sql2ai/enterprise
strictness: high
```

### Startup Standard
```yaml
# Pragmatic naming, essential documentation
extends: sql2ai/startup
strictness: medium
```

### Legacy Modernization
```yaml
# Gradual improvement, backward compatibility
extends: sql2ai/legacy-compat
strictness: low
auto_fix: naming_only
```

## CLI Commands

```bash
# Analyze database against standards
sql2ai standardize analyze --connection "..." --standard enterprise

# Generate fix scripts
sql2ai standardize fix --output ./fixes --dry-run

# Apply fixes automatically
sql2ai standardize fix --auto --backup

# Check specific categories
sql2ai standardize check naming
sql2ai standardize check coding
sql2ai standardize check structure

# Generate compliance report
sql2ai standardize report --format html --output compliance.html
```

## Integration Points

- **SQL Code**: Review standards violations in code review
- **SQL Migrator**: Apply standards to generated migrations
- **SQL Version**: Track standards compliance over time
- **SQL Orchestrator**: Schedule regular compliance scans
