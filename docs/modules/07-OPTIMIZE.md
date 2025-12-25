# SQL Optimize

**Module 7 of 8** | **Status:** Planned | **Priority:** P0

## Overview

SQL Optimize provides deep performance analysis using Query Store data, wait statistics, execution plans, and error logs. It identifies issues, explains root causes, and generates one-click remediation scripts with AI-powered insights.

## Problems Solved

| Problem | Current State | SQL Optimize Solution |
|---------|---------------|----------------------|
| Query Store overload | Too much data, no insight | Prioritized actionable findings |
| Plan regression mystery | "Why is it slow now?" | Root cause analysis |
| Missing index guessing | sys.dm_db_missing_index | Context-aware recommendations |
| Wait stats confusion | Numbers without meaning | Explained wait categories |
| Reactive firefighting | Find issues after impact | Proactive detection |

## Analysis Capabilities

### 1. Query Store Analysis

**Top Resource Consumers**
```
┌─────────────────────────────────────────────────────────────┐
│ Top 10 Queries by CPU                                       │
├─────────────────────────────────────────────────────────────┤
│ Rank │ Query                  │ Avg CPU │ Executions │ Trend│
├──────┼────────────────────────┼─────────┼────────────┼──────┤
│ 1    │ sp_ProcessOrder        │ 234ms   │ 45,231     │ ↑ 15%│
│ 2    │ SELECT * FROM Orders...│ 156ms   │ 12,456     │ ↓ 5% │
│ 3    │ fn_CalculateTax        │ 89ms    │ 145,678    │ → 0% │
└─────────────────────────────────────────────────────────────┘
```

**Plan Regression Detection**
```
⚠ PLAN REGRESSION DETECTED

Query: sp_GetCustomerOrders
Query Hash: 0x8A7B3C2D1E

Timeline:
├─ 2024-12-20: New plan selected (Plan ID: 47)
├─ 2024-12-20: Execution time increased 340%
└─ 2024-12-24: Still using suboptimal plan

Root Cause Analysis:
The query optimizer chose a new plan after statistics update on
the Orders table. The new plan uses a Hash Match instead of
Nested Loops, which is suboptimal for small result sets.

Recommendations:
1. Force previous plan (Plan ID: 42)         [Apply] [Script]
2. Update statistics with FULLSCAN          [Apply] [Script]
3. Add query hint OPTION(USE PLAN...)       [Apply] [Script]
```

### 2. Wait Statistics Analysis

**Current Wait Categories**
```
┌─────────────────────────────────────────────────────────────┐
│ Wait Statistics Analysis                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ CPU Pressure (Signal Waits): 23%                            │
│ ████████░░░░░░░░░░░░ Normal                                │
│                                                             │
│ I/O Pressure: 45%                                           │
│ █████████████░░░░░░░ Elevated ⚠                            │
│ → Top: PAGEIOLATCH_SH (12,456 ms/sec)                       │
│ → Recommendation: Review missing indexes                    │
│                                                             │
│ Lock Contention: 8%                                         │
│ ███░░░░░░░░░░░░░░░░░ Normal                                │
│                                                             │
│ Memory Pressure: 3%                                         │
│ █░░░░░░░░░░░░░░░░░░░ Low                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3. Index Analysis

**Missing Index Recommendations**
```
Missing Index Analysis

1. HIGH IMPACT (Estimated improvement: 89%)
   Table: dbo.Orders
   Recommended Index:
   CREATE NONCLUSTERED INDEX IX_Orders_CustomerID_Status
   ON dbo.Orders (CustomerID, Status)
   INCLUDE (OrderDate, TotalAmount);

   Justification:
   - Used by 23 queries
   - Would eliminate 4.2M key lookups/day
   - Estimated size: 145 MB

   [Create Index] [Schedule for Maintenance Window]

2. MEDIUM IMPACT (Estimated improvement: 45%)
   Table: dbo.OrderItems
   ...
```

**Unused Index Detection**
```
Unused Indexes (Last 30 Days)

1. IX_Customers_CreatedAt
   Table: dbo.Customers
   Size: 234 MB
   Reads: 0 | Writes: 12,456
   Created: 2023-06-15
   Recommendation: DROP (saves 234 MB, improves insert performance)

   [Drop Index] [Mark as Keep] [Analyze Queries]
```

**Duplicate/Overlapping Indexes**
```
Overlapping Indexes Detected

Table: dbo.Orders

Index 1: IX_Orders_CustomerID
  Columns: (CustomerID)

Index 2: IX_Orders_CustomerID_Date
  Columns: (CustomerID, OrderDate)

Analysis: IX_Orders_CustomerID is redundant because
IX_Orders_CustomerID_Date covers the same leading column.

Recommendation: Drop IX_Orders_CustomerID
Space Savings: 89 MB

[Drop Redundant] [Keep Both] [Explain]
```

### 4. Parameter Sniffing Detection

```
Parameter Sniffing Issue Detected

Procedure: sp_GetOrdersByCustomer
Parameter: @CustomerID

Problem:
The procedure was first compiled with @CustomerID = 12345
(a customer with 50,000 orders). The plan optimized for large
result sets is being used for all customers, including those
with only a few orders.

Evidence:
- Customer 12345: 50,000 orders → 45ms (optimal)
- Customer 99999: 3 orders → 8,200ms (using same plan!)

Solutions:

1. OPTION (RECOMPILE)
   Pros: Always optimal plan
   Cons: Compilation overhead
   Best for: Infrequent queries

2. OPTION (OPTIMIZE FOR UNKNOWN)
   Pros: Uses average statistics
   Cons: May not be optimal for extremes
   Best for: Evenly distributed data

3. Filtered Procedures
   Pros: Optimal plans for each case
   Cons: Code duplication
   Best for: Known usage patterns

[Apply Solution 1] [Apply Solution 2] [Show Code for 3]
```

### 5. Blocking & Deadlock Analysis

**Current Blocking Chains**
```
Active Blocking Chains

Chain 1 (Duration: 45 seconds)
SPID 55 (Blocker)
  └─ Query: UPDATE Inventory SET Qty = ...
  └─ Wait: WRITELOG
     └─ SPID 67 (Blocked)
        └─ Query: SELECT * FROM Inventory WHERE...
        └─ Wait: LCK_M_S (23 sec)
           └─ SPID 89 (Blocked)
              └─ Query: INSERT INTO Orders...
              └─ Wait: LCK_M_IX (12 sec)

Recommendation:
- SPID 55 is waiting on log writes (slow I/O)
- Consider: Transaction log on faster storage
- Consider: Reduce transaction size

[Kill SPID 55] [Alert DBA] [Analyze Query]
```

**Deadlock History**
```
Deadlock Analysis (Last 7 Days)

Total Deadlocks: 23
Pattern Detected: sp_ProcessOrder vs sp_UpdateInventory

Deadlock Graph:
┌─────────────────┐     ┌─────────────────┐
│ sp_ProcessOrder │────▸│ Orders (X)      │
│                 │◂────│                 │
│ Wants: Inventory│     │ Has: Orders     │
└─────────────────┘     └─────────────────┘
         │                      ▲
         ▼                      │
┌─────────────────┐     ┌─────────────────┐
│ Inventory (X)   │────▸│sp_UpdateInv     │
│                 │◂────│                 │
│ Has: Inventory  │     │ Wants: Orders   │
└─────────────────┘     └─────────────────┘

Root Cause: Lock acquisition order differs between procedures

Solution: Modify lock order in sp_UpdateInventory to:
1. Lock Orders first
2. Then lock Inventory

[Show Fix Script] [Compare Procedures]
```

### 6. Log Analysis

**Error Log Pattern Detection**
```
Error Log Analysis (Last 24 Hours)

Pattern: Login Failures
Count: 1,247 occurrences
Trend: ↑ 500% from yesterday

Sample:
  Login failed for user 'webapp'. Reason: Password mismatch
  Client: 10.0.1.45

Analysis:
- 98% from same IP (10.0.1.45)
- Started at 03:45 AM
- Possible brute force attack

Recommendations:
1. Block IP 10.0.1.45 at firewall
2. Enable account lockout policy
3. Review 'webapp' account permissions

[Block IP] [Enable Lockout] [Alert Security]
```

## Remediation Engine

### One-Click Fixes

Each finding includes remediation options:

```
Fix Options:

[Quick Fix]     - Apply immediately (simple, low risk)
[Script Only]   - Generate script for review
[Schedule]      - Apply during maintenance window
[Explain]       - Detailed explanation of the fix
[Simulate]      - Estimate impact before applying
```

### Fix Simulation

```
Fix Simulation: Add Missing Index

Current Performance:
- Query Duration: 4,500 ms
- Logical Reads: 1,245,678
- Execution Plan: Clustered Index Scan

After Index (Estimated):
- Query Duration: 45 ms (99% improvement)
- Logical Reads: 234 (99.98% reduction)
- Execution Plan: Index Seek + Key Lookup

Side Effects:
- Index Size: ~145 MB
- Insert Overhead: +2ms per insert
- Update Overhead: +1ms per update

Recommendation: APPLY (benefits outweigh costs)

[Confirm Apply] [Modify Index] [Cancel]
```

## API Endpoints

```
GET    /api/optimize/summary              # Overall health summary
GET    /api/optimize/query-store          # Query Store analysis
GET    /api/optimize/wait-stats           # Wait statistics
GET    /api/optimize/indexes/missing      # Missing indexes
GET    /api/optimize/indexes/unused       # Unused indexes
GET    /api/optimize/indexes/duplicates   # Duplicate indexes
GET    /api/optimize/blocking             # Current blocking
GET    /api/optimize/deadlocks            # Deadlock history
GET    /api/optimize/errors               # Error log patterns

POST   /api/optimize/remediate            # Apply fix
POST   /api/optimize/simulate             # Simulate fix
```

## CLI Commands

```bash
sql2ai optimize analyze --connection "..."
sql2ai optimize report --format html
sql2ai optimize indexes --action recommend
sql2ai optimize indexes --action cleanup
sql2ai optimize queries --top 20
sql2ai optimize blocking --watch
sql2ai optimize deadlocks --days 30
sql2ai optimize fix --issue IX001 --apply
```

## Implementation Status

- [ ] Core library structure (libs/query-optimizer)
- [ ] Query Store integration
- [ ] Wait statistics analyzer
- [ ] Missing index analyzer
- [ ] Unused index detector
- [ ] Duplicate index finder
- [ ] Parameter sniffing detector
- [ ] Plan regression detector
- [ ] Blocking chain analyzer
- [ ] Deadlock analyzer
- [ ] Error log analyzer
- [ ] Remediation engine
- [ ] Fix simulation
- [ ] API routers
- [ ] CLI commands
