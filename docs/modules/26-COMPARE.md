# SQL Compare

**AI-Powered Schema Comparison and Sync Script Generation**

## Overview

SQL Compare provides intelligent, hands-off comparison between databases with automatic generation of modular, implementable sync scripts. It uses AI to understand semantic differences and generates deployment-ready scripts that can be easily reviewed, tested, and executed.

## The Problem

### Current Comparison Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Manual comparison | Side-by-side inspection | Missed differences |
| Monolithic scripts | One giant deployment file | Impossible to debug |
| No dependency order | Manual ordering | Deployment failures |
| Text-only diff | Can't detect refactoring | False positives |
| No rollback | Hope it works | Stuck if it fails |
| Environment mixing | Same script everywhere | Dev objects in prod |

## SQL Compare Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL COMPARE                                   │
│                                                                  │
│  ┌──────────────────┐         ┌──────────────────┐              │
│  │  SOURCE DATABASE │         │  TARGET DATABASE │              │
│  │  (Dev/Staging)   │         │  (Prod/Target)   │              │
│  └────────┬─────────┘         └────────┬─────────┘              │
│           │                            │                         │
│           ▼                            ▼                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    SCHEMA EXTRACTION                         ││
│  │  • Tables, Views, Procedures, Functions, Triggers           ││
│  │  • Indexes, Constraints, Permissions                        ││
│  │  • Dependencies and relationships                           ││
│  └─────────────────────────────────────────────────────────────┘│
│           │                            │                         │
│           ▼                            ▼                         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    AI COMPARISON ENGINE                      ││
│  │  • Semantic diff (not just text)                            ││
│  │  • Detect refactoring and renames                           ││
│  │  • Understand intent of changes                             ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    SCRIPT GENERATOR                          ││
│  │  • Modular individual scripts                               ││
│  │  • Dependency-ordered deployment                            ││
│  │  • Automatic rollback generation                            ││
│  └─────────────────────────────────────────────────────────────┘│
│                          │                                       │
│                          ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    OUTPUT                                    ││
│  │  📁 sync-scripts/                                            ││
│  │  ├── 01-tables/                                              ││
│  │  ├── 02-views/                                               ││
│  │  ├── 03-procedures/                                          ││
│  │  ├── 04-rollback/                                            ││
│  │  └── 00-deploy-all.sql                                       ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Comparison Output

### Summary Report

```
╔══════════════════════════════════════════════════════════════════╗
║                    SQL COMPARE RESULTS                            ║
╠══════════════════════════════════════════════════════════════════╣
║  Source: dev-database @ server-01                                 ║
║  Target: prod-database @ server-02                               ║
║  Compared: 2024-12-25 10:30:45                                    ║
║  Duration: 4.2 seconds                                            ║
╠══════════════════════════════════════════════════════════════════╣
║ OBJECT TYPE        │ NEW    │ MODIFIED │ DELETED │ IDENTICAL    ║
╠════════════════════╪════════╪══════════╪═════════╪══════════════╣
║ Tables             │   3    │    2     │    0    │     45       ║
║ Views              │   1    │    1     │    0    │     12       ║
║ Stored Procedures  │   5    │    8     │    1    │     67       ║
║ Functions          │   0    │    2     │    0    │     15       ║
║ Triggers           │   0    │    0     │    0    │      8       ║
║ Indexes            │   4    │    0     │    2    │    112       ║
║ Constraints        │   2    │    0     │    0    │     89       ║
╠══════════════════════════════════════════════════════════════════╣
║ TOTAL CHANGES: 28                                                 ║
║ ESTIMATED DEPLOYMENT TIME: 2-3 minutes                           ║
╚══════════════════════════════════════════════════════════════════╝
```

### Modular Script Structure

```
sync-scripts/
├── 00-deploy-all.sql              # Master deployment orchestrator
├── 00-rollback-all.sql            # Master rollback orchestrator
├── 01-tables/
│   ├── 01-create-CustomerPreferences.sql
│   ├── 01-rollback-CustomerPreferences.sql
│   ├── 02-create-OrderAuditLog.sql
│   ├── 02-rollback-OrderAuditLog.sql
│   ├── 03-alter-Orders-add-tracking.sql
│   └── 03-rollback-Orders-add-tracking.sql
├── 02-views/
│   ├── 01-create-vw_CustomerOrders.sql
│   └── 01-rollback-vw_CustomerOrders.sql
├── 03-procedures/
│   ├── 01-create-sp_ProcessRefund.sql
│   ├── 01-rollback-sp_ProcessRefund.sql
│   ├── 02-alter-sp_GetCustomerOrders.sql
│   └── 02-rollback-sp_GetCustomerOrders.sql
├── 04-functions/
│   └── ...
├── 05-indexes/
│   └── ...
└── deployment-report.html          # Visual comparison report
```

### Individual Script Example

```sql
-- ═══════════════════════════════════════════════════════════════════
-- SQL Compare Generated Script
-- ═══════════════════════════════════════════════════════════════════
-- Object:      dbo.sp_GetCustomerOrders
-- Change Type: MODIFY
-- Source:      dev-database
-- Target:      prod-database
-- Generated:   2024-12-25 10:30:45
-- ═══════════════════════════════════════════════════════════════════

-- Pre-deployment validation
IF NOT EXISTS (SELECT 1 FROM sys.objects WHERE name = 'sp_GetCustomerOrders')
BEGIN
    RAISERROR('Object sp_GetCustomerOrders does not exist in target', 16, 1);
    RETURN;
END

-- Backup existing definition
EXEC sp_rename 'dbo.sp_GetCustomerOrders', 'sp_GetCustomerOrders_backup_20241225';
GO

-- Deploy new version
CREATE OR ALTER PROCEDURE dbo.sp_GetCustomerOrders
    @CustomerId INT,
    @StartDate DATE = NULL,
    @IncludeReturns BIT = 0  -- NEW PARAMETER
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        o.OrderId,
        o.OrderDate,
        o.Total,
        o.Status,
        o.TrackingNumber,  -- NEW COLUMN
        CASE WHEN r.ReturnId IS NOT NULL THEN 1 ELSE 0 END AS HasReturn
    FROM Orders o
    LEFT JOIN Returns r ON o.OrderId = r.OrderId  -- NEW JOIN
        AND @IncludeReturns = 1
    WHERE o.CustomerId = @CustomerId
        AND (@StartDate IS NULL OR o.OrderDate >= @StartDate)
    ORDER BY o.OrderDate DESC;
END
GO

-- Post-deployment validation
DECLARE @error INT = 0;
EXEC @error = sp_GetCustomerOrders @CustomerId = 1;
IF @error <> 0
BEGIN
    RAISERROR('Post-deployment validation failed', 16, 1);
    -- Rollback will be triggered
END

-- Cleanup backup (optional, can be scheduled)
-- DROP PROCEDURE IF EXISTS dbo.sp_GetCustomerOrders_backup_20241225;

PRINT 'Successfully deployed: dbo.sp_GetCustomerOrders';
GO
```

## AI-Powered Features

### Semantic Comparison

```yaml
ai_comparison:
  # Detects refactoring, not just text changes
  detect_renames:
    - "CustomerID" → "CustomerId"  # Case normalization
    - "GetCust" → "GetCustomer"    # Rename detection

  detect_refactoring:
    - Extracted common logic to function
    - Merged duplicate procedures
    - Split large procedure into smaller ones

  ignore_cosmetic:
    - Whitespace changes
    - Comment additions
    - Formatting differences
```

### Smart Dependency Ordering

```
Deployment Order (Automatically Determined):

1. Tables (base objects first)
   └── CustomerPreferences (no dependencies)
   └── OrderAuditLog (depends on Orders)

2. Functions (before procedures that use them)
   └── fn_CalculateDiscount

3. Views (after tables they reference)
   └── vw_CustomerOrders

4. Procedures (after functions/views they use)
   └── sp_GetCustomerOrders (uses fn_CalculateDiscount)
   └── sp_ProcessRefund (uses vw_CustomerOrders)

5. Triggers (after tables/procedures they reference)
   └── tr_Orders_AuditLog

6. Indexes (after tables, non-blocking where possible)
   └── IX_Orders_CustomerDate
```

## Configuration

```yaml
# sql2ai-compare.yaml
comparison:
  include:
    - tables
    - views
    - procedures
    - functions
    - triggers
    - indexes
    - constraints
    - permissions

  exclude:
    patterns:
      - "*_backup"
      - "*_temp"
      - "*_dev"
      - "test_*"
    schemas:
      - "staging"
      - "debug"

  options:
    ignore_whitespace: true
    ignore_comments: false
    case_sensitive: false
    compare_data: false  # Schema only by default

output:
  format: modular        # or monolithic
  generate_rollback: true
  include_validation: true
  deployment_report: html

environment:
  dev:
    connection: "Server=dev-db;Database=AppDB;..."
  staging:
    connection: "Server=staging-db;Database=AppDB;..."
  production:
    connection: "Server=prod-db;Database=AppDB;..."
    requires_approval: true
```

## CLI Commands

```bash
# Basic comparison
sql2ai compare --source dev-db --target prod-db

# Comparison with output directory
sql2ai compare \
  --source "Server=dev;Database=App" \
  --target "Server=prod;Database=App" \
  --output ./deployment-scripts

# Preview only (no script generation)
sql2ai compare --source dev --target prod --preview

# Compare specific object types
sql2ai compare \
  --source dev --target prod \
  --include tables,procedures \
  --exclude indexes

# Compare specific objects by name
sql2ai compare \
  --source dev --target prod \
  --objects "dbo.Orders,dbo.Customers,dbo.sp_*"

# Generate with rollback scripts
sql2ai compare \
  --source dev --target prod \
  --generate-rollback \
  --output ./scripts

# Deploy generated scripts (with dry-run)
sql2ai compare deploy \
  --scripts ./deployment-scripts \
  --target prod-db \
  --dry-run

# Deploy for real
sql2ai compare deploy \
  --scripts ./deployment-scripts \
  --target prod-db \
  --confirm

# Generate HTML comparison report
sql2ai compare report \
  --source dev --target prod \
  --format html \
  --output comparison-report.html

# Schedule recurring comparison
sql2ai compare schedule \
  --source dev --target staging \
  --cron "0 6 * * *" \
  --notify-on-drift
```

## Integration with CI/CD

```yaml
# GitHub Actions example
name: Database Schema Comparison

on:
  push:
    branches: [main]
    paths:
      - 'database/**'

jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Compare schemas
        run: |
          sql2ai compare \
            --source ${{ secrets.DEV_CONNECTION }} \
            --target ${{ secrets.STAGING_CONNECTION }} \
            --output ./sync-scripts \
            --generate-rollback

      - name: Upload deployment scripts
        uses: actions/upload-artifact@v3
        with:
          name: deployment-scripts
          path: ./sync-scripts

      - name: Create PR with changes
        if: steps.compare.outputs.has_changes == 'true'
        run: |
          # Create PR with generated scripts
```

## Integration Points

- **SQL Version**: Compare against versioned snapshots
- **SQL Migrate**: Generate migration files from comparison
- **SQL Test**: Auto-generate tests for changed objects
- **SQL Orchestrate**: Schedule recurring comparisons
- **SQL Audit**: Log all comparison and deployment activities
