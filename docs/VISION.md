# SQL2.AI — Vision & Architecture

**Version:** 1.0.0 (Planning)
**Author:** Chris Therriault <chris@servicevision.net>
**Created:** 2025-12-24
**Status:** Strategic Planning Phase

---

## Executive Summary

**SQL2.AI** is a comprehensive SaaS platform that brings the same level of AI-driven sophistication to database-first development that coding AI assistants have brought to application development. We bridge the gap between:

- **What AI can do for code** (generate, refactor, test, review)
- **What AI should do for databases** (model, optimize, migrate, monitor, document)

### The Core Thesis

Modern AI coding assistants excel at application code but treat databases as an afterthought. They generate ORM models that create inefficient schemas, ignore set-based optimization, and produce row-by-row processing where set operations would be orders of magnitude faster.

**SQL2.AI inverts this paradigm:**
- Data models drive application objects (not the reverse)
- Stored procedures, views, and functions are first-class citizens
- Set-based optimization is the default, not the exception
- Transactions have full contextual visibility from the LLM
- Saga patterns are natively supported for distributed systems
- Database telemetry feeds back into AI recommendations

---

## The Problem We Solve

### Current State: Code-First, Database-Last

```
Developer → AI Assistant → Application Code → ORM → Database (afterthought)
                                                         ↓
                                              Inefficient schemas
                                              Missing indexes
                                              N+1 queries
                                              No stored procedures
                                              Poor transaction handling
```

### SQL2.AI State: Database-First, AI-Enhanced

```
Developer → SQL2.AI → Data Models → Stored Procedures → Optimized Schema
                          ↓                ↓                    ↓
                   Application Objects  API Layer          Monitoring
                          ↓                ↓                    ↓
                   AI-Generated Code   AI-Optimized        AI-Analyzed
                                       Transactions        Telemetry
```

---

## Core Principles

### 1. Database-First Development
- Schema is the source of truth
- Application models are generated FROM the database, not TO it
- Changes flow: Schema → Migrations → Code regeneration

### 2. Set-Based Optimization
- AI understands relational algebra
- Cursor operations are flagged and refactored
- Batch operations preferred over row-by-row

### 3. Stored Procedures as First-Class Citizens
- Not hidden behind ORMs
- Full AI assistance for SP development
- Automatic documentation generation
- Performance analysis and optimization

### 4. Transaction Contextual Visibility
- LLM sees the full transaction context
- Understands isolation levels and their implications
- Can reason about deadlock potential
- Suggests appropriate locking strategies

### 5. Saga Pattern Support
- Native understanding of distributed transactions
- Compensating transaction generation
- Failure scenario analysis
- State machine visualization

### 6. Telemetry-Driven Optimization
- Query execution telemetry feeds AI
- Index recommendations based on actual usage
- Performance regression detection
- Capacity planning assistance

---

## Product Architecture

### Platform Layers

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SQL2.AI Platform                            │
├─────────────────────────────────────────────────────────────────────┤
│  PRESENTATION LAYER                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  sql2ai.com  │  │  VS Code     │  │  SSMS        │              │
│  │  (Next.js)   │  │  Extension   │  │  Add-in      │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│  API LAYER                                                           │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  SQL2.AI API (FastAPI + .NET Core hybrid)                    │  │
│  │  - Analysis Endpoints                                         │  │
│  │  - Generation Endpoints                                       │  │
│  │  - Monitoring Endpoints                                       │  │
│  │  - MCP Server Endpoints                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│  INTELLIGENCE LAYER                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  SQL Parser  │  │  Schema      │  │  Query       │              │
│  │  & Analyzer  │  │  Reasoner    │  │  Optimizer   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Migration   │  │  Telemetry   │  │  LLM         │              │
│  │  Planner     │  │  Analyzer    │  │  Orchestrator│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
├─────────────────────────────────────────────────────────────────────┤
│  DATA LAYER                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  PostgreSQL  │  │  SQL Server  │  │  Time Series │              │
│  │  (Primary)   │  │  (Support)   │  │  (Telemetry) │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Product Modules

SQL2.AI consists of 8 integrated modules that cover the complete database development lifecycle.
See `/docs/modules/` for detailed specifications of each module.

### Module 1: SQL Orchestrator
**Purpose:** Unified monitoring, security auditing, and compliance checking
**Status:** In Development | **Priority:** P0

**Key Capabilities:**
- Multi-trigger check execution (scheduled, deployment hooks, anomaly-based)
- Performance, security, and compliance checks in one framework
- Schema snapshots for before/after change comparison
- Agent-based distributed collection (extends sql-monitor-agent)
- Automated compliance evidence gathering

**Documentation:** [01-ORCHESTRATOR.md](./modules/01-ORCHESTRATOR.md)

---

### Module 2: SQL Migrator
**Purpose:** Database-first migrations that generate code, not the reverse
**Status:** In Development | **Priority:** P0

**Key Capabilities:**
- Database is source of truth (not code-first ORM)
- Auto-generate Dapper C# models from schema
- Generate TypeScript types for API layer
- Convert DACPAC projects to versioned migrations
- Dependency-aware rollback script generation

**Documentation:** [02-MIGRATOR.md](./modules/02-MIGRATOR.md)

---

### Module 3: SQL Version
**Purpose:** Git-like version control for database objects
**Status:** Planned | **Priority:** P1

**Key Capabilities:**
- Object-level version history (each SP, view tracked separately)
- Diff between any two versions
- Line-by-line blame attribution
- Branch support for environments (dev/staging/prod)
- Merge conflict detection for database objects

**Documentation:** [03-VERSION.md](./modules/03-VERSION.md)

---

### Module 4: SQL Code
**Purpose:** Automated code review, release notes, and AI data dictionary
**Status:** Planned | **Priority:** P1

**Key Capabilities:**
- AI-inferred column and table descriptions
- Auto-generate data dictionaries ("Swagger for Databases")
- Security vulnerability scanning in SQL code
- Automatic release notes from migrations
- OpenAPI-compatible schema export

**Documentation:** [04-CODE.md](./modules/04-CODE.md)

---

### Module 5: SQL Writer
**Purpose:** AI-powered DDL and programmable object generation
**Status:** Planned | **Priority:** P1

**Key Differentiator:** Beyond text-to-SQL. Generates complete stored procedures,
views, functions, and triggers—not just SELECT queries.

**Key Capabilities:**
- Generate complete stored procedures with TRY/CATCH
- Views with optimization hints
- Proper transaction management
- Security best practices built-in
- Full schema context awareness

**Documentation:** [05-WRITER.md](./modules/05-WRITER.md)

---

### Module 6: SSMS Plugin
**Purpose:** Bring AI capabilities directly into SQL Server Management Studio
**Status:** Planned | **Priority:** P2

**Key Capabilities:**
- Inline AI query completions in editor
- Right-click "Explain Query" and "Optimize Query"
- Execution plan analysis with AI explanations
- Generate CRUD procedures from table context
- Local LLM support for air-gapped environments

**Documentation:** [06-SSMS-PLUGIN.md](./modules/06-SSMS-PLUGIN.md)

---

### Module 7: SQL Optimize
**Purpose:** Deep performance analysis with AI-driven remediation
**Status:** Planned | **Priority:** P0

**Key Capabilities:**
- Query Store analysis and plan regression detection
- Parameter sniffing detection and fixes
- Missing, unused, and duplicate index analysis
- Blocking chain and deadlock analysis
- One-click remediation script generation

**Documentation:** [07-OPTIMIZE.md](./modules/07-OPTIMIZE.md)

---

### Module 8: SQL Comply
**Purpose:** Automated compliance checking at the database level
**Status:** Planned | **Priority:** P1

**Supported Frameworks:** SOC 2, HIPAA, PCI-DSS, GDPR, FERPA

**Key Capabilities:**
- Configuration checks (TDE, TLS, audit settings)
- Access control analysis (permissions, orphaned users)
- Data-level PII/PHI scanning with Presidio
- Automated compliance evidence collection
- Framework-specific remediation guidance

**Documentation:** [08-COMPLY.md](./modules/08-COMPLY.md)

---

## Technical Architecture

### Nx Monorepo Structure

```
sql2ai/
├── apps/
│   ├── api/                    # FastAPI + .NET Core API
│   │   ├── src/
│   │   ├── Dockerfile
│   │   └── project.json
│   ├── web/                    # Main SaaS dashboard (Next.js)
│   │   ├── src/
│   │   └── project.json
│   ├── site/                   # Marketing site (sql2aisite)
│   │   ├── src/
│   │   └── project.json
│   ├── vscode-extension/       # VS Code extension
│   │   ├── src/
│   │   └── project.json
│   └── ssms-addin/             # SSMS Add-in (C#)
│       ├── src/
│       └── project.json
│
├── libs/
│   ├── sql-parser/             # SQL parsing library
│   ├── schema-analyzer/        # Schema analysis
│   ├── query-optimizer/        # Query optimization
│   ├── migration-engine/       # Migration generation
│   ├── telemetry-collector/    # Database telemetry
│   ├── llm-orchestrator/       # LLM interaction layer
│   ├── ui-components/          # Shared React components
│   └── shared-types/           # TypeScript type definitions
│
├── packages/
│   ├── sql2ai-cli/             # CLI tool
│   ├── sql2ai-mcp/             # MCP server for Claude
│   └── sql2ai-sdk/             # SDK for integrations
│
├── tools/
│   ├── generators/             # Nx generators
│   └── scripts/                # Build/deploy scripts
│
├── mvp/
│   └── original/               # Original 20 projects (reference)
│       ├── sqlanalyzer/
│       ├── sqlauditor/
│       ├── ... (20 projects)
│
├── docs/
│   ├── VISION.md               # This document
│   ├── ARCHITECTURE.md         # Technical architecture
│   ├── API.md                  # API documentation
│   └── CONTRIBUTING.md         # Contribution guidelines
│
├── .claude/
│   └── CLAUDE.md               # Claude Code instructions
│
├── nx.json                     # Nx configuration
├── package.json                # Root package.json
├── tsconfig.base.json          # Base TypeScript config
└── README.md                   # Project README
```

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend (SaaS) | Next.js 14 (App Router) | Server components, React Server Actions |
| Frontend (Site) | Next.js 14 (App Router) | Vercel deployment, SEO optimized |
| API (Primary) | FastAPI (Python) | Async, OpenAPI, existing Python tools |
| API (Secondary) | ASP.NET Core | SQL Server native, existing C# tools |
| Database | PostgreSQL | Primary platform, open source |
| Database (Support) | SQL Server | Customer databases, existing tooling |
| Telemetry | TimescaleDB | Time-series metrics |
| Cache | Redis | Session, rate limiting |
| Queue | Redis Streams | Async job processing |
| LLM | Claude (Anthropic) | MCP integration, code understanding |
| Monorepo | Nx | Multi-language, task orchestration |
| Deployment | Vercel (site), Azure (API) | Optimal for each workload |

---

## Database-First Development Workflow

### The SQL2.AI Development Cycle

```
1. DESIGN PHASE
   ┌─────────────────────────────────────────────────────────┐
   │  Developer describes data requirements in natural language │
   │                           ↓                               │
   │  SQL2.AI generates normalized schema proposal             │
   │                           ↓                               │
   │  Developer reviews, AI explains tradeoffs                 │
   │                           ↓                               │
   │  Schema finalized with constraints, indexes               │
   └─────────────────────────────────────────────────────────┘

2. BUILD PHASE
   ┌─────────────────────────────────────────────────────────┐
   │  SQL2.AI generates stored procedures from requirements   │
   │                           ↓                               │
   │  Views created for common query patterns                  │
   │                           ↓                               │
   │  Functions generated for computed values                  │
   │                           ↓                               │
   │  Application models generated FROM database               │
   └─────────────────────────────────────────────────────────┘

3. OPTIMIZE PHASE
   ┌─────────────────────────────────────────────────────────┐
   │  Telemetry collected from development queries             │
   │                           ↓                               │
   │  AI analyzes execution plans                              │
   │                           ↓                               │
   │  Index recommendations generated                          │
   │                           ↓                               │
   │  Query rewrites suggested for set-based optimization     │
   └─────────────────────────────────────────────────────────┘

4. DEPLOY PHASE
   ┌─────────────────────────────────────────────────────────┐
   │  Migration scripts generated with rollback               │
   │                           ↓                               │
   │  Dependency order calculated automatically               │
   │                           ↓                               │
   │  Release notes generated from changes                    │
   │                           ↓                               │
   │  Deployment validated in staging                         │
   └─────────────────────────────────────────────────────────┘

5. MONITOR PHASE
   ┌─────────────────────────────────────────────────────────┐
   │  Production telemetry feeds back to AI                   │
   │                           ↓                               │
   │  Performance regressions detected automatically          │
   │                           ↓                               │
   │  Optimization recommendations generated                  │
   │                           ↓                               │
   │  Capacity planning informed by actual usage              │
   └─────────────────────────────────────────────────────────┘
```

---

## Saga Pattern Support

### Native Distributed Transaction Handling

SQL2.AI understands saga patterns natively:

```
┌─────────────────────────────────────────────────────────────┐
│                    Order Processing Saga                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  [Create Order] → [Reserve Inventory] → [Process Payment]   │
│        ↓                   ↓                    ↓            │
│   Compensate:         Compensate:          Compensate:       │
│   Cancel Order        Release Stock        Refund Payment    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Capabilities:**
- Saga state machine generation
- Compensating transaction auto-generation
- Failure scenario simulation
- Dead letter handling
- Idempotency key management

---

## Transaction Contextual Visibility

### What the LLM Sees

Traditional AI assistants see individual queries. SQL2.AI gives the LLM full transaction context:

```sql
-- LLM sees the complete transaction with annotations
BEGIN TRANSACTION
  -- Context: User checkout process, expects < 100ms
  -- Isolation: REPEATABLE READ (required for inventory)
  -- Tables touched: Orders, OrderItems, Inventory, Payments

  INSERT INTO Orders (...) -- Creates order header
  INSERT INTO OrderItems (...) -- Adds line items (set-based from cart)
  UPDATE Inventory SET qty = qty - @ordered -- Atomic decrement
  INSERT INTO Payments (...) -- Payment record

  -- AI understands:
  -- 1. Lock order: Inventory → Orders (potential deadlock if reversed)
  -- 2. Inventory update uses set-based decrement, not row-by-row
  -- 3. Payment insert should be last (compensating transaction order)
COMMIT
```

---

## MCP Integration

### sql2ai-mcp Server

The SQL2.AI MCP server provides Claude with database superpowers:

```typescript
// Available tools via MCP
{
  "tools": [
    {
      "name": "analyze_schema",
      "description": "Analyze database schema and provide recommendations"
    },
    {
      "name": "explain_query",
      "description": "Explain query execution plan with optimization hints"
    },
    {
      "name": "generate_stored_procedure",
      "description": "Generate stored procedure from natural language"
    },
    {
      "name": "compare_schemas",
      "description": "Compare schemas across environments"
    },
    {
      "name": "generate_migration",
      "description": "Generate migration script for schema changes"
    },
    {
      "name": "analyze_telemetry",
      "description": "Analyze query performance telemetry"
    },
    {
      "name": "generate_saga",
      "description": "Generate saga pattern implementation"
    }
  ]
}
```

---

## sql2aisite — Marketing Site Plan

### Purpose
The sql2aisite is the public-facing marketing and documentation site for SQL2.AI, hosted on Vercel.

### Structure

```
apps/site/
├── src/
│   ├── app/
│   │   ├── page.tsx              # Landing page
│   │   ├── pricing/              # Pricing page
│   │   ├── features/             # Feature pages
│   │   ├── docs/                 # Documentation
│   │   ├── blog/                 # Blog (MDX)
│   │   ├── changelog/            # Product changelog
│   │   └── api-reference/        # API docs (OpenAPI)
│   ├── components/
│   │   ├── marketing/            # Marketing components
│   │   ├── docs/                 # Documentation components
│   │   └── shared/               # Shared components
│   └── lib/
│       ├── mdx/                  # MDX processing
│       └── analytics/            # Vercel Analytics
├── content/
│   ├── docs/                     # Documentation MDX files
│   ├── blog/                     # Blog MDX files
│   └── changelog/                # Changelog entries
├── public/
│   ├── images/                   # Static images
│   └── og/                       # OpenGraph images
├── next.config.js
├── tailwind.config.js
└── vercel.json
```

### Key Pages

| Page | Purpose |
|------|---------|
| `/` | Landing page with value proposition |
| `/features` | Detailed feature breakdown |
| `/pricing` | Pricing tiers (Free, Pro, Enterprise) |
| `/docs` | Product documentation |
| `/docs/api` | API reference |
| `/blog` | Engineering blog |
| `/changelog` | Product updates |
| `/demo` | Interactive demo |
| `/contact` | Contact/sales form |

### Tech Stack
- Next.js 14 (App Router)
- Tailwind CSS
- Shadcn/ui components
- MDX for content
- Vercel Analytics
- Vercel Edge Functions

---

## Pricing Model (Planned)

| Tier | Price | Features |
|------|-------|----------|
| **Free** | $0 | 1 database, basic analysis, community support |
| **Pro** | $49/mo | 5 databases, all modules, email support |
| **Team** | $199/mo | 20 databases, team collaboration, priority support |
| **Enterprise** | Custom | Unlimited, SSO, dedicated support, on-prem option |

---

## Roadmap

### Phase 1: Foundation (Current)
- [x] Collect and organize existing SQL tools
- [ ] Set up Nx monorepo
- [ ] Migrate 20 projects to mvp/original
- [ ] Create shared type definitions
- [ ] Establish CLAUDE.md for development

### Phase 2: Core Platform
- [ ] Implement sql-parser library
- [ ] Build schema-analyzer library
- [ ] Create SQL2.AI API (FastAPI)
- [ ] Develop sql2ai-mcp server
- [ ] Build basic web dashboard

### Phase 3: Intelligence Layer
- [ ] Integrate LLM orchestration
- [ ] Implement query optimization recommendations
- [ ] Build migration generation engine
- [ ] Create telemetry collection

### Phase 4: Integrations
- [ ] VS Code extension
- [ ] SSMS add-in (from SSMS-AI)
- [ ] CLI tool
- [ ] SDK for third-party integration

### Phase 5: Launch
- [ ] sql2aisite marketing site
- [ ] Documentation complete
- [ ] Beta program
- [ ] Public launch

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Monthly Active Users | 10,000 (Year 1) |
| Paid Subscribers | 500 (Year 1) |
| Databases Analyzed | 50,000 (Year 1) |
| Queries Optimized | 1M (Year 1) |
| Customer NPS | > 50 |

---

## Competitive Positioning

| Competitor | Their Focus | SQL2.AI Advantage |
|------------|-------------|-------------------|
| Redgate | Traditional SQL tooling | AI-first, LLM integration |
| dbForge | IDE-focused | Platform-agnostic, cloud-native |
| DataGrip | Developer IDE | Database-first philosophy |
| GitHub Copilot | Code generation | SQL/database specialization |

---

*End of Vision Document*
*This is a living document. Update as the product evolves.*
