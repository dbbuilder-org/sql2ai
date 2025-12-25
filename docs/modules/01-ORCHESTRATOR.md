# SQL Orchestrator

**Module 1 of 8** | **Status:** In Development | **Priority:** P0

## Overview

SQL Orchestrator is the central coordination hub for SQL2.AI, providing unified monitoring, security auditing, and compliance checking with full before/after context for change impact analysis.

## Problems Solved

| Problem | Current State | SQL Orchestrator Solution |
|---------|---------------|---------------------------|
| Fragmented monitoring | Multiple disconnected tools | Single unified platform |
| No change context | Metrics without "why" | Before/after snapshots |
| Manual compliance | Spreadsheets and audits | Automated evidence collection |
| Reactive alerting | Find issues after impact | Anomaly-based proactive checks |
| Siloed data | Can't correlate across systems | Unified data model |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SQL2.AI Platform                          │
├─────────────────────────────────────────────────────────────┤
│  API Layer (FastAPI)                                         │
│  └── /api/orchestrator/*                                     │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator Engine                                         │
│  ├── Check Registry (extensible)                             │
│  ├── Execution Engine (priority queue)                       │
│  ├── Snapshot Manager                                        │
│  ├── Diff Engine                                             │
│  └── Event Bus                                               │
├─────────────────────────────────────────────────────────────┤
│  Triggers                                                    │
│  ├── Scheduled (cron)                                        │
│  ├── Deployment (CI/CD hooks)                                │
│  ├── Anomaly (metric thresholds)                             │
│  └── On-demand (API)                                         │
├─────────────────────────────────────────────────────────────┤
│  Agents (distributed)                                        │
│  └── sql-monitor-agent pattern                               │
└─────────────────────────────────────────────────────────────┘
```

## Check Categories

### Performance Checks
- Query performance regression detection
- Index usage analysis
- Wait statistics monitoring
- Blocking chain detection
- TempDB contention
- Plan cache analysis

### Security Checks
- Permission audit (sysadmin, db_owner detection)
- Encryption validation (TDE, TLS)
- Login/access auditing
- Vulnerability scanning
- Sensitive data exposure

### Compliance Checks
- SOC 2 control validation
- HIPAA PHI protection
- GDPR data classification
- PCI-DSS cardholder security
- FERPA educational records
- Custom framework support

## Trigger System

### Scheduled Triggers
```yaml
schedule:
  type: cron
  expression: "*/5 * * * *"  # Every 5 minutes
  checks:
    - performance.query-stats
    - performance.blocking
  priority: normal
```

### Deployment Triggers
```yaml
trigger:
  type: deployment
  stages:
    pre:
      - capture_snapshot: true
      - checks: [security.*, compliance.*]
    post:
      - capture_snapshot: true
      - compare_snapshots: true
      - checks: [performance.*]
```

### Anomaly Triggers
```yaml
trigger:
  type: anomaly
  metrics:
    - name: cpu_percent
      threshold: 85
      duration: 5m
      action:
        run_checks: [performance.query-stats, performance.blocking]
        capture_snapshot: true
```

## Snapshot System

### What Gets Captured
- Full schema (tables, columns, indexes, constraints)
- Code objects (procedures, views, functions, triggers)
- Security principals (logins, users, roles, permissions)
- Server configuration
- Database settings

### Comparison Features
- Table-by-table diff
- Column modification detection
- Breaking change identification
- Dependency impact analysis
- Migration script generation

## API Endpoints

```
POST   /api/orchestrator/runs           # Trigger new run
GET    /api/orchestrator/runs           # List runs
GET    /api/orchestrator/runs/{id}      # Get run details
POST   /api/orchestrator/runs/{id}/cancel

GET    /api/orchestrator/checks         # List check definitions
POST   /api/orchestrator/checks/config  # Configure check for connection

POST   /api/orchestrator/snapshots      # Capture snapshot
GET    /api/orchestrator/snapshots      # List snapshots
POST   /api/orchestrator/snapshots/compare

GET    /api/orchestrator/reports/compliance
GET    /api/orchestrator/reports/security
```

## Database Schema

### Core Tables
- `CheckDefinitions` - Available checks
- `CheckConfigurations` - Per-connection settings
- `OrchestratorRuns` - Execution tracking
- `CheckExecutions` - Individual check runs
- `CheckFindings` - Discovered issues
- `SchemaSnapshots` - State captures
- `SchemaDiffs` - Comparison results
- `ComplianceEvidence` - Audit trail

## Integration Points

| Integrates With | Purpose |
|-----------------|---------|
| SQL Optimize | Receive performance findings for remediation |
| SQL Compliance | Provide compliance evidence |
| SQL Version | Trigger on deployments |
| SQL Migrator | Validate migrations |
| LLM Orchestrator | AI analysis of findings |

## CLI Commands

```bash
sql2ai orchestrator run --checks=all
sql2ai orchestrator run --category=security
sql2ai orchestrator snapshot capture
sql2ai orchestrator snapshot diff before.id after.id
sql2ai orchestrator status
```

## Implementation Status

- [ ] Core library structure (libs/sql-orchestrator)
- [ ] Check base class and registry
- [ ] Performance checks (10 checks)
- [ ] Security checks (8 checks)
- [ ] Compliance checks (12 checks)
- [ ] Trigger system
- [ ] Snapshot manager
- [ ] Diff engine
- [ ] API routers
- [ ] Database schema
- [ ] Agent integration
