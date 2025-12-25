# SQL2.AI — Claude Code Instructions

**Project:** SQL2.AI — AI-Driven Database Development Platform
**Repository:** sql2ai (Nx Monorepo)
**Author:** Chris Therriault <chris@servicevision.net>

---

## Project Identity

SQL2.AI is a comprehensive SaaS platform that brings AI sophistication to database-first development. The core thesis:

> **Data models drive objects, not the reverse.**

We prioritize:
- Stored procedures, views, and functions as first-class citizens
- Set-based optimization over row-by-row processing
- Transaction contextual visibility for LLM reasoning
- Saga patterns for distributed transactions
- Telemetry-driven optimization

---

## Core Principles

### 1. Database-First Development
- Schema is the source of truth
- Application models are generated FROM the database
- Never generate ORM-first migrations

### 2. Set-Based Optimization
- Always prefer set operations over cursors
- Flag row-by-row processing for refactoring
- Explain set-based alternatives when suggesting changes

### 3. Full Transaction Context
- Understand isolation levels and their implications
- Reason about deadlock potential
- Consider lock ordering in multi-table operations

### 4. Cross-Platform Support
- Primary: PostgreSQL and SQL Server
- Translate syntax appropriately
- Note platform-specific optimizations

---

## Monorepo Structure

```
sql2ai/
├── apps/           # Deployable applications
│   ├── api/        # FastAPI + .NET Core API
│   ├── web/        # SaaS dashboard (Next.js)
│   ├── site/       # Marketing site (Next.js/Vercel)
│   ├── vscode-extension/
│   └── ssms-addin/
├── libs/           # Shared libraries
│   ├── sql-parser/
│   ├── schema-analyzer/
│   ├── query-optimizer/
│   ├── migration-engine/
│   ├── telemetry-collector/
│   ├── llm-orchestrator/
│   ├── ui-components/
│   └── shared-types/
├── packages/       # Publishable packages
│   ├── sql2ai-cli/
│   ├── sql2ai-mcp/
│   └── sql2ai-sdk/
├── tools/          # Build tooling
├── mvp/original/   # Source projects (reference only)
└── docs/           # Documentation
```

---

## Technology Stack

| Layer | Technology | Notes |
|-------|------------|-------|
| Frontend | Next.js 14 (App Router) | Server components preferred |
| API | FastAPI (Python) | Async, existing SQL tools |
| API | ASP.NET Core | SQL Server native integration |
| Database | PostgreSQL | Primary platform |
| Database | SQL Server | Customer support |
| LLM | Claude (Anthropic) | MCP integration |
| Monorepo | Nx | Multi-language support |
| Deploy | Vercel (site), Azure (API) | |

---

## Coding Standards

### Python (FastAPI, SQL Analysis)
```python
# Use async/await for all database operations
async def analyze_schema(connection: AsyncConnection) -> SchemaAnalysis:
    # Type hints required
    # Pydantic models for all DTOs
    pass

# Use Repository pattern for data access
class SchemaRepository:
    async def get_tables(self, schema: str) -> list[TableDefinition]:
        pass
```

### TypeScript (Next.js, Libraries)
```typescript
// Strict TypeScript - no `any`
// Use Zod for runtime validation
// Server components by default

export async function SchemaView({ schemaId }: { schemaId: string }) {
  const schema = await getSchema(schemaId); // Server-side fetch
  return <SchemaDisplay schema={schema} />;
}
```

### C# (SSMS Add-in, .NET API)
```csharp
// Explicit types, async/await everywhere
// Dependency injection via built-in container
// FluentValidation for input validation

public async Task<SchemaAnalysis> AnalyzeSchemaAsync(
    string connectionString,
    CancellationToken cancellationToken = default)
{
    // Use Repository pattern
    // Return rich domain objects
}
```

### SQL (Generated and Analyzed)
```sql
-- Always include transaction context comments
-- Explain isolation level requirements
-- Note lock ordering for deadlock prevention

-- Transaction: Order Processing
-- Isolation: REPEATABLE READ (inventory consistency)
-- Lock Order: Inventory -> Orders (never reverse)
BEGIN TRANSACTION;
  -- Set-based inventory decrement
  UPDATE Inventory
  SET Quantity = Quantity - oi.Quantity
  FROM Inventory i
  INNER JOIN @OrderItems oi ON i.ProductId = oi.ProductId;

  -- Batch insert order items
  INSERT INTO OrderItems (OrderId, ProductId, Quantity, Price)
  SELECT @OrderId, ProductId, Quantity, Price
  FROM @OrderItems;
COMMIT;
```

---

## Extended Thinking Triggers

For complex database operations, use extended thinking:

| Trigger | Use Case |
|---------|----------|
| `think` | Standard SQL analysis |
| `think hard` | Cross-platform migration planning |
| `think harder` | Saga pattern design, deadlock analysis |
| `ultrathink` | Full system architecture decisions |

---

## Module Development Guidelines

### When Working on sql-parser
- Support both T-SQL and PostgreSQL dialects
- Generate AST that can be analyzed and transformed
- Preserve comments and formatting information

### When Working on schema-analyzer
- Compare schemas at structural and semantic levels
- Detect breaking changes in migrations
- Identify optimization opportunities

### When Working on query-optimizer
- Understand execution plan interpretation
- Suggest index improvements based on patterns
- Flag cursor operations for set-based refactoring

### When Working on migration-engine
- Generate forward and rollback scripts
- Calculate dependency order automatically
- Support both online and offline migrations

### When Working on telemetry-collector
- Collect query execution metrics
- Aggregate performance data
- Feed insights back to optimization engine

---

## MCP Server Development

The sql2ai-mcp server exposes tools to Claude:

```typescript
// Tool naming convention: verb_noun
// Examples: analyze_schema, generate_procedure, compare_schemas

export const analyzeSchemaHandler = async (params: {
  connectionString: string;
  schemaName?: string;
}): Promise<SchemaAnalysis> => {
  // Implementation
};
```

### MCP Tool Requirements
1. Clear, descriptive tool names
2. Comprehensive parameter validation
3. Rich error messages with context
4. Progress indication for long operations
5. Cancellation support

---

## Testing Requirements

| Component | Test Type | Coverage Target |
|-----------|-----------|-----------------|
| sql-parser | Unit | 95% |
| schema-analyzer | Unit + Integration | 90% |
| query-optimizer | Unit + Property | 90% |
| migration-engine | Integration | 85% |
| API endpoints | Integration | 80% |
| UI components | Component | 70% |

### Test Database Setup
- Use Testcontainers for PostgreSQL
- Use SQL Server LocalDB or container for SQL Server
- Never use production connection strings in tests

---

## MVP/Original Projects Reference

The `mvp/original/` folder contains 20 source projects. These are:
- **Reference implementations** — Learn from their patterns
- **Code mining source** — Extract reusable components
- **NOT directly imported** — Rebuild with unified architecture

### Key Projects to Study
| Project | Extract For |
|---------|-------------|
| sqlanalyzer | Schema comparison logic |
| SQLMCP | MCP server patterns |
| sql-monitor | Telemetry collection |
| bcpplus | Bulk operations |
| babelfishAI | Cross-platform translation |

---

## What Claude Must NOT Do

1. **Never generate ORM-first migrations** — Database drives models
2. **Never suggest row-by-row processing** — Set-based only
3. **Never ignore transaction context** — Always consider isolation
4. **Never hardcode connection strings** — Use configuration
5. **Never skip SQL injection protection** — Parameterized queries only
6. **Never generate untested stored procedures** — TDD for SQL too

---

## Workflow for New Features

1. **Analyze existing MVP projects** for similar functionality
2. **Design with database-first principle**
3. **Write tests before implementation** (TDD)
4. **Generate SQL with full context comments**
5. **Consider cross-platform compatibility**
6. **Update documentation**

---

## Quick Reference

### Nx Commands
```bash
# Run specific app
nx serve api
nx serve web
nx serve site

# Build
nx build api --prod
nx build web --prod

# Test
nx test sql-parser
nx test schema-analyzer

# Generate
nx g @nx/node:lib new-lib --directory=libs
```

### Project Tags
- `scope:api` — Backend services
- `scope:web` — Web applications
- `scope:lib` — Shared libraries
- `scope:pkg` — Publishable packages
- `type:sql` — SQL-focused
- `type:ui` — UI components

---

*End of CLAUDE.md*
*Update as the project evolves.*
