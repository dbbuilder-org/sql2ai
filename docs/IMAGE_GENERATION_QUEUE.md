# SQL2.AI Image Generation Queue

This document contains all image specifications from the Design Specification, formatted for easy generation using AI image tools.

---

## Image 1: Hero - Schema Visualization

**Page:** Homepage (Hero Section)
**Dimensions:** 1920x1080 (16:9)
**Filename:** `hero-schema-visualization.png`
**Priority:** HIGH (above-the-fold homepage image)

### Prompt
```
A sophisticated database schema visualization on a near-black background (#09090f), showing 6-8 interconnected tables as rounded rectangles with subtle borders, each containing visible column names in small monospace text, tables connected by thin lines representing foreign keys, one table highlighted with a blue glow (#3b82f6), subtle dot grid pattern in background at 5% opacity, professional enterprise software aesthetic, clean vector style, no labels outside diagram area, cinematic lighting
```

### Generation Notes
- Focus on technical accuracy - tables should look like real database tables
- Ensure column names are legible (even if placeholder text)
- Blue highlight should be subtle but noticeable
- Background must be very dark (#09090f) to match site design
- Avoid generic "AI art" aesthetics - this needs to look professional

---

## Image 2: Query Optimization Before/After

**Page:** Homepage (Features Section), Features Page
**Dimensions:** 1920x1080 (16:9)
**Filename:** `query-optimization-before-after.png`
**Priority:** HIGH (key value proposition visualization)

### Prompt
```
Split screen code editor interface on dark background, left panel titled "Original" showing SQL query with sections highlighted in subtle red tint indicating inefficiencies, right panel titled "Optimized" showing cleaner SQL with green highlighted improvements, syntax highlighting with blue keywords and orange strings, line numbers visible, floating badge between panels showing "94% faster" with arrow, professional developer tool aesthetic, photorealistic software screenshot style
```

### Generation Notes
- Must look like an actual code editor (VS Code, JetBrains style)
- SQL syntax highlighting should be realistic
- Performance badge should be clearly visible and professional
- Ensure text is sharp and readable
- Split should be exactly 50/50

---

## Image 3: Execution Plan Visualization

**Page:** Features Page (Optimize Section), Documentation
**Dimensions:** 1200x900 (4:3)
**Filename:** `execution-plan-tree.png`
**Priority:** MEDIUM

### Prompt
```
Database query execution plan as flowing tree diagram on dark charcoal background, nodes are rounded rectangles labeled with operations like "Index Seek" and "Hash Match", each node shows percentage cost in corner, nodes connected by lines with data flow arrows, one node glowing red indicating the bottleneck (47% cost), cool blue accents on non-bottleneck nodes, clean technical diagram style, enterprise software aesthetic
```

### Generation Notes
- Tree should flow top-to-bottom
- Use realistic SQL Server/PostgreSQL execution plan operation names
- Red bottleneck highlight should be obvious
- Percentages should add up to ~100% for realism
- Maintain high contrast for readability

---

## Image 4: Terminal CLI Interface

**Page:** Homepage (Integration Section), Documentation
**Dimensions:** 1600x900 (16:9)
**Filename:** `terminal-cli-interface.png`
**Priority:** HIGH (shows actual product interface)

### Prompt
```
macOS terminal window with title bar buttons visible, semi-transparent dark background showing blurred desktop, inside terminal is command "sql2ai analyze --connection postgres://localhost/mydb", below shows colorized output with green checkmarks, yellow warning symbols, and a formatted ASCII table of results, professional developer screenshot, realistic terminal emulator appearance
```

### Generation Notes
- Must look like iTerm2 or macOS Terminal
- Command should be exact: `sql2ai analyze --connection postgres://localhost/mydb`
- Output should include realistic success/warning indicators
- ASCII table formatting is important for technical credibility
- Terminal transparency should be subtle

---

## Image 5: Cross-Platform Bridge

**Page:** Homepage (Platforms Section), Features Page
**Dimensions:** 1920x800 (2.4:1)
**Filename:** `cross-platform-bridge.png`
**Priority:** MEDIUM

### Prompt
```
Technical diagram showing SQL Server logo (red) on left and PostgreSQL elephant logo (blue) on right, connected through a central hub with glowing data streams, binary/code particles flowing between them, transformation symbols along the path, dark background with subtle tech grid, professional enterprise software illustration style, vector art aesthetic
```

### Generation Notes
- Use official SQL Server (red/white) and PostgreSQL (blue elephant) branding
- Data flow should be bidirectional
- Central hub represents SQL2.AI (keep neutral/blue)
- Avoid overly "sci-fi" aesthetic - should feel professional
- Grid pattern should be very subtle

---

## Image 6: MCP Integration / IDE

**Page:** Features Page (Integration Section)
**Dimensions:** 1920x1080 (16:9)
**Filename:** `mcp-ide-integration.png`
**Priority:** MEDIUM

### Prompt
```
Modern IDE interface on dark theme showing code editor on left with SQL query visible, right panel shows AI assistant response with database context, visible schema tree sidebar showing table icons, subtle connection visualization between code and AI response, professional developer tool aesthetic, realistic software interface, no visible branding or logos
```

### Generation Notes
- Should resemble VS Code or JetBrains IDE
- SQL query in editor should be realistic
- AI response should show helpful database suggestions
- Schema tree on left/right sidebar with table icons
- Keep interface clean and uncluttered

---

## Image 7: Lifecycle Diagram

**Page:** Homepage (Lifecycle Section), Features Page
**Dimensions:** 1200x1200 (1:1)
**Filename:** `lifecycle-circular-diagram.png`
**Priority:** HIGH (core product concept)

### Prompt
```
Circular workflow infographic with 7 hexagonal nodes arranged in a circle, each node contains a minimal line icon (magnifying glass for Analyze, gauge for Optimize, wrench for Refactor, list for Index, document for Document, branch for Version, rocket for Deploy), nodes connected by curved arrows, "Analyze" node highlighted in blue, dark background with subtle radial gradient, clean vector infographic style
```

### Generation Notes
- Exactly 7 nodes in circular arrangement
- Icons should be simple line icons (not filled)
- Arrows should show clockwise flow
- Blue highlight on "Analyze" should match brand color (#3b82f6)
- Labels for each stage: Analyze, Optimize, Refactor, Index, Document, Version, Deploy
- Vector style, not photorealistic

---

## Summary Table

| # | Filename | Dimensions | Priority | Used On |
|---|----------|------------|----------|---------|
| 1 | `hero-schema-visualization.png` | 1920x1080 | HIGH | Homepage Hero |
| 2 | `query-optimization-before-after.png` | 1920x1080 | HIGH | Homepage Features, Features Page |
| 3 | `execution-plan-tree.png` | 1200x900 | MEDIUM | Features Page, Docs |
| 4 | `terminal-cli-interface.png` | 1600x900 | HIGH | Homepage Integration, Docs |
| 5 | `cross-platform-bridge.png` | 1920x800 | MEDIUM | Homepage Platforms, Features Page |
| 6 | `mcp-ide-integration.png` | 1920x1080 | MEDIUM | Features Page |
| 7 | `lifecycle-circular-diagram.png` | 1200x1200 | HIGH | Homepage Lifecycle, Features Page |

---

## File Organization

All generated images should be placed in:
```
/Users/admin/Dev2/sql2ai/public/images/marketing/
```

### Naming Convention
- All lowercase
- Hyphen-separated
- Descriptive but concise
- No version numbers in filename (use git for versioning)

### File Format
- Primary format: PNG (for transparency support and sharp edges)
- Compression: Optimize for web (use tools like ImageOptim or Squoosh)
- Backup: Keep original high-res versions in separate archive folder

---

## Generation Workflow

1. **Copy prompt** from this document
2. **Generate** using recommended AI tool (see TOOL_RECOMMENDATIONS.md)
3. **Review** against specifications:
   - Correct dimensions?
   - Dark theme consistent?
   - Technical accuracy?
   - No generic AI artifacts?
4. **Iterate** if needed (adjust prompt, regenerate)
5. **Optimize** for web (compress without quality loss)
6. **Save** to `/public/images/marketing/`
7. **Commit** to git with descriptive message

---

## Quality Checklist

Before marking an image as "done", verify:

- [ ] Dimensions are exact (use ImageMagick or similar to verify)
- [ ] Background color matches design system (#09090f or close)
- [ ] Text is sharp and readable (no blur)
- [ ] Colors match design tokens (blues #3b82f6, reds #ef4444, etc.)
- [ ] No obvious "AI art" artifacts (weird hands, distorted text, etc.)
- [ ] Looks professional and enterprise-grade
- [ ] File size is optimized (< 500KB for PNG, ideally < 200KB)
- [ ] Works well on both light and dark backgrounds (if applicable)

---

**Last Updated:** 2024-12-24
**Source:** `/Users/admin/Dev2/sql2ai/docs/DESIGN_SPECIFICATION.md` Section 6
