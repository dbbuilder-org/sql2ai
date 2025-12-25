# SQL Version

**Module 3 of 8** | **Status:** Planned | **Priority:** P1

## Overview

SQL Version provides Git-like version control specifically designed for database objects. Track every change to every stored procedure, view, and function with full history, blame, diff, and rollback capabilities.

## Problems Solved

| Problem | Current State | SQL Version Solution |
|---------|---------------|----------------------|
| Lost procedure history | Overwritten on deploy | Full version history |
| No change attribution | "Who changed this?" | Line-by-line blame |
| Environment drift | Dev differs from prod | Branch-based tracking |
| Rollback difficulty | Manual script hunting | One-click restore |
| Merge conflicts | Overwrite and hope | Conflict detection |

## Core Concepts

### Object-Level Versioning

Unlike file-based version control, SQL Version tracks each database object independently:

```
Database: MyApp
├── Tables/
│   ├── Customers (v12) ─── Last modified: 2024-12-20
│   ├── Orders (v8) ─────── Last modified: 2024-12-18
│   └── Products (v15) ──── Last modified: 2024-12-24
├── Procedures/
│   ├── sp_ProcessOrder (v23) ── 23 versions tracked
│   ├── sp_GetCustomer (v7) ──── 7 versions tracked
│   └── sp_UpdateInventory (v11)
├── Views/
│   └── vw_ActiveOrders (v4)
└── Functions/
    └── fn_CalculateTax (v3)
```

### Version Metadata

Each version captures:
- Full object definition (CREATE statement)
- Author (who made the change)
- Timestamp (when)
- Environment (where: dev/staging/prod)
- Commit message (why)
- Parent version (lineage)
- Content hash (integrity)

## Workflow

### 1. Initialize Tracking
```bash
sql2ai version init --connection "Server=...;Database=MyDB"
# Captures baseline of all objects
# Creates version tracking tables
```

### 2. Make Changes
Developer modifies procedure in SSMS or any SQL tool.

### 3. Capture Version
```bash
sql2ai version capture --message "Fixed tax calculation for international orders"
```

Output:
```
Changes detected:

Procedures:
  ~ dbo.sp_ProcessOrder
    + Added international tax handling
    + Updated error messages
    Lines: +45, -12

Captured as version v24
Author: chris@servicevision.net
```

### 4. View History
```bash
sql2ai version history dbo.sp_ProcessOrder
```

Output:
```
Version History: dbo.sp_ProcessOrder

v24  2024-12-24 10:30  chris@servicevision.net
     Fixed tax calculation for international orders

v23  2024-12-20 14:15  jane@company.com
     Added logging for audit compliance

v22  2024-12-18 09:00  chris@servicevision.net
     Refactored to use set-based operations

v21  2024-12-15 16:45  mike@company.com
     Added retry logic for deadlocks

... (19 more versions)
```

### 5. Diff Versions
```bash
sql2ai version diff dbo.sp_ProcessOrder v22 v24
```

Output:
```diff
--- dbo.sp_ProcessOrder v22
+++ dbo.sp_ProcessOrder v24
@@ -45,6 +45,20 @@
     -- Calculate tax
-    SET @Tax = @Subtotal * 0.08;
+    -- Handle international orders
+    IF @Country <> 'US'
+    BEGIN
+        SET @Tax = dbo.fn_GetInternationalTax(@Country, @Subtotal);
+    END
+    ELSE
+    BEGIN
+        SET @Tax = @Subtotal * @StateTaxRate;
+    END
+
+    -- Log for audit
+    INSERT INTO AuditLog (OrderID, TaxCalculated, Timestamp)
+    VALUES (@OrderID, @Tax, GETUTCDATE());
```

### 6. Blame
```bash
sql2ai version blame dbo.sp_ProcessOrder
```

Output:
```
dbo.sp_ProcessOrder - Line-by-Line Attribution

v24 chris@...  │  1: CREATE PROCEDURE dbo.sp_ProcessOrder
v1  original   │  2:     @OrderID INT,
v1  original   │  3:     @CustomerID INT
v15 jane@...   │  4:     @Country NVARCHAR(2) = 'US'
v24 chris@...  │  5: AS
v24 chris@...  │  6: BEGIN
v22 chris@...  │  7:     SET NOCOUNT ON;
v22 chris@...  │  8:     SET XACT_ABORT ON;
...
v24 chris@...  │ 45:     -- Handle international orders
v24 chris@...  │ 46:     IF @Country <> 'US'
```

### 7. Rollback
```bash
sql2ai version restore dbo.sp_ProcessOrder v22
```

Creates a new version (v25) with the content of v22.

## Branch Support

Track different object versions across environments:

```
                    ┌─── staging (v23)
                    │
main (v24) ─────────┼─── production (v22)
                    │
                    └─── feature/loyalty (v25)
```

### Commands
```bash
sql2ai version branch list
sql2ai version branch create feature/new-tax
sql2ai version branch merge feature/new-tax --into staging
sql2ai version branch compare staging production
```

## Conflict Detection

When the same object is modified in multiple branches:

```bash
sql2ai version merge staging --into production
```

Output:
```
Merge Conflict Detected!

Object: dbo.sp_ProcessOrder

staging (v25):
  Line 47: SET @Tax = dbo.fn_GetInternationalTax(@Country, @Subtotal);

production (v22):
  Line 47: SET @Tax = @Subtotal * 0.08;

Options:
  1. Keep staging version
  2. Keep production version
  3. Open merge editor
  4. Abort merge
```

## API Endpoints

```
GET    /api/versions/objects              # List tracked objects
GET    /api/versions/objects/{name}/history
GET    /api/versions/objects/{name}/{version}
POST   /api/versions/capture              # Capture changes
POST   /api/versions/restore              # Restore version
GET    /api/versions/diff/{v1}/{v2}
GET    /api/versions/blame/{name}
GET    /api/versions/branches
POST   /api/versions/branches
POST   /api/versions/merge
```

## Storage

### Version Table Schema
```sql
CREATE TABLE ObjectVersions (
    VersionID BIGINT IDENTITY PRIMARY KEY,
    ObjectName NVARCHAR(256) NOT NULL,
    ObjectType NVARCHAR(50) NOT NULL,
    Version INT NOT NULL,
    Definition NVARCHAR(MAX) NOT NULL,
    DefinitionHash VARBINARY(32) NOT NULL,
    Author NVARCHAR(256) NOT NULL,
    Message NVARCHAR(1000) NULL,
    Branch NVARCHAR(100) NOT NULL DEFAULT 'main',
    ParentVersionID BIGINT NULL,
    CapturedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),

    INDEX IX_Object_Version (ObjectName, Version DESC),
    INDEX IX_Branch (Branch, CapturedAt DESC)
);
```

## Git Integration

Optionally sync versions to git repository:

```bash
sql2ai version sync-to-git --repo ./database-objects
```

Creates:
```
database-objects/
├── Procedures/
│   ├── sp_ProcessOrder.sql
│   └── sp_GetCustomer.sql
├── Views/
│   └── vw_ActiveOrders.sql
└── Functions/
    └── fn_CalculateTax.sql
```

Each change creates a git commit with proper attribution.

## CLI Commands

```bash
sql2ai version init                    # Initialize tracking
sql2ai version capture                 # Capture current changes
sql2ai version history {object}        # Show version history
sql2ai version show {object} {version} # Show specific version
sql2ai version diff {v1} {v2}          # Compare versions
sql2ai version blame {object}          # Line-by-line attribution
sql2ai version restore {object} {v}    # Rollback to version
sql2ai version branch list             # List branches
sql2ai version branch create {name}    # Create branch
sql2ai version merge {from} --into {to}
sql2ai version sync-to-git             # Sync to git repo
```

## Implementation Status

- [ ] Core library structure (libs/version-control)
- [ ] Object tracking tables
- [ ] Version capture
- [ ] History retrieval
- [ ] Diff engine
- [ ] Blame calculation
- [ ] Restore functionality
- [ ] Branch support
- [ ] Conflict detection
- [ ] Git sync
- [ ] API routers
- [ ] CLI commands
