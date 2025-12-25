# SQL2.AI Design Strategy — Draft 1

## The Positioning Challenge

Most AI coding tools treat databases as an afterthought—something to generate ORM migrations for. SQL2.AI must communicate a fundamentally different philosophy:

**The database is not a persistence layer. It is the source of truth.**

This positioning requires visual language that:
1. Establishes technical credibility immediately
2. Speaks to developers who understand database complexity
3. Differentiates from "AI wrapper" products
4. Conveys depth without overwhelming

---

## Core Positioning: The Full Lifecycle

SQL2.AI is not a single tool. It's a complete lifecycle platform:

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL2.AI LIFECYCLE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ANALYZE ──► OPTIMIZE ──► REFACTOR ──► INDEX ──► DOCUMENT     │
│       │                                               │         │
│       │                                               │         │
│       └──────────────── VERSION ◄─────────────────────┘         │
│                            │                                    │
│                            ▼                                    │
│                         DEPLOY                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1. ANALYZE
- Schema structure analysis
- Dependency graph visualization
- Pattern detection (N+1, cursor abuse, implicit conversions)
- Cross-platform compatibility checking (SQL Server ↔ PostgreSQL)
- Data type mapping and translation

### 2. OPTIMIZE
- Execution plan interpretation
- Query rewriting suggestions
- Set-based alternatives to procedural code
- Parameter sniffing detection
- Sargability analysis

### 3. REFACTOR
- Cursor-to-set conversion
- Dead code detection
- Normalization suggestions
- Stored procedure decomposition
- Transaction scope optimization

### 4. INDEX
- Missing index recommendations
- Covering index suggestions
- Unused index detection
- Index consolidation opportunities
- Filtered index recommendations

### 5. DOCUMENT
- Auto-generated schema documentation
- ERD generation
- Data dictionary creation
- Dependency documentation
- Change history tracking

### 6. VERSION
- Schema versioning (not ORM migrations)
- Migration script generation
- Rollback script generation
- Drift detection
- Breaking change analysis

### 7. DEPLOY
- Migration execution with safety checks
- Online schema change support
- Rollback automation
- Environment promotion
- Deployment verification

---

## Developer-First, Database-First Messaging

### Primary Message
> "AI that understands your database the way you do."

### Supporting Messages

**For the skeptical DBA:**
> "We don't generate ORM migrations. We generate SQL that respects your architecture."

**For the performance-obsessed developer:**
> "Set-based thinking, not cursor crutches. Real optimization, not syntax sugar."

**For the cross-platform team:**
> "SQL Server to PostgreSQL. PostgreSQL to SQL Server. With full context preservation."

**For the enterprise architect:**
> "Transaction-aware. Isolation-level conscious. Deadlock-preventing."

---

## Visual Design Principles

### What We ARE
- **Technical** — Real code, real execution plans, real metrics
- **Dense** — Developers appreciate information density
- **Precise** — Exact numbers, not "approximately faster"
- **Dark-mode native** — Terminal aesthetics, not consumer app
- **Diagrammatic** — Schema relationships, dependency graphs, execution flows

### What We ARE NOT
- **Chatbot-shaped** — No chat bubbles on marketing pages
- **Magic-wand AI** — No sparkles, no "AI generated this!" badges
- **Consumer-friendly** — Not dumbed down, not over-explained
- **Gradient-heavy** — No purple-to-blue AI aesthetic
- **Stock imagery** — No robots, no abstract "AI" visualizations

---

## Design Inspirations to Study

### Developer-Native Brands

| Brand | What to Learn |
|-------|---------------|
| **Linear** | Information density, keyboard-first feel, dark mode excellence |
| **Vercel** | Minimal but powerful, developer respect, speed messaging |
| **GitHub** | Developer trust, code-centricity, understated sophistication |
| **Supabase** | Database focus with modern design, green as differentiator |
| **PlanetScale** | MySQL focus translated to brand, branching visualization |
| **Neon** | PostgreSQL identity, serverless messaging, technical depth |
| **Raycast** | Developer productivity, keyboard shortcuts, speed |
| **Fig** | Terminal-native design, autocomplete visualization |

### Anti-Inspirations (What to Avoid)

| Pattern | Why to Avoid |
|---------|--------------|
| ChatGPT-style chat bubbles | Implies conversational, not professional tooling |
| Purple/blue AI gradients | Overused, signals "AI wrapper" |
| Robot/AI imagery | Cliché, doesn't convey database expertise |
| "Magic" language | Undermines technical credibility |
| Overly playful tone | Mismatched with enterprise database work |

---

## Front-End Design Resources

### Figma Community Resources

**Dashboard/Admin Templates:**
- Untitled UI — Clean, professional admin components
- Horizon UI — Dark mode dashboard system
- Tremor — Data visualization focused

**Developer Tool Aesthetics:**
- Terminal UI Kit — CLI-inspired components
- Code Editor Components — Syntax highlighting patterns
- Developer Portfolio templates — Technical presentation

**Data Visualization:**
- Chart & Graph Component Libraries
- Flow/Diagram Components
- Table/Grid Systems

### npm/React Ecosystem

**Code Display:**
```json
{
  "@monaco-editor/react": "Code editing with IntelliSense",
  "prism-react-renderer": "Syntax highlighting",
  "shiki": "VS Code-quality highlighting",
  "react-syntax-highlighter": "Quick highlighting"
}
```

**Data Visualization:**
```json
{
  "recharts": "Composable charts for React",
  "@visx/visx": "Low-level visualization primitives",
  "d3": "Full control data visualization",
  "reactflow": "Node-based diagrams (for schema viz)"
}
```

**UI Components:**
```json
{
  "@radix-ui/react-*": "Accessible primitives",
  "shadcn/ui": "Radix-based components",
  "@headlessui/react": "Tailwind-compatible accessibility",
  "cmdk": "Command palette (Raycast-style)"
}
```

**Animation:**
```json
{
  "framer-motion": "Production-ready animations",
  "react-spring": "Physics-based animations"
}
```

**Tables:**
```json
{
  "@tanstack/react-table": "Headless table logic",
  "ag-grid-react": "Enterprise data grid"
}
```

### shadcn/ui Components to Prioritize

For SQL2.AI's site specifically:
- Command (⌘K palette)
- Tabs (feature sections)
- Card (feature highlights)
- Table (comparison matrices)
- Badge (plan tiers)
- Sheet (mobile navigation)
- Tooltip (feature explanations)
- Accordion (FAQ sections)

---

## Custom Components Needed

### 1. Schema Visualization
Interactive ERD-style diagram showing:
- Tables with columns
- Relationship lines (FK connections)
- Diff highlighting (added/removed/changed)
- Zoom and pan navigation

### 2. Execution Plan Viewer
Visual representation of query plans:
- Tree structure of operations
- Cost percentages
- Row estimates vs actuals
- Bottleneck highlighting

### 3. Query Diff Component
Side-by-side or unified diff showing:
- Original query
- Optimized query
- Highlighted changes
- Performance delta

### 4. Lifecycle Progress Indicator
Visual showing position in the lifecycle:
- Current stage highlighted
- Completed stages checked
- Upcoming stages previewed

### 5. Code Terminal Block
Terminal-styled code display:
- Command prompt appearance
- Copy button
- Language indicator
- Line numbers

---

## Color Strategy

### Primary Palette

| Role | Color | Hex | Usage |
|------|-------|-----|-------|
| Primary | Blue | #2563EB | CTAs, links, active states |
| Background | Slate | #0F172A | Dark mode base |
| Surface | Slate | #1E293B | Cards, elevated surfaces |
| Text | White/Slate | #F8FAFC / #94A3B8 | Primary/secondary text |
| Success | Emerald | #10B981 | Optimizations, improvements |
| Warning | Amber | #F59E0B | Cautions, considerations |
| Error | Red | #EF4444 | Breaking changes, errors |

### SQL-Specific Colors

| Purpose | Color | Usage |
|---------|-------|-------|
| PostgreSQL | #336791 | PostgreSQL-specific features |
| SQL Server | #CC2927 | SQL Server-specific features |
| Added | #22C55E | Schema additions |
| Removed | #EF4444 | Schema removals |
| Modified | #EAB308 | Schema changes |

---

## Typography

### Headings
- **Font:** Inter (variable weight)
- **Weights:** 600 (semibold) for h1-h3, 500 (medium) for h4-h6
- **Tracking:** Slightly tight (-0.02em)

### Body
- **Font:** Inter
- **Weight:** 400 (regular)
- **Line height:** 1.6 for readability

### Code
- **Font:** JetBrains Mono or Fira Code
- **Weight:** 400
- **Features:** Ligatures enabled for operators

---

## Image Strategy (prompt2image)

### Hero Images Needed

1. **Schema Diff Visualization**
   - Side-by-side database schemas
   - Visual diff highlighting
   - Professional, technical aesthetic

2. **Execution Plan Tree**
   - Query plan visualization
   - Bottleneck callouts
   - Performance metrics overlay

3. **CLI in Action**
   - Terminal window with sql2ai commands
   - Output showing analysis results
   - Dark terminal aesthetic

4. **MCP Integration**
   - Claude Code with SQL2.AI tools
   - Natural language to SQL flow
   - Context awareness visualization

5. **Lifecycle Diagram**
   - The 7-stage lifecycle
   - Connecting arrows
   - Icon for each stage

### Image Style Guidelines

**DO:**
- Use actual code/SQL in images
- Show real metrics and numbers
- Dark backgrounds with syntax highlighting
- Clean, technical diagrams
- Monospace fonts for code

**DON'T:**
- Abstract AI imagery
- Robots or humanoid AI
- Glowing/neon effects
- Stock photography of people
- Overly complex illustrations

---

## Page-by-Page Design Notes

### Homepage

**Hero:**
- Headline emphasizing database-first
- Subheadline with lifecycle breadth
- Primary CTA: "Start Free Trial"
- Secondary CTA: "Watch Demo"
- Background: Subtle schema pattern or code texture

**Lifecycle Section:**
- Visual representation of 7 stages
- Brief description of each
- Links to detailed feature pages

**Comparison Section:**
- Before/After query optimization
- Interactive if possible
- Real performance metrics

**Trust Section:**
- Database logos (PostgreSQL, SQL Server)
- Metrics (queries optimized, schemas analyzed)
- Enterprise-ready messaging

### Features Page

Each feature gets:
- Clear headline
- Problem statement
- Solution explanation
- Visual demonstration
- Code example

### Pricing Page

- Three tiers clearly differentiated
- Feature comparison table
- FAQ section
- Enterprise CTA

### Documentation

- Left sidebar navigation
- Breadcrumbs
- Table of contents (right)
- Code blocks with copy
- Version selector

---

## Responsive Strategy

### Breakpoints

| Name | Width | Layout |
|------|-------|--------|
| Mobile | < 640px | Single column, hamburger nav |
| Tablet | 640-1024px | Two columns, condensed nav |
| Desktop | 1024-1280px | Full layout |
| Wide | > 1280px | Centered with max-width |

### Mobile Considerations

- Code blocks scroll horizontally
- Tables become cards on mobile
- Schema diagrams simplify
- Navigation becomes sheet/drawer

---

## Performance Requirements

- Lighthouse score > 90 on all pages
- First Contentful Paint < 1.5s
- Largest Contentful Paint < 2.5s
- Total Blocking Time < 200ms
- Cumulative Layout Shift < 0.1

### Strategies
- Static generation for all marketing pages
- Lazy load below-fold images
- Optimize code highlighting (server-side)
- Minimal JavaScript for static pages

---

## Next Steps

1. [ ] Audit Linear, Vercel, Supabase, PlanetScale, Neon sites
2. [ ] Select Figma templates/components to adapt
3. [ ] Build component library with shadcn/ui base
4. [ ] Create prompt2image specifications for each visual
5. [ ] Build homepage first draft
6. [ ] Iterate based on lifecycle messaging
7. [ ] Expand to other pages

---

*Draft 1 — To be revised and perfected*
