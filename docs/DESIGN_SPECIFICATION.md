# SQL2.AI Design Specification
## Final Version — Production Ready

---

## 1. Strategic Positioning

### 1.1 The Core Thesis

> **"Data models drive application objects, not the reverse."**

SQL2.AI is built on the principle that databases are not persistence layers to be abstracted away—they are the execution engine where business logic belongs. Every design decision flows from this philosophy.

### 1.2 Market Position

| Dimension | Our Position |
|-----------|--------------|
| **Philosophy** | Database-first, not ORM-first |
| **Scope** | Full lifecycle, not point solutions |
| **Platforms** | SQL Server + PostgreSQL, not single-vendor |
| **Integration** | Workflow-native (CLI, MCP, IDE), not standalone app |
| **Audience** | Experienced developers, DBAs, architects |
| **Aesthetic** | Technical credibility, not consumer-friendly |

### 1.3 Competitive Differentiation

**Against ORM-based AI tools (Copilot, Cursor for ORMs):**
- We generate database-native SQL, not migrations
- We optimize stored procedures, not repositories
- We understand transaction isolation, not just CRUD

**Against point solutions (SSMS advisors, pgAdmin):**
- Full lifecycle coverage, not single-phase
- Cross-platform translation, not vendor lock-in
- AI-powered insights, not rule-based suggestions

**Against database AI chatbots:**
- Workflow integration (CLI, MCP), not chat windows
- Versioned migrations, not one-off suggestions
- Enterprise deployment support, not playground

---

## 2. The Complete Lifecycle

### 2.1 Seven Stages

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐          │
│    │ ANALYZE  │────▶│ OPTIMIZE │────▶│ REFACTOR │          │
│    └──────────┘     └──────────┘     └──────────┘          │
│          │                                  │               │
│          │         ┌──────────┐            │               │
│          └────────▶│  INDEX   │◀───────────┘               │
│                    └──────────┘                            │
│                          │                                 │
│                    ┌──────────┐                            │
│                    │ DOCUMENT │                            │
│                    └──────────┘                            │
│                          │                                 │
│                    ┌──────────┐                            │
│                    │ VERSION  │                            │
│                    └──────────┘                            │
│                          │                                 │
│                    ┌──────────┐                            │
│                    │  DEPLOY  │                            │
│                    └──────────┘                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Stage Details

| Stage | Capabilities | AI Role |
|-------|--------------|---------|
| **ANALYZE** | Schema structure, dependencies, patterns, compatibility | Identifies anti-patterns, N+1 risks, implicit conversions |
| **OPTIMIZE** | Execution plans, query rewriting, set-based conversion | Suggests rewrites, explains plan bottlenecks |
| **REFACTOR** | Cursor removal, procedure decomposition, normalization | Generates set-based alternatives |
| **INDEX** | Missing indexes, covering indexes, unused detection | Recommends based on query patterns |
| **DOCUMENT** | ERD, data dictionary, change tracking | Generates descriptions, documents intent |
| **VERSION** | Migrations, rollbacks, drift detection | Generates scripts, identifies breaking changes |
| **DEPLOY** | Execution, verification, rollback automation | Validates safety, suggests deployment order |

---

## 3. Cross-Platform Bridge

### 3.1 SQL Server ↔ PostgreSQL Translation

**Semantic Preservation:**
- Transaction behavior maintained
- Isolation level semantics preserved
- Lock ordering documented
- Error handling translated

**Syntax Translation:**

| Concept | SQL Server | PostgreSQL |
|---------|------------|------------|
| Identity | `IDENTITY(1,1)` | `SERIAL` / `GENERATED ALWAYS` |
| Top N | `TOP 10` | `LIMIT 10` |
| String concat | `'a' + 'b'` | `'a' \|\| 'b'` |
| Temp tables | `#temp` | `TEMP TABLE` |
| Date parts | `DATEPART(year, @d)` | `EXTRACT(year FROM d)` |
| If exists | `IF EXISTS(SELECT...)` | `EXISTS(SELECT...)` |
| Procedures | `CREATE PROCEDURE` | `CREATE FUNCTION` (with caveats) |
| Output params | `OUTPUT` | `OUT` / `INOUT` |

**What Cannot Be Translated (Documented Clearly):**
- CLR stored procedures
- Linked servers
- Service Broker
- Some system functions

---

## 4. Visual Design System

### 4.1 Design Principles

1. **Technical Credibility** — Real code, real metrics, real diagrams
2. **Information Density** — Developers appreciate completeness
3. **Dark-Mode Native** — Terminal aesthetic as default
4. **Precision** — Exact numbers, not approximations
5. **No Magic** — Explainable AI, not black box

### 4.2 Color Tokens

```css
/* Background layers */
--color-bg-base: #09090f;
--color-bg-surface: #111118;
--color-bg-elevated: #18181f;
--color-bg-overlay: #1f1f27;

/* Borders */
--color-border-subtle: #27272f;
--color-border-default: #3f3f47;
--color-border-emphasis: #52525b;

/* Text */
--color-text-primary: #fafafa;
--color-text-secondary: #a1a1aa;
--color-text-muted: #71717a;
--color-text-disabled: #52525b;

/* Interactive */
--color-primary: #3b82f6;
--color-primary-hover: #2563eb;
--color-primary-muted: #1d4ed8;

/* Semantic */
--color-success: #22c55e;
--color-success-muted: #166534;
--color-warning: #eab308;
--color-warning-muted: #854d0e;
--color-error: #ef4444;
--color-error-muted: #991b1b;

/* Platform */
--color-postgresql: #336791;
--color-sqlserver: #cc2927;

/* Diff */
--color-diff-add-bg: rgba(34, 197, 94, 0.12);
--color-diff-add-border: rgba(34, 197, 94, 0.3);
--color-diff-remove-bg: rgba(239, 68, 68, 0.12);
--color-diff-remove-border: rgba(239, 68, 68, 0.3);
--color-diff-change-bg: rgba(234, 179, 8, 0.12);
--color-diff-change-border: rgba(234, 179, 8, 0.3);
```

### 4.3 Typography Scale

```css
/* Headings - Inter */
--font-heading: 'Inter', system-ui, sans-serif;
--text-h1: 3rem;      /* 48px */
--text-h2: 2.25rem;   /* 36px */
--text-h3: 1.75rem;   /* 28px */
--text-h4: 1.375rem;  /* 22px */
--text-h5: 1.125rem;  /* 18px */
--weight-heading: 600;
--tracking-heading: -0.02em;

/* Body - Inter */
--font-body: 'Inter', system-ui, sans-serif;
--text-body: 1rem;    /* 16px */
--text-small: 0.875rem; /* 14px */
--text-xs: 0.75rem;   /* 12px */
--weight-body: 400;
--line-height-body: 1.6;

/* Code - JetBrains Mono */
--font-code: 'JetBrains Mono', 'Fira Code', monospace;
--text-code: 0.875rem; /* 14px */
--weight-code: 400;
--line-height-code: 1.5;
```

### 4.4 Spacing Scale

```css
--space-0: 0;
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

---

## 5. Component Specifications

### 5.1 Base Components (shadcn/ui)

Install and customize:
```bash
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card tabs badge tooltip dialog sheet command accordion table
```

### 5.2 Custom Components

#### CodeBlock
```typescript
interface CodeBlockProps {
  code: string;
  language: 'sql' | 'typescript' | 'bash' | 'json';
  filename?: string;
  showLineNumbers?: boolean;
  highlightLines?: number[];
  diffMode?: 'add' | 'remove' | 'change';
}
```
- Uses Shiki for syntax highlighting
- Server-side rendered for performance
- Copy button
- Optional line highlighting

#### TerminalBlock
```typescript
interface TerminalBlockProps {
  commands: Array<{
    prompt?: string;
    command: string;
    output?: string;
  }>;
  title?: string;
}
```
- macOS-style window chrome
- Animated typing effect (optional)
- Copy command button

#### SchemaViewer
```typescript
interface SchemaViewerProps {
  tables: TableDefinition[];
  relationships: Relationship[];
  highlightTable?: string;
  onTableSelect?: (table: string) => void;
}
```
- Built with ReactFlow
- Pan and zoom
- Table detail popover on click
- Relationship lines with cardinality

#### ExecutionPlanTree
```typescript
interface ExecutionPlanTreeProps {
  plan: PlanNode;
  highlightBottlenecks?: boolean;
  showActualMetrics?: boolean;
}
```
- Tree layout top-to-bottom
- Color-coded by cost percentage
- Expandable node details
- Bottleneck highlighting

#### QueryDiff
```typescript
interface QueryDiffProps {
  original: string;
  optimized: string;
  mode: 'split' | 'unified';
  metrics?: {
    originalTime: number;
    optimizedTime: number;
  };
}
```
- Side-by-side or unified view
- Line-by-line diff highlighting
- Performance improvement badge

#### LifecycleIndicator
```typescript
interface LifecycleIndicatorProps {
  currentStage: LifecycleStage;
  completedStages: LifecycleStage[];
  interactive?: boolean;
}
```
- Visual progress through lifecycle
- Click to navigate (if interactive)
- Tooltips with stage descriptions

#### PlatformBadge
```typescript
interface PlatformBadgeProps {
  platform: 'postgresql' | 'sqlserver' | 'both';
  size?: 'sm' | 'md' | 'lg';
}
```
- Platform logo + name
- Colored to match platform identity

#### MetricCard
```typescript
interface MetricCardProps {
  label: string;
  value: string | number;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: string;
  icon?: ReactNode;
}
```
- Large value display
- Trend indicator
- Optional icon

---

## 6. Image Specifications (prompt2image)

### 6.1 Hero: Schema Visualization
**Dimensions:** 1920x1080
**Prompt:**
```
A sophisticated database schema visualization on a near-black background (#09090f), showing 6-8 interconnected tables as rounded rectangles with subtle borders, each containing visible column names in small monospace text, tables connected by thin lines representing foreign keys, one table highlighted with a blue glow (#3b82f6), subtle dot grid pattern in background at 5% opacity, professional enterprise software aesthetic, clean vector style, no labels outside diagram area, cinematic lighting
```

### 6.2 Query Optimization Before/After
**Dimensions:** 1920x1080
**Prompt:**
```
Split screen code editor interface on dark background, left panel titled "Original" showing SQL query with sections highlighted in subtle red tint indicating inefficiencies, right panel titled "Optimized" showing cleaner SQL with green highlighted improvements, syntax highlighting with blue keywords and orange strings, line numbers visible, floating badge between panels showing "94% faster" with arrow, professional developer tool aesthetic, photorealistic software screenshot style
```

### 6.3 Execution Plan Visualization
**Dimensions:** 1200x900
**Prompt:**
```
Database query execution plan as flowing tree diagram on dark charcoal background, nodes are rounded rectangles labeled with operations like "Index Seek" and "Hash Match", each node shows percentage cost in corner, nodes connected by lines with data flow arrows, one node glowing red indicating the bottleneck (47% cost), cool blue accents on non-bottleneck nodes, clean technical diagram style, enterprise software aesthetic
```

### 6.4 Terminal CLI
**Dimensions:** 1600x900
**Prompt:**
```
macOS terminal window with title bar buttons visible, semi-transparent dark background showing blurred desktop, inside terminal is command "sql2ai analyze --connection postgres://localhost/mydb", below shows colorized output with green checkmarks, yellow warning symbols, and a formatted ASCII table of results, professional developer screenshot, realistic terminal emulator appearance
```

### 6.5 Cross-Platform Bridge
**Dimensions:** 1920x800
**Prompt:**
```
Technical diagram showing SQL Server logo (red) on left and PostgreSQL elephant logo (blue) on right, connected through a central hub with glowing data streams, binary/code particles flowing between them, transformation symbols along the path, dark background with subtle tech grid, professional enterprise software illustration style, vector art aesthetic
```

### 6.6 MCP Integration
**Dimensions:** 1920x1080
**Prompt:**
```
Modern IDE interface on dark theme showing code editor on left with SQL query visible, right panel shows AI assistant response with database context, visible schema tree sidebar showing table icons, subtle connection visualization between code and AI response, professional developer tool aesthetic, realistic software interface, no visible branding or logos
```

### 6.7 Lifecycle Diagram
**Dimensions:** 1200x1200
**Prompt:**
```
Circular workflow infographic with 7 hexagonal nodes arranged in a circle, each node contains a minimal line icon (magnifying glass for Analyze, gauge for Optimize, wrench for Refactor, list for Index, document for Document, branch for Version, rocket for Deploy), nodes connected by curved arrows, "Analyze" node highlighted in blue, dark background with subtle radial gradient, clean vector infographic style
```

---

## 7. Page Architecture

### 7.1 Homepage Structure

```
┌─────────────────────────────────────────────────────────────┐
│ NAVIGATION                                                  │
│ Logo | Features | Pricing | Docs | Blog | Login | Sign Up   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ HERO                                                        │
│                                                             │
│ Database Development,                                       │
│ Powered by AI                                               │
│                                                             │
│ The complete lifecycle platform for SQL Server              │
│ and PostgreSQL — from analysis to deployment.               │
│                                                             │
│ [Start Free Trial]  [Watch Demo]                            │
│                                                             │
│ Background: Schema visualization image                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PHILOSOPHY                                                  │
│                                                             │
│ Most AI tools help you escape your database.                │
│ We help you master it.                                      │
│                                                             │
│ [ORM Approach]     vs     [SQL2.AI Approach]                │
│ Generate migrations       Generate native DDL               │
│ Abstract away SQL         Optimize SQL                      │
│ Ignore procedures         Procedures first-class            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ LIFECYCLE                                                   │
│                                                             │
│ The Complete Database Development Lifecycle                 │
│                                                             │
│ [Interactive lifecycle diagram - 7 stages]                  │
│                                                             │
│ Hover each stage for details                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PLATFORMS                                                   │
│                                                             │
│ One Platform. Two Databases. Zero Compromises.              │
│                                                             │
│ [PostgreSQL logo] ←→ [SQL2.AI Bridge] ←→ [SQL Server logo]  │
│                                                             │
│ Translate between platforms with full context               │
│ preservation: transactions, isolation, and semantics.       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FEATURES                                                    │
│                                                             │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐            │
│ │  ANALYZE    │ │  OPTIMIZE   │ │  VERSION    │            │
│ │             │ │             │ │             │            │
│ │ Schema deep │ │ Query perf  │ │ Migrations  │            │
│ │ dive with   │ │ with AI     │ │ with full   │            │
│ │ pattern     │ │ suggestions │ │ rollback    │            │
│ │ detection   │ │             │ │ support     │            │
│ └─────────────┘ └─────────────┘ └─────────────┘            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ INTEGRATION                                                 │
│                                                             │
│ Works Where You Work                                        │
│                                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│ │   CLI    │ │   MCP    │ │  VS Code │ │  CI/CD   │       │
│ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│                                                             │
│ Terminal command example                                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ PRICING PREVIEW                                             │
│                                                             │
│ ┌──────────┐ ┌──────────┐ ┌──────────┐                     │
│ │  Free    │ │   Pro    │ │  Team    │  Enterprise →      │
│ │   $0     │ │   $29    │ │   $99    │                     │
│ └──────────┘ └──────────┘ └──────────┘                     │
│                                                             │
│ [See Full Pricing]                                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ CTA                                                         │
│                                                             │
│ Ready to Master Your Database?                              │
│                                                             │
│ [Start Free Trial — No Credit Card Required]                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ FOOTER                                                      │
│                                                             │
│ SQL2.AI | Product | Resources | Company | Legal             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Key Messaging by Page

| Page | Primary Message | CTA |
|------|-----------------|-----|
| **Home** | "Database development, powered by AI" | Start Free Trial |
| **Features** | "The complete lifecycle" | Try This Feature |
| **Pricing** | "Plans for every team" | Get Started |
| **Docs** | "Learn to master your database" | Copy Code |
| **Blog** | "Insights from database experts" | Read More |

---

## 8. Technology Stack

### 8.1 Core Dependencies

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "latest",
    "framer-motion": "^11.0.0",
    "shiki": "^1.0.0",
    "@tanstack/react-table": "^8.0.0",
    "reactflow": "^11.0.0",
    "lucide-react": "^0.300.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "tailwind-merge": "^2.2.0"
  }
}
```

### 8.2 Development Dependencies

```json
{
  "devDependencies": {
    "typescript": "^5.4.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.0.0",
    "eslint": "^8.57.0",
    "prettier": "^3.2.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Configure Tailwind with design tokens
- [ ] Set up shadcn/ui components
- [ ] Create typography components
- [ ] Build CodeBlock with Shiki
- [ ] Build TerminalBlock
- [ ] Create layout components (Header, Footer, Container)

### Phase 2: Marketing Components (Week 2)
- [ ] Build Hero section
- [ ] Build FeatureCard grid
- [ ] Build PricingTable
- [ ] Build LifecycleIndicator
- [ ] Build PlatformBadge
- [ ] Build CTASection

### Phase 3: Technical Components (Week 3)
- [ ] Build SchemaViewer with ReactFlow
- [ ] Build ExecutionPlanTree
- [ ] Build QueryDiff
- [ ] Build MetricCard
- [ ] Build IntegrationShowcase

### Phase 4: Pages (Week 4)
- [ ] Complete Homepage
- [ ] Complete Features page
- [ ] Complete Pricing page
- [ ] Set up Documentation structure

### Phase 5: Content & Polish (Week 5)
- [ ] Write all copy
- [ ] Generate images with prompt2image
- [ ] Add animations
- [ ] Optimize performance
- [ ] SEO metadata

### Phase 6: Launch Prep (Week 6)
- [ ] Cross-browser testing
- [ ] Mobile testing
- [ ] Accessibility audit
- [ ] Performance audit (Lighthouse)
- [ ] Final review

---

## 10. Success Metrics

### Design Goals

| Metric | Target |
|--------|--------|
| Lighthouse Performance | > 95 |
| Lighthouse Accessibility | > 95 |
| First Contentful Paint | < 1.0s |
| Largest Contentful Paint | < 2.0s |
| Time to Interactive | < 2.5s |
| Cumulative Layout Shift | < 0.05 |

### Conversion Goals

| Funnel Step | Target |
|-------------|--------|
| Homepage → Features | 40% |
| Homepage → Pricing | 25% |
| Homepage → Sign Up | 5% |
| Pricing → Sign Up | 15% |
| Any Page → Docs | 20% |

---

*This document is the authoritative design specification for SQL2.AI marketing site.*
*Last updated: December 2024*
