# SQL2.AI Design Strategy — Revision 2

## Executive Positioning

### The Problem We Solve

Every AI coding assistant today treats databases the same way: as a necessary evil to be abstracted away. They generate ORM migrations, wrap queries in repository patterns, and encourage developers to think of data as objects first, storage second.

**This is backwards.**

The database is not a persistence layer. It is the execution engine. It is where your business logic should live. It is the source of truth.

### Our Thesis

> **Data models drive application objects, not the reverse.**

SQL2.AI is the first AI platform built on this principle. We don't help you escape your database—we help you master it.

### The Competitive Gap

| Current Tools | SQL2.AI |
|--------------|---------|
| Generate ORM migrations | Generate database-native DDL |
| Abstract away SQL | Optimize and enhance SQL |
| Treat procedures as legacy | Treat procedures as first-class |
| Single database focus | SQL Server ↔ PostgreSQL bridging |
| Point solutions | Full lifecycle platform |
| Chat-based interface | Developer workflow integration |

---

## The SQL2.AI Lifecycle

This is our core differentiator. Not a single tool, but a complete methodology:

```
                         ┌─────────────┐
                         │   DESIGN    │
                         │  (schema)   │
                         └──────┬──────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
  ┌──────────┐           ┌──────────┐           ┌──────────┐
  │ ANALYZE  │───────────│ OPTIMIZE │───────────│ REFACTOR │
  │          │           │          │           │          │
  │ • Schema │           │ • Plans  │           │ • Cursor │
  │ • Deps   │           │ • Queries│           │   to Set │
  │ • Compat │           │ • Index  │           │ • Decomp │
  └──────────┘           └──────────┘           └──────────┘
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
                         ┌──────┴──────┐
                         │  DOCUMENT   │
                         │             │
                         │ • ERD       │
                         │ • Dictionary│
                         │ • Changes   │
                         └──────┬──────┘
                                │
                         ┌──────┴──────┐
                         │   VERSION   │
                         │             │
                         │ • Migrations│
                         │ • Rollbacks │
                         │ • Drift     │
                         └──────┬──────┘
                                │
                         ┌──────┴──────┐
                         │   DEPLOY    │
                         │             │
                         │ • Execute   │
                         │ • Verify    │
                         │ • Rollback  │
                         └─────────────┘
```

---

## Cross-Platform Bridging

A key differentiator: SQL Server ↔ PostgreSQL translation with full context.

### What We Translate

| Category | SQL Server | PostgreSQL |
|----------|------------|------------|
| Data Types | NVARCHAR(MAX) | TEXT |
| Identity | IDENTITY(1,1) | SERIAL / GENERATED |
| Pagination | OFFSET FETCH | LIMIT OFFSET |
| Strings | + concatenation | \|\| concatenation |
| Booleans | BIT | BOOLEAN |
| Date/Time | DATETIME2 | TIMESTAMP |
| JSON | OPENJSON | jsonb operators |
| CTEs | WITH (NOLOCK) hints | Different locking |
| Procedures | CREATE PROCEDURE | CREATE FUNCTION |

### What We Preserve

- Transaction semantics
- Isolation level behavior
- Lock ordering recommendations
- Index strategy translations
- Constraint mappings

### The Bridge Workflow

```
SQL Server Schema                    PostgreSQL Schema
      │                                    ▲
      ▼                                    │
┌─────────────────────────────────────────────────────┐
│                  SQL2.AI Bridge                     │
│                                                     │
│  1. Parse source dialect                            │
│  2. Build semantic model                            │
│  3. Identify platform-specific patterns             │
│  4. Generate target dialect                         │
│  5. Verify semantic equivalence                     │
│  6. Document differences                            │
└─────────────────────────────────────────────────────┘
```

---

## Developer Workflow Integration

SQL2.AI meets developers where they work:

### 1. CLI (sql2ai)
```bash
# Analyze schema
sql2ai analyze --connection "postgres://..." --output schema.json

# Optimize query
sql2ai optimize --file slow-query.sql --dialect postgresql

# Generate migration
sql2ai migrate --from prod --to staging --output migrations/

# Check compatibility
sql2ai bridge --source sqlserver --target postgres --file procedures/
```

### 2. MCP Server (Claude Code Integration)
```
Claude: "Analyze the Orders table and suggest indexes"

SQL2.AI MCP → Connects to database
            → Analyzes table structure
            → Examines query patterns
            → Returns index recommendations

Claude: "I found 3 opportunities:
         1. Covering index on (CustomerId, OrderDate) INCLUDE (Total)
         2. Remove duplicate index IX_Orders_Date
         3. Consider filtered index for Status = 'Pending'"
```

### 3. IDE Extensions
- VS Code: SQL file analysis, inline suggestions
- SSMS: Right-click menu integration
- DataGrip: Plugin for optimization

### 4. CI/CD Integration
```yaml
# GitHub Actions example
- name: SQL2.AI Schema Check
  uses: sql2ai/action@v1
  with:
    command: migrate
    source: ${{ secrets.PROD_CONNECTION }}
    target: ./migrations/
    fail-on-breaking: true
```

---

## Visual Identity: The Technical Aesthetic

### Design Philosophy

We design for developers who:
- Appreciate information density
- Prefer dark mode
- Value precision over prettiness
- Want to see real code, real numbers
- Distrust "magic"

### Color System

**Core Palette:**
```css
--background: #0a0a14;      /* Near black, not pure */
--surface: #12121e;         /* Elevated surfaces */
--surface-hover: #1a1a2e;   /* Interactive states */
--border: #2a2a3e;          /* Subtle borders */
--text-primary: #f0f0f5;    /* Main content */
--text-secondary: #8888a0;  /* Supporting text */
--text-muted: #5555670;     /* Disabled, hints */
```

**Action Colors:**
```css
--primary: #3b82f6;         /* Blue - primary actions */
--primary-hover: #2563eb;   /* Blue - hover state */
--success: #22c55e;         /* Green - positive changes */
--warning: #eab308;         /* Yellow - caution */
--error: #ef4444;           /* Red - breaking changes */
```

**Platform Colors:**
```css
--postgresql: #336791;      /* PostgreSQL brand */
--sqlserver: #cc2927;       /* SQL Server brand */
```

**Diff Colors:**
```css
--diff-add-bg: rgba(34, 197, 94, 0.15);
--diff-add-text: #22c55e;
--diff-remove-bg: rgba(239, 68, 68, 0.15);
--diff-remove-text: #ef4444;
--diff-change-bg: rgba(234, 179, 8, 0.15);
--diff-change-text: #eab308;
```

### Typography System

**Headings:**
- Font: Inter (variable)
- H1: 48px / 600 weight / -0.02em tracking
- H2: 36px / 600 weight / -0.02em tracking
- H3: 28px / 600 weight / -0.01em tracking
- H4: 22px / 500 weight / normal tracking

**Body:**
- Font: Inter
- Regular: 16px / 400 weight / 1.6 line-height
- Small: 14px / 400 weight / 1.5 line-height

**Code:**
- Font: JetBrains Mono
- Size: 14px
- Weight: 400
- Ligatures: enabled

### Component Library Selection

**Base: shadcn/ui + Tailwind CSS**

Why shadcn/ui:
- Radix primitives (accessibility)
- Copy-paste ownership (not a dependency)
- Tailwind-native (matches our stack)
- Dark mode excellent

**Components to implement:**

| Component | Priority | Notes |
|-----------|----------|-------|
| Command (⌘K) | High | Search, quick actions |
| CodeBlock | High | Custom with SQL highlighting |
| Tabs | High | Feature sections |
| Card | High | Feature highlights |
| Table | High | Comparisons, pricing |
| Dialog | Medium | Modals, confirmations |
| Sheet | Medium | Mobile navigation |
| Tooltip | Medium | Feature explanations |
| Badge | Medium | Status, tiers |
| Accordion | Low | FAQs |

**Custom Components to Build:**

| Component | Description |
|-----------|-------------|
| SchemaViewer | Interactive ERD with pan/zoom |
| ExecutionPlan | Tree visualization of query plans |
| QueryDiff | Side-by-side with highlighting |
| LifecycleIndicator | Current stage in workflow |
| TerminalBlock | CLI-styled code display |
| MetricCard | KPI with trend indicator |
| PlatformBadge | PostgreSQL/SQL Server indicator |

---

## prompt2image Specifications

### Image 1: Hero Schema Visualization

**Prompt:**
```
Technical diagram of a database schema visualization interface, dark theme (#0a0a14 background), showing interconnected database tables with column names and data types visible, foreign key relationships shown as connecting lines, one table highlighted in blue (#3b82f6) showing it's selected, subtle grid pattern in background, professional software UI aesthetic, no text labels outside the diagram, clean vector style, 16:9 aspect ratio
```

**Purpose:** Hero background or feature section
**Size:** 1920x1080

### Image 2: Query Optimization Before/After

**Prompt:**
```
Split-screen code comparison interface, left side shows SQL query with red highlighting indicating problems, right side shows optimized SQL query with green highlighting indicating improvements, dark code editor theme, syntax highlighting for SQL keywords in blue, strings in orange, line numbers visible, performance metrics badge showing "3.2s → 0.1s" improvement, professional developer tool aesthetic, 16:9 aspect ratio
```

**Purpose:** Optimization feature showcase
**Size:** 1920x1080

### Image 3: Execution Plan Tree

**Prompt:**
```
Database query execution plan visualization, tree structure flowing top to bottom, nodes representing operations like "Index Seek", "Nested Loop", "Sort", each node showing percentage cost, one node highlighted in red indicating bottleneck, connecting lines between nodes, dark background (#12121e), blue accent colors for nodes, professional data visualization style, technical diagram aesthetic, 4:3 aspect ratio
```

**Purpose:** Analysis feature showcase
**Size:** 1200x900

### Image 4: CLI in Terminal

**Prompt:**
```
Terminal window screenshot showing command-line interface, dark terminal theme with subtle transparency, command prompt showing "sql2ai analyze --connection" command, output showing colorized results with green checkmarks for passed checks and yellow warnings, ASCII table showing table names and row counts, professional developer terminal aesthetic, macOS-style window chrome, 16:9 aspect ratio
```

**Purpose:** CLI feature showcase
**Size:** 1920x1080

### Image 5: Platform Bridge Diagram

**Prompt:**
```
Technical architecture diagram showing SQL Server logo on left and PostgreSQL elephant logo on right, connected by flowing lines through a central processing block labeled with gear icons, data transformation symbols along the path, bidirectional arrows indicating two-way translation, dark background, blue (#3b82f6) accent colors, clean vector illustration style, professional technical documentation aesthetic, 16:9 aspect ratio
```

**Purpose:** Cross-platform feature
**Size:** 1920x1080

### Image 6: MCP Integration with Claude

**Prompt:**
```
Software interface mockup showing split view, left side is a code editor with SQL query, right side shows an AI assistant conversation with database schema context visible, dark theme throughout, subtle connection lines indicating the AI understands the database structure, professional developer tool aesthetic, no visible branding, clean UI with proper spacing, 16:9 aspect ratio
```

**Purpose:** AI integration feature
**Size:** 1920x1080

### Image 7: Lifecycle Infographic

**Prompt:**
```
Circular workflow diagram with 7 connected stages: Analyze, Optimize, Refactor, Index, Document, Version, Deploy, each stage represented by a minimal icon in a hexagonal node, connecting arrows between stages, one stage (Analyze) highlighted in blue to show current position, dark background with subtle gradient, professional infographic style, clean vector aesthetic, square aspect ratio
```

**Purpose:** Lifecycle explanation
**Size:** 1200x1200

---

## Page Structure Specifications

### Homepage Sections

```
1. HERO
   - Headline: "Database Development, Powered by AI"
   - Subheadline: "The complete lifecycle platform for SQL Server and PostgreSQL"
   - Primary CTA: "Start Free Trial"
   - Secondary CTA: "See How It Works"
   - Background: Subtle schema pattern (prompt2image #1)

2. PROBLEM/SOLUTION
   - "Most AI tools abstract away your database. We help you master it."
   - Three columns contrasting approaches

3. LIFECYCLE OVERVIEW
   - Interactive lifecycle diagram
   - Hover states reveal details
   - Links to feature deep-dives

4. PLATFORM BRIDGE
   - SQL Server ↔ PostgreSQL messaging
   - Translation example
   - Compatibility highlight

5. FEATURE CARDS
   - Analyze (with execution plan visual)
   - Optimize (with before/after)
   - Version (with migration diff)
   - Integrate (with MCP/CLI examples)

6. HOW IT WORKS
   - Three steps: Connect → Analyze → Improve
   - Code examples at each step

7. TRUST INDICATORS
   - Database platform logos
   - Key metrics
   - Enterprise-ready messaging

8. PRICING PREVIEW
   - Three tiers
   - Link to full pricing page

9. CTA
   - Final conversion push
   - "Start optimizing your database today"
```

### Documentation Structure

```
docs/
├── getting-started/
│   ├── quickstart.mdx
│   ├── installation.mdx
│   └── first-analysis.mdx
├── concepts/
│   ├── database-first.mdx
│   ├── set-based-thinking.mdx
│   ├── transaction-context.mdx
│   └── cross-platform.mdx
├── features/
│   ├── schema-analyzer.mdx
│   ├── query-optimizer.mdx
│   ├── migration-engine.mdx
│   ├── telemetry.mdx
│   └── versioning.mdx
├── integrations/
│   ├── mcp-claude.mdx
│   ├── cli.mdx
│   ├── vscode.mdx
│   ├── ssms.mdx
│   └── cicd.mdx
├── api/
│   ├── rest-api.mdx
│   ├── sdk.mdx
│   └── webhooks.mdx
└── reference/
    ├── sql-patterns.mdx
    ├── type-mappings.mdx
    └── troubleshooting.mdx
```

---

## Figma/Design Resources to Acquire

### From Figma Community

1. **Untitled UI** — Clean component system, good dark mode
2. **Horizon UI Dashboard** — Data visualization patterns
3. **Raycast UI Kit** — Command palette patterns
4. **Linear Clone** — Developer tool aesthetics

### From GitHub/npm

1. **cmdk** — Command palette implementation
2. **reactflow** — For schema visualization
3. **@visx/visx** — For execution plan visualization
4. **shiki** — For SQL syntax highlighting

### Typography

1. **Inter** — Variable font from Google Fonts
2. **JetBrains Mono** — From JetBrains, free

### Icons

1. **Lucide** — Consistent, clean icon set
2. **Simple Icons** — Brand logos (PostgreSQL, SQL Server)

---

## Implementation Checklist

### Phase 1: Foundation
- [ ] Set up Tailwind config with custom colors
- [ ] Install and configure shadcn/ui
- [ ] Create typography scale
- [ ] Build CodeBlock component with Shiki
- [ ] Build TerminalBlock component

### Phase 2: Core Components
- [ ] Build SchemaViewer with ReactFlow
- [ ] Build ExecutionPlan tree component
- [ ] Build QueryDiff component
- [ ] Build LifecycleIndicator
- [ ] Build PlatformBadge (PostgreSQL/SQL Server)

### Phase 3: Page Templates
- [ ] Build Homepage layout
- [ ] Build Features page layout
- [ ] Build Documentation layout
- [ ] Build Pricing page layout

### Phase 4: Content
- [ ] Write homepage copy
- [ ] Write feature descriptions
- [ ] Create code examples
- [ ] Generate images with prompt2image

### Phase 5: Polish
- [ ] Add animations (Framer Motion)
- [ ] Implement dark/light mode toggle
- [ ] Optimize performance (Lighthouse)
- [ ] Add SEO metadata

---

*Revision 2 — Ready for final polish*
