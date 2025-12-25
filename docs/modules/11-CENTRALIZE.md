# SQL Centralize

**Multi-Tier Replication & Data Distribution Platform**

## Overview

SQL Centralize provides minimally invasive, foreign key-aware data movement across SQL Server and PostgreSQL environments. It supports consolidation, replication, distribution (pub/sub), and ETL patterns while maintaining referential integrity and minimizing impact on source systems.

## The Problem

### Current Data Distribution Challenges

| Challenge | Traditional Tools | Pain Point |
|-----------|-------------------|------------|
| FK Dependencies | Ignored or break | Data integrity failures |
| Schema Drift | Manual sync | Out-of-sync replicas |
| Bidirectional Sync | Complex conflict resolution | Data loss risk |
| Cross-Platform | Separate tools for PG/SQL | Tool sprawl |
| Minimal Invasive | Heavy triggers/CDC | Performance impact |
| Real-time + Batch | Different tools | Integration complexity |

## SQL Centralize Solution

### Supported Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONSOLIDATION                                 │
│    Multiple Sources ──────────────────► Central Data Warehouse   │
│    (Branch DBs)                         (HQ Analytics)           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    REPLICATION                                   │
│    Primary ◄─────────────────────────► Secondary                 │
│    (Read/Write)                        (Read/Failover)           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    DISTRIBUTION (Pub/Sub)                        │
│    Publisher ─────────────────────────► Subscriber 1             │
│         │                               Subscriber 2             │
│         └──────────────────────────────► Subscriber N            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE                                  │
│    Source ─► Extract ─► Transform ─► Load ─► Destination         │
│              (CDC)      (Rules)     (Merge)                      │
└─────────────────────────────────────────────────────────────────┘
```

## Key Capabilities

### 1. Foreign Key-Aware Sync

SQL Centralize automatically detects and respects FK relationships:

```
Source Tables (with FKs):
  Customers ◄── Orders ◄── OrderItems ◄── Products
       │                        │
       └── Addresses            └── Inventory

Sync Order (auto-calculated):
  1. Customers (no dependencies)
  2. Addresses (depends on Customers)
  3. Products (no dependencies)
  4. Inventory (depends on Products)
  5. Orders (depends on Customers)
  6. OrderItems (depends on Orders, Products)
```

```yaml
# sql2ai-centralize.yaml
sync:
  source: "sqlserver://prod-server/SalesDB"
  target: "postgresql://warehouse/analytics"

  tables:
    - name: Customers
      mode: full

    - name: Orders
      mode: incremental
      key: OrderId
      watermark: ModifiedDate

    - name: OrderItems
      mode: incremental
      depends_on: [Orders]  # Auto-detected from FK

  fk_handling:
    mode: auto  # Auto-detect and order
    on_missing_parent: defer  # Queue until parent arrives
    on_orphan: log  # Log but continue
```

### 2. Minimally Invasive Change Detection

**Option 1: Timestamp-Based (Zero Impact)**
```sql
-- Uses existing ModifiedDate columns
-- No triggers, no CDC overhead
SELECT * FROM Orders
WHERE ModifiedDate > @LastSync;
```

**Option 2: Lightweight Triggers**
```sql
-- Minimal trigger for delete tracking
CREATE TRIGGER TR_Orders_Delete ON Orders
AFTER DELETE AS
INSERT INTO _sql2ai_deletes (TableName, PK, DeletedAt)
SELECT 'Orders', OrderId, GETUTCDATE() FROM deleted;
```

**Option 3: CDC Integration**
```sql
-- Use SQL Server CDC for full audit trail
-- SQL Centralize reads CDC tables directly
SELECT * FROM cdc.dbo_Orders_CT
WHERE __$start_lsn > @LastLSN;
```

**Option 4: PostgreSQL Logical Replication**
```sql
-- Native PostgreSQL pub/sub
CREATE PUBLICATION sales_pub FOR TABLE customers, orders;
-- SQL Centralize subscribes to publication
```

### 3. Conflict Resolution

For bidirectional sync, SQL Centralize provides multiple strategies:

```yaml
conflict_resolution:
  strategy: timestamp_wins  # Most recent change wins
  # OR
  strategy: source_wins     # Primary always wins
  # OR
  strategy: custom_rules    # Define per-table rules

  custom_rules:
    Orders:
      on_conflict:
        - if: "source.Status = 'Cancelled'"
          then: accept_source
        - if: "target.Total > source.Total"
          then: accept_target
        - else: accept_latest
```

### 4. Cross-Platform Support

```
SQL Server ◄────────────────────────────► PostgreSQL
     │                                         │
     │  ┌─────────────────────────────────┐   │
     │  │   SQL Centralize Engine         │   │
     │  │   - Schema translation          │   │
     │  │   - Type mapping                │   │
     │  │   - Syntax conversion           │   │
     │  └─────────────────────────────────┘   │
     │                                         │
     ▼                                         ▼
  Data Types:                            Data Types:
  NVARCHAR(MAX) ──────────────────────► TEXT
  DATETIME2 ──────────────────────────► TIMESTAMP
  UNIQUEIDENTIFIER ───────────────────► UUID
  BIT ────────────────────────────────► BOOLEAN
  MONEY ──────────────────────────────► NUMERIC(19,4)
```

### 5. Multi-Tier Architecture

```
                    ┌─────────────────┐
                    │   TIER 0        │
                    │   Central HQ    │
                    │   (Full Data)   │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
   │   TIER 1    │   │   TIER 1    │   │   TIER 1    │
   │  Regional   │   │  Regional   │   │  Regional   │
   │  (Subset)   │   │  (Subset)   │   │  (Subset)   │
   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
          │                  │                  │
    ┌─────┴─────┐      ┌─────┴─────┐      ┌─────┴─────┐
    ▼           ▼      ▼           ▼      ▼           ▼
 ┌──────┐   ┌──────┐   ...         ...    ...         ...
 │TIER 2│   │TIER 2│
 │Branch│   │Branch│
 │(Local)   │(Local)
 └──────┘   └──────┘
```

```yaml
# Multi-tier configuration
tiers:
  - name: central
    level: 0
    databases: ["hq-primary"]
    data: "*"  # All data

  - name: regional
    level: 1
    databases: ["region-east", "region-west"]
    data:
      filter: "RegionId = @TierRegionId"
    sync_up: true   # Changes flow up to central
    sync_down: true # Changes flow down from central

  - name: branch
    level: 2
    databases: ["branch-*"]
    data:
      filter: "BranchId = @TierBranchId"
    sync_up: true
    sync_down: true
```

## Sync Modes

### 1. Full Sync
```yaml
mode: full
schedule: "0 2 * * *"  # Daily at 2 AM
options:
  truncate_target: false
  preserve_deletes: true
```

### 2. Incremental Sync
```yaml
mode: incremental
schedule: "*/5 * * * *"  # Every 5 minutes
watermark:
  column: ModifiedDate
  type: timestamp
```

### 3. Real-Time Streaming
```yaml
mode: stream
source:
  type: cdc  # or logical_replication for PG
latency_target: "< 1 second"
```

### 4. Snapshot + CDC
```yaml
mode: snapshot_plus_cdc
initial:
  method: bulk_copy
  parallel: 8
ongoing:
  method: cdc_stream
```

## Monitoring Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL CENTRALIZE DASHBOARD                            ║
╠══════════════════════════════════════════════════════════════════╣
║ ACTIVE SYNC JOBS                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ Sales → Warehouse     ● Running    Lag: 2.3s    12,450 rows/min  ║
║ Inventory → Regional  ● Running    Lag: 45s     3,200 rows/min   ║
║ Branch → Central      ● Running    Lag: 1.2s    890 rows/min     ║
╠══════════════════════════════════════════════════════════════════╣
║ RECENT ACTIVITY (Last Hour)                                      ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Rows Synced:        1,247,893                              ║
║ Conflicts Resolved:       23 (auto)                              ║
║ Errors:                   0                                      ║
║ FK Deferrals:             156 (all resolved)                     ║
╠══════════════════════════════════════════════════════════════════╣
║ DATA FRESHNESS                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Warehouse.Customers:      2 seconds ago                          ║
║ Warehouse.Orders:         2 seconds ago                          ║
║ Regional.Inventory:       45 seconds ago                         ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Initialize sync configuration
sql2ai centralize init --source "..." --target "..."

# Analyze FK dependencies
sql2ai centralize analyze-deps

# Run initial full sync
sql2ai centralize sync --mode full

# Start continuous replication
sql2ai centralize stream --config sync.yaml

# Check sync status
sql2ai centralize status

# Compare source/target data
sql2ai centralize validate --table Orders
```

## Integration Points

- **SQL Convert**: Sync data during migrations
- **SQL Version**: Track schema changes across replicas
- **SQL Comply**: Ensure data handling meets compliance
- **SQL Orchestrator**: Monitor sync health and alerts
