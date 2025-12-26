# SQL2.AI Implementation Plan

## Overview

This document outlines the detailed implementation plan for the SQL2.AI platform MVP, covering:
1. **MCP Server** - Model Context Protocol server for Claude integration
2. **Phase C** - Frontend Application
3. **Phase B** - Authentication Layer
4. **Phase D** - Schema/Metadata Engine
5. **Phase A** - AI Features Integration

---

## Part 1: MCP Server for SQL2.AI

### 1.1 What is MCP?

Model Context Protocol (MCP) is Anthropic's open protocol for connecting AI models to external data sources and tools. An MCP server allows Claude (via Claude Desktop, Claude Code, or API) to:
- Access external data sources
- Execute actions in external systems
- Maintain context across conversations

### 1.2 SQL2.AI MCP Server Vision

The SQL2.AI MCP server will enable developers to use Claude as an intelligent database assistant directly in their IDE or terminal.

**Use Cases:**
```
User: "Show me the schema for the customers table"
Claude: [Calls MCP tool] Here's the customers table schema...

User: "Write a query to find customers who haven't ordered in 90 days"
Claude: [Uses schema context, generates SQL, optionally executes]

User: "That query is slow, can you optimize it?"
Claude: [Gets execution plan via MCP, analyzes, suggests improvements]
```

### 1.3 MCP Server Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Claude Desktop / Claude Code              │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ MCP Protocol (JSON-RPC over stdio)
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQL2.AI MCP Server                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │ Connection  │  │   Schema    │  │      Query          │  │
│  │  Manager    │  │  Provider   │  │     Executor        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Security   │  │   Prompt    │  │     Audit           │  │
│  │   Layer     │  │  Templates  │  │     Logger          │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │SQL Server│   │PostgreSQL│   │  MySQL   │
        └──────────┘   └──────────┘   └──────────┘
```

### 1.4 MCP Tools to Implement

#### Connection Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `sql2ai_connect` | Add a database connection | name, type, host, port, database, username, password |
| `sql2ai_list_connections` | List saved connections | (none) |
| `sql2ai_test_connection` | Test a connection | connection_name |
| `sql2ai_disconnect` | Remove a connection | connection_name |

#### Schema Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `sql2ai_get_schema` | Get full database schema | connection_name, include_views, include_procedures |
| `sql2ai_get_table` | Get table details | connection_name, table_name |
| `sql2ai_get_columns` | Get column details | connection_name, table_name |
| `sql2ai_get_relationships` | Get foreign key relationships | connection_name, table_name? |
| `sql2ai_search_schema` | Search schema for keyword | connection_name, keyword |

#### Query Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `sql2ai_execute` | Execute a SQL query | connection_name, sql, max_rows?, timeout? |
| `sql2ai_explain` | Get execution plan | connection_name, sql |
| `sql2ai_validate` | Validate SQL syntax | connection_name, sql |
| `sql2ai_format` | Format SQL code | sql, dialect |

#### AI-Assisted Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `sql2ai_generate` | Generate SQL from natural language | connection_name, request |
| `sql2ai_optimize` | Suggest query optimizations | connection_name, sql |
| `sql2ai_review` | Review SQL for issues | sql, dialect |
| `sql2ai_document` | Generate documentation for object | connection_name, object_name |

#### Migration Tools
| Tool | Description | Parameters |
|------|-------------|------------|
| `sql2ai_diff` | Compare schemas | connection_a, connection_b |
| `sql2ai_generate_migration` | Generate migration script | connection_name, changes |

### 1.5 MCP Resources to Expose

Resources provide context that Claude can read:

| Resource URI | Description |
|--------------|-------------|
| `sql2ai://connections` | List of configured connections |
| `sql2ai://schema/{connection}` | Full schema for a connection |
| `sql2ai://table/{connection}/{table}` | Table definition |
| `sql2ai://history/{connection}` | Recent query history |
| `sql2ai://templates` | Available SQL templates |

### 1.6 MCP Server Files to Create

```
apps/mcp-server/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts              # Entry point, MCP server setup
│   ├── server.ts             # MCP server implementation
│   ├── tools/
│   │   ├── index.ts          # Tool registry
│   │   ├── connection.ts     # Connection management tools
│   │   ├── schema.ts         # Schema introspection tools
│   │   ├── query.ts          # Query execution tools
│   │   ├── ai.ts             # AI-assisted tools
│   │   └── migration.ts      # Migration tools
│   ├── resources/
│   │   ├── index.ts          # Resource registry
│   │   ├── connections.ts    # Connection list resource
│   │   ├── schema.ts         # Schema resource
│   │   └── history.ts        # Query history resource
│   ├── db/
│   │   ├── connection-manager.ts  # Database connection handling
│   │   ├── sqlserver.ts      # SQL Server adapter
│   │   ├── postgresql.ts     # PostgreSQL adapter
│   │   └── types.ts          # Database types
│   ├── security/
│   │   ├── sanitizer.ts      # SQL injection prevention
│   │   ├── permissions.ts    # Query permission checks
│   │   └── audit.ts          # Audit logging
│   └── config/
│       ├── settings.ts       # Configuration management
│       └── connections.json  # Saved connections (encrypted)
└── README.md
```

### 1.7 Security Considerations

1. **Credential Storage**: Encrypt database passwords at rest using system keychain
2. **Query Sanitization**: Prevent SQL injection in generated queries
3. **Permission Model**: Allow read-only mode, block DDL, configurable per connection
4. **Audit Logging**: Log all queries executed via MCP
5. **Rate Limiting**: Prevent runaway queries
6. **Timeout Enforcement**: Kill long-running queries

### 1.8 Installation & Configuration

```bash
# Install globally
npm install -g @sql2ai/mcp-server

# Or use npx
npx @sql2ai/mcp-server

# Configure in Claude Desktop
# ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "sql2ai": {
      "command": "npx",
      "args": ["@sql2ai/mcp-server"],
      "env": {
        "SQL2AI_CONFIG_PATH": "~/.sql2ai/config.json"
      }
    }
  }
}
```

---

## Part 1B: SQL2.AI CLI

### 1B.1 Overview

The SQL2.AI CLI (`@sql2ai/cli`) provides command-line access to all SQL2.AI capabilities, enabling scripting, automation, and CI/CD integration.

### 1B.2 CLI Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      SQL2.AI CLI                              │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  Command    │  │   Config    │  │      Output         │  │
│  │  Parser     │  │  Manager    │  │    Formatter        │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │    API      │  │   Local     │  │       MCP           │  │
│  │   Client    │  │    DB       │  │      Server         │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │SQL Server│   │PostgreSQL│   │SQL2.AI API│
        └──────────┘   └──────────┘   └──────────┘
```

### 1B.3 Command Categories

| Category | Commands | Description |
|----------|----------|-------------|
| `connection` | add, list, test, remove, default | Manage database connections |
| `schema` | show, columns, relations, export, search | Schema introspection |
| `query` | execute, generate, explain, optimize, format | Query operations |
| `migrate` | new, generate, up, down, status, validate | Migration management |
| `codegen` | typescript, csharp, api | Code generation |
| `comply` | check, scan-pii, report, evidence | Compliance operations |
| `version` | snapshot, history, diff, blame | Version control |
| `ai` | generate, explain, review, optimize | AI-powered operations |
| `monitor` | status, queries, blocking, indexes | Monitoring integration |
| `mcp` | serve | MCP server mode |

### 1B.4 CLI Files to Create

```
packages/sql2ai-cli/
├── package.json
├── tsconfig.json
├── bin/
│   └── sql2ai.ts                 # Entry point
├── src/
│   ├── index.ts                  # Main CLI setup
│   ├── commands/
│   │   ├── index.ts              # Command registry
│   │   ├── connection.ts         # Connection management
│   │   ├── schema.ts             # Schema operations
│   │   ├── query.ts              # Query operations
│   │   ├── migrate.ts            # Migration commands
│   │   ├── codegen.ts            # Code generation
│   │   ├── comply.ts             # Compliance checks
│   │   ├── version.ts            # Version control
│   │   ├── ai.ts                 # AI operations
│   │   ├── monitor.ts            # Monitoring
│   │   └── mcp.ts                # MCP server mode
│   ├── config/
│   │   ├── loader.ts             # Config file loading
│   │   ├── schema.ts             # Config validation
│   │   └── secrets.ts            # Secret management
│   ├── db/
│   │   ├── connection.ts         # Database connections
│   │   ├── sqlserver.ts          # SQL Server adapter
│   │   └── postgresql.ts         # PostgreSQL adapter
│   ├── api/
│   │   └── client.ts             # SQL2.AI API client
│   ├── output/
│   │   ├── formatter.ts          # Output formatting
│   │   ├── table.ts              # Table output
│   │   └── json.ts               # JSON/YAML output
│   └── utils/
│       ├── spinner.ts            # Progress indicators
│       └── prompts.ts            # Interactive prompts
├── templates/
│   └── config.yaml               # Default config template
└── README.md
```

### 1B.5 Core Dependencies

```json
{
  "dependencies": {
    "commander": "^12.0.0",
    "inquirer": "^9.0.0",
    "chalk": "^5.0.0",
    "ora": "^8.0.0",
    "cli-table3": "^0.6.0",
    "yaml": "^2.0.0",
    "mssql": "^10.0.0",
    "pg": "^8.0.0",
    "keytar": "^7.0.0"
  }
}
```

### 1B.6 Implementation Steps

1. **CLI Framework** (Day 1)
   - Commander.js setup
   - Global options
   - Help system

2. **Configuration** (Day 2)
   - Config file loading
   - Environment variables
   - Secret management with keytar

3. **Connection Commands** (Day 3)
   - Add/remove connections
   - Test connectivity
   - Credential storage

4. **Schema Commands** (Day 4)
   - Schema introspection
   - Export formats
   - Search functionality

5. **Query Commands** (Day 5)
   - Query execution
   - AI generation integration
   - Result formatting

6. **Migration Commands** (Day 6)
   - Migration creation
   - Up/down execution
   - Status and validation

7. **Code Generation** (Day 7)
   - TypeScript types
   - C# Dapper models
   - API generation

8. **Compliance & AI** (Day 8)
   - Compliance checks
   - AI operations
   - MCP server mode

---

## Part 2: Phase C - Frontend Application

### 2.1 Overview

Build the user-facing web application at `apps/app` using Next.js 14 with App Router.

### 2.2 Application Structure

```
apps/app/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   ├── signup/page.tsx
│   │   │   └── layout.tsx
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx           # Dashboard shell with sidebar
│   │   │   ├── page.tsx             # Dashboard home
│   │   │   ├── connections/
│   │   │   │   ├── page.tsx         # List connections
│   │   │   │   ├── new/page.tsx     # Add connection
│   │   │   │   └── [id]/page.tsx    # Connection details
│   │   │   ├── query/
│   │   │   │   ├── page.tsx         # Query editor
│   │   │   │   └── history/page.tsx # Query history
│   │   │   ├── schema/
│   │   │   │   ├── page.tsx         # Schema explorer
│   │   │   │   └── [table]/page.tsx # Table details
│   │   │   ├── ai/
│   │   │   │   ├── page.tsx         # AI assistant
│   │   │   │   └── prompts/page.tsx # Prompt templates
│   │   │   ├── compliance/
│   │   │   │   ├── page.tsx         # Compliance dashboard
│   │   │   │   └── scan/page.tsx    # Run compliance scan
│   │   │   └── settings/
│   │   │       ├── page.tsx         # General settings
│   │   │       ├── team/page.tsx    # Team management
│   │   │       └── billing/page.tsx # Subscription/billing
│   │   └── api/                     # API routes (if needed)
│   ├── components/
│   │   ├── ui/                      # Base UI components
│   │   │   ├── button.tsx
│   │   │   ├── input.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── table.tsx
│   │   │   ├── tabs.tsx
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── sidebar.tsx
│   │   │   ├── header.tsx
│   │   │   ├── nav-item.tsx
│   │   │   └── user-menu.tsx
│   │   ├── connections/
│   │   │   ├── connection-card.tsx
│   │   │   ├── connection-form.tsx
│   │   │   ├── connection-test.tsx
│   │   │   └── dialect-icon.tsx
│   │   ├── query/
│   │   │   ├── query-editor.tsx     # Monaco editor wrapper
│   │   │   ├── query-results.tsx    # Results table
│   │   │   ├── query-history.tsx
│   │   │   ├── execution-status.tsx
│   │   │   └── ai-assist-panel.tsx
│   │   ├── schema/
│   │   │   ├── schema-tree.tsx
│   │   │   ├── table-details.tsx
│   │   │   ├── column-list.tsx
│   │   │   └── relationship-diagram.tsx
│   │   └── ai/
│   │       ├── chat-interface.tsx
│   │       ├── sql-suggestion.tsx
│   │       └── optimization-card.tsx
│   ├── lib/
│   │   ├── api-client.ts            # API client (fetch wrapper)
│   │   ├── auth.ts                  # Clerk utilities
│   │   ├── hooks/
│   │   │   ├── use-connections.ts
│   │   │   ├── use-query.ts
│   │   │   ├── use-schema.ts
│   │   │   └── use-ai.ts
│   │   └── utils.ts
│   ├── stores/
│   │   ├── connection-store.ts      # Zustand store
│   │   ├── query-store.ts
│   │   └── ui-store.ts
│   └── styles/
│       └── globals.css
├── public/
├── package.json
├── tailwind.config.ts
├── next.config.js
└── tsconfig.json
```

### 2.3 Key Pages & Features

#### Dashboard Home (`/`)
- Quick stats (connections, queries today, AI tokens used)
- Recent queries
- Connection health status
- Quick actions

#### Connections (`/connections`)
- List all database connections
- Add new connection with test
- Connection health monitoring
- Quick connect/disconnect

#### Query Editor (`/query`)
- Monaco editor with SQL syntax highlighting
- AI assist panel (natural language → SQL)
- Query execution with results
- Export results (CSV, JSON, Excel)
- Query history sidebar
- Saved queries

#### Schema Explorer (`/schema`)
- Tree view of database objects
- Table/view details with columns
- Relationship visualization
- Search across schema
- DDL generation

#### AI Assistant (`/ai`)
- Chat interface for database questions
- SQL generation from natural language
- Query optimization suggestions
- Code review for SQL
- Compliance checking

#### Settings (`/settings`)
- Profile settings
- Team management (invite, roles)
- Billing (Stripe integration)
- API keys
- Preferences

### 2.4 UI Components Library

Use shadcn/ui for consistent, accessible components:
- Button, Input, Select, Checkbox
- Dialog, Sheet, Popover
- Table, DataTable with sorting/filtering
- Tabs, Accordion
- Toast notifications
- Command palette (⌘K)

### 2.5 State Management

Use Zustand for global state:
```typescript
// stores/connection-store.ts
interface ConnectionStore {
  connections: Connection[];
  activeConnection: Connection | null;
  setActiveConnection: (id: string) => void;
  fetchConnections: () => Promise<void>;
}
```

### 2.6 API Client

```typescript
// lib/api-client.ts
class APIClient {
  private baseUrl: string;
  private token: string;

  async get<T>(path: string): Promise<T>;
  async post<T>(path: string, data: unknown): Promise<T>;
  async put<T>(path: string, data: unknown): Promise<T>;
  async delete(path: string): Promise<void>;

  // Typed methods
  connections = {
    list: () => this.get<Connection[]>('/connections'),
    create: (data: CreateConnection) => this.post<Connection>('/connections', data),
    test: (data: TestConnection) => this.post<TestResult>('/connections/test', data),
    // ...
  };

  queries = {
    execute: (data: ExecuteQuery) => this.post<QueryResult>('/queries/execute', data),
    generate: (data: GenerateQuery) => this.post<GeneratedSQL>('/queries/generate', data),
    // ...
  };
}
```

### 2.7 Implementation Steps

1. **Setup** (Day 1)
   - Initialize Next.js app with TypeScript
   - Configure Tailwind CSS
   - Install shadcn/ui
   - Setup project structure

2. **Auth Shell** (Day 2)
   - Install Clerk
   - Create auth pages (login, signup)
   - Protected route wrapper
   - User context provider

3. **Dashboard Layout** (Day 3)
   - Sidebar navigation
   - Header with user menu
   - Responsive layout
   - Theme support (light/dark)

4. **Connections Module** (Day 4-5)
   - Connection list page
   - Add connection form
   - Connection test flow
   - Edit/delete connections

5. **Query Editor** (Day 6-8)
   - Monaco editor integration
   - Query execution
   - Results table with pagination
   - AI assist panel
   - Query history

6. **Schema Explorer** (Day 9-10)
   - Schema tree component
   - Table details view
   - Column information
   - Basic relationship view

7. **Settings** (Day 11)
   - Profile settings
   - Team management UI
   - Billing integration

8. **Polish** (Day 12)
   - Error handling
   - Loading states
   - Empty states
   - Keyboard shortcuts

---

## Part 3: Phase B - Authentication Layer

### 3.1 Overview

Implement complete authentication using Clerk with multi-tenant support.

### 3.2 Components

#### API Middleware (`apps/api/src/middleware/auth.py`)

```python
class AuthMiddleware:
    """Clerk authentication middleware."""

    async def __call__(self, request: Request, call_next):
        # 1. Extract token from Authorization header
        # 2. Verify with Clerk
        # 3. Get user and organization
        # 4. Set tenant context for RLS
        # 5. Attach user to request state
```

#### Dependencies (`apps/api/src/dependencies/auth.py`)

```python
async def get_current_user(request: Request) -> User:
    """Dependency to get authenticated user."""

async def get_current_tenant(request: Request) -> Tenant:
    """Dependency to get current tenant context."""

async def require_permission(permission: str):
    """Dependency factory for permission checks."""

def require_role(role: UserRole):
    """Decorator for role-based access."""
```

#### Permission System

```python
class Permissions:
    # Connection permissions
    CONNECTIONS_READ = "connections:read"
    CONNECTIONS_WRITE = "connections:write"
    CONNECTIONS_DELETE = "connections:delete"

    # Query permissions
    QUERIES_EXECUTE = "queries:execute"
    QUERIES_EXECUTE_DDL = "queries:execute_ddl"  # CREATE, ALTER, DROP
    QUERIES_EXECUTE_DML = "queries:execute_dml"  # INSERT, UPDATE, DELETE

    # AI permissions
    AI_GENERATE = "ai:generate"
    AI_OPTIMIZE = "ai:optimize"

    # Admin permissions
    ADMIN_USERS = "admin:users"
    ADMIN_BILLING = "admin:billing"
    ADMIN_SETTINGS = "admin:settings"

ROLE_PERMISSIONS = {
    UserRole.OWNER: ["*"],  # All permissions
    UserRole.ADMIN: [
        Permissions.CONNECTIONS_READ,
        Permissions.CONNECTIONS_WRITE,
        Permissions.QUERIES_EXECUTE,
        Permissions.AI_GENERATE,
        Permissions.ADMIN_USERS,
        # ... etc
    ],
    UserRole.DBA: [...],
    UserRole.DEVELOPER: [...],
    UserRole.VIEWER: [Permissions.CONNECTIONS_READ, Permissions.QUERIES_EXECUTE],
}
```

### 3.3 Webhook Handlers

```python
# apps/api/src/routers/webhooks/clerk.py

@router.post("/webhooks/clerk")
async def handle_clerk_webhook(request: Request):
    """Handle Clerk webhook events."""

    event = verify_webhook(request)

    match event["type"]:
        case "user.created":
            await handle_user_created(event["data"])
        case "user.updated":
            await handle_user_updated(event["data"])
        case "user.deleted":
            await handle_user_deleted(event["data"])
        case "organization.created":
            await handle_org_created(event["data"])
        case "organizationMembership.created":
            await handle_membership_created(event["data"])
        # ... etc
```

### 3.4 Implementation Steps

1. **Clerk SDK Integration**
   - Install Clerk Python SDK
   - Configure API keys
   - Token verification utility

2. **Auth Middleware**
   - Token extraction
   - Clerk verification
   - User/tenant context setting
   - RLS configuration

3. **Route Protection**
   - Apply middleware to all /api routes
   - Public routes exception list
   - Permission decorators

4. **Webhook Handlers**
   - User lifecycle events
   - Organization events
   - Membership events
   - Sync to local database

5. **Frontend Auth**
   - Clerk React components
   - Protected route wrapper
   - Token passing to API

---

## Part 4: Phase D - Schema/Metadata Engine

### 4.1 Overview

Build a robust schema introspection and caching system that provides context for AI features.

### 4.2 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Schema Engine                            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │    Extractor    │  │     Cache       │  │   Differ    │  │
│  │  (per dialect)  │  │  (Redis+DB)     │  │             │  │
│  └────────┬────────┘  └────────┬────────┘  └──────┬──────┘  │
│           │                    │                   │         │
│           ▼                    ▼                   ▼         │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    Schema Model                          ││
│  │  Database → Schemas → Tables → Columns                   ││
│  │                    → Views  → Indexes                    ││
│  │                    → Procedures → Parameters             ││
│  │                    → Functions                           ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 4.3 Schema Models

```python
# libs/shared/sql2ai_shared/schema/models.py

@dataclass
class Column:
    name: str
    data_type: str
    nullable: bool
    default_value: Optional[str]
    is_primary_key: bool
    is_foreign_key: bool
    references: Optional[ForeignKeyRef]
    description: Optional[str]

@dataclass
class Table:
    schema: str
    name: str
    columns: List[Column]
    primary_key: List[str]
    indexes: List[Index]
    foreign_keys: List[ForeignKey]
    row_count_estimate: Optional[int]
    description: Optional[str]

@dataclass
class DatabaseSchema:
    connection_id: str
    dialect: DatabaseDialect
    extracted_at: datetime
    schemas: List[SchemaInfo]
    tables: List[Table]
    views: List[View]
    procedures: List[Procedure]
    functions: List[Function]

    def to_context_string(self, max_tokens: int = 4000) -> str:
        """Format schema for AI prompt context."""

    def get_table(self, name: str) -> Optional[Table]:
        """Get table by name (case-insensitive)."""

    def search(self, keyword: str) -> List[SchemaObject]:
        """Search schema for keyword."""
```

### 4.4 Schema Extractors

```python
# libs/shared/sql2ai_shared/schema/extractors/

class BaseSchemaExtractor(ABC):
    """Base class for schema extraction."""

    @abstractmethod
    async def extract_tables(self) -> List[Table]: ...

    @abstractmethod
    async def extract_views(self) -> List[View]: ...

    @abstractmethod
    async def extract_procedures(self) -> List[Procedure]: ...

    @abstractmethod
    async def extract_relationships(self) -> List[ForeignKey]: ...

class SQLServerSchemaExtractor(BaseSchemaExtractor):
    """SQL Server schema extraction using system views."""

    TABLES_QUERY = """
    SELECT
        s.name AS schema_name,
        t.name AS table_name,
        p.rows AS row_count
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    LEFT JOIN sys.partitions p ON t.object_id = p.object_id AND p.index_id IN (0,1)
    WHERE t.is_ms_shipped = 0
    """

    COLUMNS_QUERY = """
    SELECT
        c.name AS column_name,
        TYPE_NAME(c.user_type_id) AS data_type,
        c.is_nullable,
        dc.definition AS default_value,
        CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key
    FROM sys.columns c
    JOIN sys.tables t ON c.object_id = t.object_id
    LEFT JOIN sys.default_constraints dc ON c.default_object_id = dc.object_id
    LEFT JOIN (
        SELECT ic.object_id, ic.column_id
        FROM sys.index_columns ic
        JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
        WHERE i.is_primary_key = 1
    ) pk ON c.object_id = pk.object_id AND c.column_id = pk.column_id
    WHERE t.object_id = @table_id
    """

class PostgreSQLSchemaExtractor(BaseSchemaExtractor):
    """PostgreSQL schema extraction using information_schema."""

    TABLES_QUERY = """
    SELECT
        table_schema,
        table_name,
        (SELECT reltuples FROM pg_class WHERE oid = (quote_ident(table_schema) || '.' || quote_ident(table_name))::regclass) AS row_count
    FROM information_schema.tables
    WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
    AND table_type = 'BASE TABLE'
    """
```

### 4.5 Schema Cache

```python
# libs/shared/sql2ai_shared/schema/cache.py

class SchemaCache:
    """Multi-layer schema cache."""

    def __init__(self, redis: RedisCache, db: AsyncSession):
        self.redis = redis
        self.db = db
        self.local_cache: Dict[str, DatabaseSchema] = {}  # L1

    async def get(self, connection_id: str) -> Optional[DatabaseSchema]:
        """Get schema with fallback through cache layers."""
        # L1: Local memory
        if connection_id in self.local_cache:
            return self.local_cache[connection_id]

        # L2: Redis
        cached = await self.redis.get(f"schema:{connection_id}")
        if cached:
            schema = DatabaseSchema.from_json(cached)
            self.local_cache[connection_id] = schema
            return schema

        # L3: Database
        db_schema = await self.db.get(SchemaSnapshot, connection_id)
        if db_schema:
            schema = DatabaseSchema.from_json(db_schema.data)
            await self.redis.set(f"schema:{connection_id}", db_schema.data, ttl=3600)
            self.local_cache[connection_id] = schema
            return schema

        return None

    async def refresh(self, connection_id: str) -> DatabaseSchema:
        """Extract fresh schema and update all cache layers."""

    async def invalidate(self, connection_id: str) -> None:
        """Invalidate schema across all layers."""
```

### 4.6 Schema Diff

```python
# libs/shared/sql2ai_shared/schema/diff.py

@dataclass
class SchemaDiff:
    """Represents differences between two schema versions."""

    added_tables: List[Table]
    removed_tables: List[str]
    modified_tables: List[TableDiff]
    added_columns: Dict[str, List[Column]]
    removed_columns: Dict[str, List[str]]
    modified_columns: Dict[str, List[ColumnDiff]]

class SchemaDiffer:
    """Compare two schema versions."""

    def diff(self, before: DatabaseSchema, after: DatabaseSchema) -> SchemaDiff:
        """Generate diff between two schema versions."""

    def to_migration(self, diff: SchemaDiff, dialect: DatabaseDialect) -> str:
        """Generate migration SQL from diff."""
```

### 4.7 AI Context Builder

```python
# libs/shared/sql2ai_shared/schema/context.py

class SchemaContextBuilder:
    """Build optimized schema context for AI prompts."""

    def __init__(self, schema: DatabaseSchema):
        self.schema = schema

    def build_full_context(self, max_tokens: int = 4000) -> str:
        """Build complete schema context, truncating if needed."""

    def build_relevant_context(
        self,
        query: str,
        tables: Optional[List[str]] = None,
        max_tokens: int = 2000,
    ) -> str:
        """Build context relevant to a specific query."""

    def build_table_context(self, table_name: str) -> str:
        """Build detailed context for a single table."""

    def to_ddl(self, tables: Optional[List[str]] = None) -> str:
        """Generate CREATE TABLE statements."""
```

### 4.8 Implementation Steps

1. **Schema Models** (Day 1)
   - Define all schema dataclasses
   - Serialization/deserialization
   - Context string formatting

2. **SQL Server Extractor** (Day 2)
   - System view queries
   - Column extraction
   - Index extraction
   - Relationship extraction

3. **PostgreSQL Extractor** (Day 3)
   - information_schema queries
   - Handle PostgreSQL-specific types
   - Extension support

4. **Schema Cache** (Day 4)
   - Redis integration
   - Database persistence
   - Invalidation logic

5. **API Endpoints** (Day 5)
   - GET /schema/{connection_id}
   - GET /schema/{connection_id}/tables
   - GET /schema/{connection_id}/tables/{table}
   - POST /schema/{connection_id}/refresh

6. **AI Context Builder** (Day 6)
   - Token estimation
   - Relevance filtering
   - DDL generation

---

## Part 5: Phase A - AI Features Integration

### 5.1 Overview

Wire up the prompt system to the API endpoints and make AI features functional.

### 5.2 AI Service Layer

```python
# apps/api/src/services/ai_service.py

class AIService:
    """Orchestrates AI operations for SQL2.AI."""

    def __init__(
        self,
        executor: PromptExecutor,
        schema_cache: SchemaCache,
        settings: Settings,
    ):
        self.executor = executor
        self.schema_cache = schema_cache
        self.settings = settings

    async def generate_query(
        self,
        request: str,
        connection_id: str,
        context: RequestContext,
    ) -> GeneratedQueryResult:
        """Generate SQL from natural language."""

        # Get schema context
        schema = await self.schema_cache.get(connection_id)
        schema_context = SchemaContextBuilder(schema).build_relevant_context(request)

        # Create prompt
        prompt = QueryGenerationPrompt(
            request=request,
            dialect=schema.dialect,
            schema_context=schema_context,
        )

        # Execute with tracking
        result = await self.executor.execute(
            prompt,
            context={
                "tenant_id": context.tenant_id,
                "user_id": context.user_id,
                "request_id": context.request_id,
            }
        )

        # Parse and validate generated SQL
        if result.success:
            sql = self._extract_sql(result.content)
            validation = await self._validate_sql(sql, connection_id)

            return GeneratedQueryResult(
                sql=sql,
                explanation=self._extract_explanation(result.content),
                confidence=self._estimate_confidence(result),
                validation=validation,
                prompt_hash=result.prompt_hash,
                tokens_used=result.tokens_used,
            )
        else:
            raise AIGenerationError(result.error)

    async def optimize_query(
        self,
        sql: str,
        connection_id: str,
        context: RequestContext,
    ) -> OptimizationResult:
        """Analyze and optimize a SQL query."""

        schema = await self.schema_cache.get(connection_id)

        # Get execution plan if possible
        execution_plan = await self._get_execution_plan(sql, connection_id)

        prompt = QueryOptimizationPrompt(
            sql=sql,
            dialect=schema.dialect,
            schema_context=SchemaContextBuilder(schema).build_full_context(),
            execution_plan=execution_plan,
        )

        result = await self.executor.execute(prompt, context=context.to_dict())

        return self._parse_optimization_result(result)

    async def explain_query(
        self,
        sql: str,
        audience: str = "technical",
        detail_level: str = "standard",
    ) -> ExplanationResult:
        """Explain what a SQL query does."""

        prompt = QueryExplanationPrompt(
            sql=sql,
            audience=audience,
            detail_level=detail_level,
        )

        result = await self.executor.execute(prompt)

        return ExplanationResult(
            explanation=result.content,
            prompt_hash=result.prompt_hash,
        )

    async def check_compliance(
        self,
        sql_or_schema: str,
        frameworks: List[ComplianceFramework],
        context: RequestContext,
    ) -> ComplianceResult:
        """Check for compliance violations."""

        prompt = ComplianceCheckPrompt(
            sql_or_schema=sql_or_schema,
            frameworks=frameworks,
        )

        result = await self.executor.execute(prompt, context=context.to_dict())

        return self._parse_compliance_result(result)
```

### 5.3 Updated Query Router

```python
# apps/api/src/routers/queries.py

@router.post("/generate", response_model=GenerateResponse)
async def generate_query(
    request: GenerateRequest,
    ai_service: AIService = Depends(get_ai_service),
    current_user: User = Depends(get_current_user),
    context: RequestContext = Depends(get_request_context),
):
    """Generate SQL from natural language using AI."""

    result = await ai_service.generate_query(
        request=request.prompt,
        connection_id=request.connection_id,
        context=context,
    )

    return GenerateResponse(
        sql=result.sql,
        explanation=result.explanation,
        confidence=result.confidence,
        validation=result.validation,
        prompt_version=result.prompt_version,
        prompt_hash=result.prompt_hash,
        tokens_used=result.tokens_used,
    )
```

### 5.4 Streaming Support

```python
# apps/api/src/routers/queries.py

@router.post("/generate/stream")
async def generate_query_stream(
    request: GenerateRequest,
    ai_service: AIService = Depends(get_ai_service),
):
    """Stream SQL generation for real-time feedback."""

    async def event_generator():
        async for chunk in ai_service.generate_query_stream(
            request=request.prompt,
            connection_id=request.connection_id,
        ):
            yield f"data: {json.dumps(chunk)}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

### 5.5 Query Execution Integration

```python
# apps/api/src/services/query_executor.py

class QueryExecutor:
    """Execute queries against target databases."""

    async def execute(
        self,
        connection: Connection,
        sql: str,
        parameters: Optional[Dict] = None,
        max_rows: int = 1000,
        timeout: int = 30,
    ) -> QueryResult:
        """Execute a query and return results."""

        # Get connection from pool
        pool = await self._get_pool(connection)

        async with pool.acquire() as conn:
            # Set query timeout
            await conn.execute(f"SET STATEMENT_TIMEOUT = {timeout * 1000}")

            start_time = time.time()

            try:
                # Execute query
                if self._is_select(sql):
                    result = await conn.fetch(sql, *parameters.values() if parameters else [])
                    rows = [dict(row) for row in result[:max_rows]]
                    columns = list(result[0].keys()) if result else []
                else:
                    result = await conn.execute(sql, *parameters.values() if parameters else [])
                    rows = []
                    columns = []

                duration_ms = (time.time() - start_time) * 1000

                return QueryResult(
                    columns=columns,
                    rows=rows,
                    row_count=len(rows),
                    duration_ms=duration_ms,
                    truncated=len(result) > max_rows if self._is_select(sql) else False,
                )

            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                raise QueryExecutionError(
                    message=str(e),
                    sql=sql,
                    duration_ms=duration_ms,
                )
```

### 5.6 Implementation Steps

1. **AI Service Layer** (Day 1-2)
   - AIService class
   - Integration with PromptExecutor
   - Schema context building

2. **Update Query Endpoints** (Day 3)
   - Wire generate endpoint
   - Wire optimize endpoint
   - Wire explain endpoint

3. **Query Execution** (Day 4-5)
   - Connection pool management
   - SQL Server execution
   - PostgreSQL execution
   - Result formatting

4. **Streaming** (Day 6)
   - SSE endpoint
   - Frontend integration
   - Progress updates

5. **Compliance Integration** (Day 7)
   - Compliance endpoint
   - Report generation
   - Finding storage

6. **Testing & Polish** (Day 8)
   - Integration tests
   - Error handling
   - Performance optimization

---

## Timeline Summary

| Phase | Description | Duration |
|-------|-------------|----------|
| **MCP Server** | Model Context Protocol server | 5 days |
| **CLI** | Command-line interface | 8 days |
| **Phase C** | Frontend Application | 12 days |
| **Phase B** | Authentication Layer | 4 days |
| **Phase D** | Schema Engine | 6 days |
| **Phase A** | AI Features Integration | 8 days |
| **Total** | | ~43 days |

Note: Phases can overlap. MCP Server and CLI can be built in parallel with other phases, sharing common database connection and schema extraction code.

---

## Success Criteria

### MVP Complete When:
1. ✅ User can sign up and log in (Clerk)
2. ✅ User can add and test database connections
3. ✅ User can view database schema
4. ✅ User can write and execute SQL queries
5. ✅ User can generate SQL from natural language
6. ✅ User can get query optimization suggestions
7. ✅ MCP server allows Claude to interact with databases
8. ✅ Basic compliance scanning works
9. ✅ CLI can manage connections and run migrations
10. ✅ CLI can generate TypeScript/C# types from schema
11. ✅ CLI integrates with CI/CD pipelines

### Quality Gates:
- [ ] All endpoints have authentication
- [ ] All mutations have audit logging
- [ ] Error handling is consistent
- [ ] API documentation is complete
- [ ] Frontend is responsive
- [ ] Loading states are implemented
- [ ] Empty states are designed
