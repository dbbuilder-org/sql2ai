# SQL2.AI Marketing Site Plan

**Location:** `apps/site`
**Deployment:** Vercel
**Framework:** Next.js 14 (App Router)
**Domain:** sql2.ai

**Related Documents:**
- `DESIGN_SPECIFICATION.md` — Visual design system and component specs
- `DESIGN_STRATEGY_REVISED.md` — Positioning and messaging strategy
- `VISION.md` — Product vision and architecture

---

## Purpose

The marketing site serves as the public face of SQL2.AI, designed to:

1. **Communicate value** — Clearly explain what SQL2.AI does and why it matters
2. **Convert visitors** — Drive signups for free trials and paid plans
3. **Educate users** — Provide documentation, tutorials, and resources
4. **Build trust** — Showcase testimonials, case studies, and enterprise credibility

---

## Site Structure

```
apps/site/
├── src/
│   ├── app/
│   │   ├── page.tsx                 # Homepage
│   │   ├── layout.tsx               # Root layout
│   │   ├── features/
│   │   │   └── page.tsx             # Features overview
│   │   ├── pricing/
│   │   │   └── page.tsx             # Pricing plans
│   │   ├── docs/
│   │   │   ├── page.tsx             # Docs home
│   │   │   ├── getting-started/
│   │   │   ├── schema-analyzer/
│   │   │   ├── query-optimizer/
│   │   │   ├── migrations/
│   │   │   └── mcp-integration/
│   │   ├── blog/
│   │   │   ├── page.tsx             # Blog index
│   │   │   └── [slug]/page.tsx      # Blog posts
│   │   ├── about/
│   │   │   └── page.tsx             # About/team
│   │   ├── contact/
│   │   │   └── page.tsx             # Contact form
│   │   ├── login/
│   │   │   └── page.tsx             # Redirect to app
│   │   ├── signup/
│   │   │   └── page.tsx             # Signup flow
│   │   ├── changelog/
│   │   │   └── page.tsx             # Product changelog
│   │   └── legal/
│   │       ├── privacy/
│   │       └── terms/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── MobileNav.tsx
│   │   ├── marketing/
│   │   │   ├── Hero.tsx
│   │   │   ├── FeatureGrid.tsx
│   │   │   ├── PricingTable.tsx
│   │   │   ├── Testimonials.tsx
│   │   │   ├── CTASection.tsx
│   │   │   └── DatabaseComparison.tsx
│   │   ├── docs/
│   │   │   ├── DocsSidebar.tsx
│   │   │   ├── CodeBlock.tsx
│   │   │   └── TableOfContents.tsx
│   │   └── ui/
│   │       └── (shared from @sql2ai/ui-components)
│   └── lib/
│       ├── blog.ts                  # Blog content helpers
│       └── docs.ts                  # Docs content helpers
├── content/
│   ├── blog/                        # MDX blog posts
│   └── docs/                        # MDX documentation
├── public/
│   ├── images/
│   ├── og/                          # Open Graph images
│   └── favicon.ico
├── next.config.js
├── tailwind.config.js
└── vercel.json
```

---

## Key Pages

### 1. Homepage (`/`)

**Hero Section:**
- Headline: "Database Development, Powered by AI"
- Subheadline: Clear value proposition about database-first development
- Primary CTA: "Start Free Trial"
- Secondary CTA: "Watch Demo"

**Feature Highlights:**
- Schema Analyzer — Visual comparison with AI insights
- Query Optimizer — Before/after with performance metrics
- Migration Engine — Dependency graph visualization
- MCP Integration — Claude Code integration demo

**Social Proof:**
- Logos of compatible databases (PostgreSQL, SQL Server)
- Key metrics (queries optimized, schemas analyzed)
- Testimonials from DBAs/developers

**CTA Section:**
- Final conversion push
- No credit card required messaging

### 2. Features (`/features`)

Dedicated pages for each major feature:

- `/features/schema-analyzer` — Deep dive into schema analysis
- `/features/query-optimizer` — Query optimization capabilities
- `/features/migration-engine` — Migration generation workflow
- `/features/telemetry` — Performance monitoring features
- `/features/mcp-integration` — Claude/AI integration

### 3. Pricing (`/pricing`)

**Tiers:**

| Plan | Price | Target |
|------|-------|--------|
| Free | $0/mo | Individual developers |
| Professional | $29/mo | Professional developers |
| Team | $99/mo | Development teams (up to 10) |
| Enterprise | Custom | Large organizations |

**Feature comparison matrix:**
- Connections per plan
- Query optimizations/month
- Schema comparisons
- Telemetry retention
- Support level

### 4. Documentation (`/docs`)

**Sections:**
1. **Getting Started**
   - Quick Start Guide
   - Installation (CLI, MCP, SDK)
   - First Schema Analysis

2. **Core Concepts**
   - Database-First Development
   - Set-Based Optimization
   - Transaction Context

3. **Features**
   - Schema Analyzer Guide
   - Query Optimizer Guide
   - Migration Engine Guide
   - Telemetry Dashboard

4. **Integrations**
   - Claude Code (MCP)
   - VS Code Extension
   - SSMS Add-in
   - CI/CD Pipelines

5. **API Reference**
   - REST API
   - SDK Reference
   - Webhooks

### 5. Blog (`/blog`)

**Content Strategy:**
- Database optimization tips
- AI in database development
- Case studies
- Product updates
- Industry analysis

---

## Design Principles

### Visual Identity

**Colors:**
- Primary: Blue (#2563EB) — Trust, technology
- Secondary: Slate (#1E293B) — Professional
- Accent: Emerald (#10B981) — Success, optimization

**Typography:**
- Headings: Inter (bold, clean)
- Body: Inter (readable, professional)
- Code: JetBrains Mono (technical credibility)

### Anti-Generic AI UI Patterns

To avoid the "ChatGPT clone" look:

1. **No chat bubbles** on marketing pages
2. **No generic robot/AI imagery**
3. **Real data visualizations** (schema diagrams, execution plans)
4. **Technical credibility** — Show actual SQL, not abstractions
5. **Developer-focused design** — Terminal aesthetics where appropriate
6. **Distinctive color palette** — Not the purple/blue gradient everyone uses

### Distinctiveness Checklist

- [ ] Custom illustrations (not stock AI images)
- [ ] Real code examples with syntax highlighting
- [ ] Interactive demos (schema diff, query optimization)
- [ ] Database-specific iconography
- [ ] Dark mode that looks intentional, not default
- [ ] Performance metrics front and center

---

## Technical Implementation

### Framework Choices

```typescript
// Next.js 14 App Router with:
- Server Components (default)
- Static Generation for marketing pages
- MDX for documentation and blog
- Tailwind CSS for styling
- Framer Motion for animations
```

### Key Dependencies

```json
{
  "dependencies": {
    "next": "^14.2.0",
    "react": "^18.3.0",
    "@sql2ai/ui-components": "workspace:*",
    "@sql2ai/shared-types": "workspace:*",
    "next-mdx-remote": "^4.4.1",
    "framer-motion": "^11.0.0",
    "prism-react-renderer": "^2.3.0"
  }
}
```

### Vercel Configuration

```json
{
  "framework": "nextjs",
  "buildCommand": "npx nx build site --prod",
  "outputDirectory": "../../dist/apps/site/.next"
}
```

### Environment Variables

```env
# Vercel project settings
NEXT_PUBLIC_APP_URL=https://app.sql2.ai
NEXT_PUBLIC_API_URL=https://api.sql2.ai
NEXT_PUBLIC_ANALYTICS_ID=...

# Build-time
CONTENTFUL_SPACE_ID=...  # If using CMS
CONTENTFUL_ACCESS_TOKEN=...
```

---

## SEO Strategy

### Technical SEO

- Server-rendered pages for crawlability
- Automatic sitemap generation
- Structured data for documentation
- Open Graph images for all pages

### Target Keywords

**Primary:**
- AI database development
- SQL optimization tool
- Database schema analyzer
- SQL migration generator

**Long-tail:**
- PostgreSQL query optimizer
- SQL Server schema comparison
- Claude database integration
- Set-based SQL optimization

### Content Strategy

- Technical blog posts (SEO + thought leadership)
- Documentation (capture search intent)
- Comparison pages (vs. competitors)
- Use case pages (by role: DBA, Developer, Architect)

---

## Analytics & Conversion

### Tracking

- Vercel Analytics (core metrics)
- PostHog (product analytics, funnels)
- Google Search Console (SEO)

### Key Metrics

| Metric | Target |
|--------|--------|
| Homepage → Signup | 5% conversion |
| Pricing → Signup | 15% conversion |
| Blog → Signup | 2% conversion |
| Docs → App | 10% transition |

### Conversion Optimization

- A/B test headlines
- CTA button variants
- Pricing page layout
- Demo video engagement

---

## Content Roadmap

### Phase 1: Launch

- [ ] Homepage with core messaging
- [ ] Pricing page with all tiers
- [ ] Basic documentation (Getting Started)
- [ ] Contact/signup forms

### Phase 2: Depth

- [ ] Full documentation site
- [ ] 5 launch blog posts
- [ ] Feature detail pages
- [ ] Interactive demos

### Phase 3: Growth

- [ ] Case studies
- [ ] Comparison pages
- [ ] Video tutorials
- [ ] Community/Discord integration

---

## Development Workflow

### Local Development

```bash
# From monorepo root
nx serve site

# Opens at http://localhost:3001
```

### Preview Deployments

- Every PR gets a Vercel preview URL
- Automatic lighthouse scores
- Visual regression testing

### Production Deployment

```bash
# Merged to main = automatic deploy
# Or manual:
nx build site --prod
```

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Design | 1 sprint | Wireframes, brand assets |
| MVP | 2 sprints | Homepage, pricing, basic docs |
| Launch | 1 sprint | Polish, copy, SEO setup |
| Growth | Ongoing | Content, optimization |

---

---

## Design Resources Checklist

### Figma Community Downloads
- [ ] **Untitled UI** — Base component system
- [ ] **Horizon UI Dashboard** — Dark mode patterns
- [ ] **Raycast UI Kit** — Command palette reference
- [ ] **Linear Clone** — Developer tool aesthetics

### npm Packages to Install
```bash
# UI Foundation
npm install @radix-ui/react-* class-variance-authority clsx tailwind-merge

# Code Display
npm install shiki

# Visualization
npm install reactflow @visx/visx recharts

# Animation
npm install framer-motion

# Command Palette
npm install cmdk

# Tables
npm install @tanstack/react-table

# Icons
npm install lucide-react
```

### Typography Assets
- [ ] Inter (variable font) — Google Fonts
- [ ] JetBrains Mono — JetBrains website

### Image Generation (prompt2image)
After first draft complete:
- [ ] Hero schema visualization
- [ ] Query optimization before/after
- [ ] Execution plan tree
- [ ] Terminal CLI screenshot
- [ ] Cross-platform bridge diagram
- [ ] MCP integration mockup
- [ ] Lifecycle infographic

See `DESIGN_SPECIFICATION.md` for detailed prompts.

---

## Quick Start for Development

```bash
# From monorepo root
cd /Users/admin/Dev2/sql2ai

# Install dependencies
npm install

# Start the marketing site
nx serve site

# Site runs at http://localhost:3001
```

### Development Workflow

1. Build components in `libs/ui-components`
2. Import into `apps/site`
3. Use Tailwind tokens from design system
4. Test on mobile/tablet/desktop
5. Run Lighthouse before PR

---

*This plan will evolve as we build. Update as decisions are made.*

**Last Updated:** December 2024
