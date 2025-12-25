# SQL Monitor

**Real-Time Database Monitoring Dashboard**

## Overview

SQL Monitor provides comprehensive real-time monitoring for SQL Server and PostgreSQL databases. Track performance metrics, query execution, connection pools, and system health from a unified dashboard.

## The Problem

### Current Monitoring Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Fragmented tools | Different dashboards per DB | No unified view |
| Reactive monitoring | Wait for alerts | Issues discovered late |
| Missing context | Raw metrics only | Hard to diagnose |
| Limited history | Short retention | Can't identify trends |
| Alert fatigue | Too many false positives | Real issues missed |

## SQL Monitor Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL MONITOR                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    DASHBOARD LAYER                          │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │
│  │  │  Performance │  │  Connections │  │    Queries   │      │ │
│  │  │   Metrics    │  │    Monitor   │  │   Analysis   │      │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    COLLECTION LAYER                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │ │
│  │  │   SQL Agent  │  │   PG Agent   │  │  Custom      │      │ │
│  │  │  Collector   │  │  Collector   │  │  Collectors  │      │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘      │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    STORAGE & ALERTS                         │ │
│  │  • Time-series metrics  • Alert rules  • Notifications     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Dashboard Components

### Performance Overview

```
╔══════════════════════════════════════════════════════════════════╗
║                    PERFORMANCE OVERVIEW                           ║
╠══════════════════════════════════════════════════════════════════╣
║ CPU Usage                          Memory Usage                   ║
║ ████████████████░░░░ 78%          ██████████████░░░░░░ 68%       ║
║                                                                   ║
║ Disk I/O (MB/s)                    Buffer/Cache Hit Ratio        ║
║ Read:  ██████░░░░ 245              ███████████████████░ 96%      ║
║ Write: ████░░░░░░ 128                                             ║
╠══════════════════════════════════════════════════════════════════╣
║ BATCH REQUESTS/SEC              TRANSACTIONS/SEC                  ║
║        1,247                           892                        ║
║ ▲ +12% from yesterday           ▲ +8% from yesterday             ║
╚══════════════════════════════════════════════════════════════════╝
```

### Connection Monitor

```
╔══════════════════════════════════════════════════════════════════╗
║                    CONNECTION MONITOR                             ║
╠══════════════════════════════════════════════════════════════════╣
║ CONNECTION POOL                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Active:    245 / 500  ████████████░░░░░░░░ 49%                   ║
║ Idle:      180                                                    ║
║ Sleeping:  75                                                     ║
║ Blocked:   3 ⚠️                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP CONNECTIONS BY DATABASE                                       ║
║ ─────────────────────────────────────────────────────────────── ║
║ production     ██████████████████ 156                            ║
║ analytics      █████████ 78                                       ║
║ staging        ████ 34                                            ║
║ development    ██ 12                                              ║
╠══════════════════════════════════════════════════════════════════╣
║ BLOCKING CHAINS                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Session 547 → blocking → [Session 892, 893, 1024]                ║
║ Duration: 3 min 24 sec | Query: UPDATE Orders SET...             ║
║ [Kill Session] [View Query] [Ignore]                             ║
╚══════════════════════════════════════════════════════════════════╝
```

### Query Analysis

```
╔══════════════════════════════════════════════════════════════════╗
║                    QUERY ANALYSIS                                 ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP QUERIES BY DURATION (Last Hour)                               ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. SELECT * FROM Orders WHERE CustomerID = @p1                   ║
║    Avg: 4.2s | Calls: 847 | CPU: High | ▲ 340% regression        ║
║                                                                   ║
║ 2. UPDATE Inventory SET Quantity = @p1 WHERE ProductID = @p2     ║
║    Avg: 2.8s | Calls: 234 | CPU: Medium | ▲ 120% regression      ║
║                                                                   ║
║ 3. INSERT INTO AuditLog (...)                                    ║
║    Avg: 1.1s | Calls: 12,456 | CPU: Low | → Normal               ║
╠══════════════════════════════════════════════════════════════════╣
║ QUERY PLAN CHANGES                                                ║
║ ─────────────────────────────────────────────────────────────── ║
║ ⚠️  Plan regression: GetCustomerOrders (query hash: 0x1234...)   ║
║     Old plan: Index Seek → New plan: Table Scan                  ║
║     Impact: 847 executions affected                              ║
║     [View Plans] [Force Old Plan] [Investigate]                  ║
╚══════════════════════════════════════════════════════════════════╝
```

## Metrics Collected

### SQL Server Metrics

```yaml
sql_server_metrics:
  performance:
    - batch_requests_per_sec
    - sql_compilations_per_sec
    - sql_recompilations_per_sec
    - page_life_expectancy
    - buffer_cache_hit_ratio
    - checkpoint_pages_per_sec

  memory:
    - total_server_memory_kb
    - target_server_memory_kb
    - memory_grants_pending
    - memory_grants_outstanding

  io:
    - disk_read_bytes_per_sec
    - disk_write_bytes_per_sec
    - io_stall_read_ms
    - io_stall_write_ms

  connections:
    - user_connections
    - blocked_processes
    - lock_waits_per_sec
    - deadlocks_per_sec
```

### PostgreSQL Metrics

```yaml
postgresql_metrics:
  performance:
    - tps (transactions per second)
    - active_connections
    - idle_connections
    - waiting_connections
    - cache_hit_ratio

  replication:
    - replication_lag_bytes
    - replication_lag_seconds
    - wal_bytes_per_sec

  vacuum:
    - dead_tuples
    - last_autovacuum
    - vacuum_running

  locks:
    - lock_waits
    - exclusive_locks
    - deadlocks
```

## Alert Configuration

```yaml
# sql2ai-monitor.yaml
alerts:
  - name: high_cpu
    metric: cpu_percent
    threshold: 90
    duration: 5m
    severity: critical
    channels: [slack, pagerduty]

  - name: blocking_detected
    metric: blocked_processes
    threshold: 1
    duration: 2m
    severity: warning
    channels: [slack, email]

  - name: memory_pressure
    metric: memory_grants_pending
    threshold: 5
    duration: 1m
    severity: critical
    channels: [slack, pagerduty]

  - name: replication_lag
    metric: replication_lag_seconds
    threshold: 60
    duration: 5m
    severity: warning
    channels: [email]

notification_channels:
  slack:
    webhook: ${SLACK_WEBHOOK}
    channel: "#db-alerts"

  pagerduty:
    routing_key: ${PAGERDUTY_KEY}

  email:
    recipients:
      - dba-team@company.com
```

## CLI Commands

```bash
# Start monitoring agent
sql2ai monitor start --connection "Server=prod-db;Database=master"

# View current status
sql2ai monitor status

# View real-time metrics
sql2ai monitor metrics --watch

# List active connections
sql2ai monitor connections

# Show blocking chains
sql2ai monitor blocks

# View top queries
sql2ai monitor queries --top 10 --sort duration

# Export metrics
sql2ai monitor export --format prometheus --output metrics.prom

# Configure alerts
sql2ai monitor alerts add --name "high-cpu" --threshold 90 --channel slack
```

## Integration Points

- **SQL Orchestrate**: Triggers monitoring checks, displays job health
- **SQL Optimize**: Feeds query performance data for analysis
- **SQL Audit**: Provides audit event dashboards
- **SQL Agent**: Observability for autonomous operations
- **SQL Comply**: Compliance status monitoring

## Retention and Storage

```yaml
retention:
  realtime_metrics: 24h      # High-resolution (1 second)
  hourly_aggregates: 30d     # Hourly rollups
  daily_aggregates: 1y       # Daily rollups
  alerts_history: 90d        # Alert occurrences

storage:
  backend: timescaledb       # Or influxdb, prometheus
  compression: enabled
  estimated_size: 50GB/server/year
```
