# SQL Tenant

**Enterprise Multi-Tenancy Platform**

## Overview

SQL Tenant brings Supabase-style multi-tenancy to SQL Server and PostgreSQL with Clerk integration for authentication. It provides standardized Row-Level Security (RLS) patterns that eliminate the complexity of multi-tenant implementations while ensuring complete data isolation with full certainty.

## The Problem

### Current Multi-Tenancy Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Complex RLS setup | Manual policies | Security gaps |
| Tenant leakage | Ad-hoc filtering | Data exposure |
| Auth integration | Custom code | Inconsistent |
| Performance | WHERE tenant_id= | Missing indexes |
| Tenant onboarding | Manual process | Slow, error-prone |
| Schema changes | Per-tenant updates | Drift, maintenance |

## SQL Tenant Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │  Frontend (React/Vue/Next.js)                               ││
│  │         │                                                   ││
│  │         ▼                                                   ││
│  │  ┌─────────────┐                                            ││
│  │  │    Clerk    │ ← Authentication & Tenant Context          ││
│  │  └──────┬──────┘                                            ││
│  └─────────┼───────────────────────────────────────────────────┘│
└────────────┼────────────────────────────────────────────────────┘
             │ JWT with tenant_id claim
             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL TENANT LAYER                              │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Extract tenant_id from JWT                             │ │
│  │  2. Set session context                                    │ │
│  │  3. RLS policies automatically filter all queries          │ │
│  │  4. Audit all tenant data access                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE (SQL Server / PostgreSQL)            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  All tables with tenant_id column                          │ │
│  │  RLS policies enforce tenant isolation                     │ │
│  │  Indexes optimized for tenant queries                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Clerk Integration

### Setup

```yaml
# sql2ai-tenant.yaml
authentication:
  provider: clerk
  config:
    publishable_key: ${CLERK_PUBLISHABLE_KEY}
    secret_key: ${CLERK_SECRET_KEY}
    jwt_claim: org_id  # Clerk organization = tenant

  session_context:
    sql_server: SESSION_CONTEXT
    postgresql: set_config

tenancy:
  mode: shared_database  # or database_per_tenant
  tenant_column: tenant_id
  tenant_type: uuid  # or int, varchar
```

### Middleware

```typescript
// Generated: middleware/tenantContext.ts
import { Clerk } from '@clerk/clerk-sdk-node';
import { NextFunction, Request, Response } from 'express';

export async function tenantContextMiddleware(
  req: Request,
  res: Response,
  next: NextFunction
) {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Verify JWT and extract tenant
    const session = await clerk.verifyToken(token);
    const tenantId = session.org_id;

    if (!tenantId) {
      return res.status(403).json({ error: 'No tenant context' });
    }

    // Set tenant context on database connection
    await req.db.execute(
      `EXEC sp_set_session_context @key = 'tenant_id', @value = @tenantId`,
      { tenantId }
    );

    req.tenantId = tenantId;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}
```

## RLS Implementation

### PostgreSQL

```sql
-- Enable RLS on table
ALTER TABLE customers ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation ON customers
    USING (tenant_id = current_setting('app.tenant_id')::uuid);

-- Force RLS for table owners too
ALTER TABLE customers FORCE ROW LEVEL SECURITY;

-- Set tenant context
SET app.tenant_id = 'abc-123-def';

-- All queries automatically filtered
SELECT * FROM customers;
-- Internally: SELECT * FROM customers WHERE tenant_id = 'abc-123-def'
```

### SQL Server (2016+)

```sql
-- Create security predicate function
CREATE FUNCTION dbo.fn_TenantSecurityPredicate(@TenantId UNIQUEIDENTIFIER)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @TenantId = CAST(SESSION_CONTEXT(N'tenant_id') AS UNIQUEIDENTIFIER);

-- Create security policy
CREATE SECURITY POLICY TenantPolicy
ADD FILTER PREDICATE dbo.fn_TenantSecurityPredicate(tenant_id) ON dbo.Customers,
ADD FILTER PREDICATE dbo.fn_TenantSecurityPredicate(tenant_id) ON dbo.Orders,
ADD FILTER PREDICATE dbo.fn_TenantSecurityPredicate(tenant_id) ON dbo.Products
WITH (STATE = ON);

-- Set tenant context
EXEC sp_set_session_context @key = N'tenant_id', @value = 'abc-123-def';

-- All queries automatically filtered
SELECT * FROM Customers;
-- Internally filtered by security policy
```

## SQL Tenant CLI Commands

### Initialize Multi-Tenancy

```bash
# Initialize tenant schema
sql2ai tenant init --connection "..."

# Add tenant column to existing tables
sql2ai tenant add-column --tables all

# Create RLS policies
sql2ai tenant create-policies --tables all

# Onboard new tenant
sql2ai tenant create --name "Acme Corp" --id "acme-123"
```

### Generated Schema

```sql
-- Generated: sql2ai_tenant schema
CREATE SCHEMA sql2ai_tenant;

-- Tenant registry
CREATE TABLE sql2ai_tenant.Tenants (
    TenantId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    Name NVARCHAR(200) NOT NULL,
    Slug NVARCHAR(100) UNIQUE NOT NULL,
    ClerkOrgId NVARCHAR(100) UNIQUE,
    Plan NVARCHAR(50) DEFAULT 'free',
    CreatedAt DATETIME2 DEFAULT GETUTCDATE(),
    Settings NVARCHAR(MAX)  -- JSON
);

-- Tenant users mapping
CREATE TABLE sql2ai_tenant.TenantUsers (
    TenantUserId UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    TenantId UNIQUEIDENTIFIER REFERENCES sql2ai_tenant.Tenants(TenantId),
    ClerkUserId NVARCHAR(100) NOT NULL,
    Role NVARCHAR(50) DEFAULT 'member',
    UNIQUE(TenantId, ClerkUserId)
);
```

## Tenant Isolation Patterns

### Pattern 1: Shared Database (Recommended)

```
Database: AppDB
├── Customers (tenant_id, ...)
├── Orders (tenant_id, ...)
├── Products (tenant_id, ...)
└── RLS policies enforce isolation
```

**Pros:** Simple, cost-effective, easy to maintain
**Cons:** Noisy neighbor potential, shared resources

### Pattern 2: Schema Per Tenant

```
Database: AppDB
├── tenant_acme/
│   ├── Customers
│   ├── Orders
│   └── Products
├── tenant_globex/
│   ├── Customers
│   ├── Orders
│   └── Products
```

**Pros:** Better isolation, per-tenant optimization
**Cons:** Schema management overhead

### Pattern 3: Database Per Tenant

```
Databases:
├── AppDB_acme
├── AppDB_globex
├── AppDB_initech
```

**Pros:** Complete isolation, easy compliance
**Cons:** Higher cost, management complexity

## Tenant-Aware Queries

### Standard Query (Auto-Filtered)

```sql
-- Developer writes:
SELECT * FROM Customers WHERE Status = 'Active';

-- SQL Tenant executes (automatically filtered):
SELECT * FROM Customers
WHERE Status = 'Active'
AND tenant_id = @CurrentTenantId;  -- Injected by RLS
```

### Cross-Tenant Query (Admin Only)

```sql
-- Requires elevated permissions
EXEC sp_set_session_context @key = 'bypass_rls', @value = 'true';

SELECT t.Name AS Tenant, COUNT(*) AS CustomerCount
FROM Customers c
JOIN sql2ai_tenant.Tenants t ON c.tenant_id = t.TenantId
GROUP BY t.Name;
```

## Tenant Onboarding

```yaml
# Automated tenant provisioning
onboarding:
  steps:
    - create_tenant_record
    - sync_with_clerk
    - create_initial_data
    - send_welcome_email

  initial_data:
    - template: default_settings
    - template: sample_data  # Optional demo data
```

```typescript
// Generated: services/tenantOnboarding.ts
export async function onboardTenant(clerkOrg: ClerkOrganization) {
  // 1. Create tenant record
  const tenant = await db.query(`
    INSERT INTO sql2ai_tenant.Tenants (Name, Slug, ClerkOrgId, Plan)
    VALUES (@name, @slug, @clerkOrgId, @plan)
    RETURNING TenantId
  `, {
    name: clerkOrg.name,
    slug: clerkOrg.slug,
    clerkOrgId: clerkOrg.id,
    plan: 'trial'
  });

  // 2. Create initial data
  await seedTenantData(tenant.TenantId);

  // 3. Send welcome email
  await sendWelcomeEmail(clerkOrg.adminEmail);

  return tenant;
}
```

## Performance Optimization

```sql
-- Optimized indexes for tenant queries
CREATE INDEX IX_Customers_TenantId
ON Customers (tenant_id)
INCLUDE (Name, Email, Status);

CREATE INDEX IX_Orders_TenantId_Date
ON Orders (tenant_id, OrderDate DESC)
INCLUDE (Total, Status);

-- Filtered statistics per tenant (high-volume tenants)
CREATE STATISTICS STAT_Customers_Acme
ON Customers (Status, CreatedDate)
WHERE tenant_id = 'acme-123-uuid';
```

## Dashboard

```
╔══════════════════════════════════════════════════════════════════╗
║                    SQL TENANT DASHBOARD                          ║
╠══════════════════════════════════════════════════════════════════╣
║ TENANT OVERVIEW                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Tenants:      247                                          ║
║ Active (30d):       189                                          ║
║ Trial:              45                                           ║
║ Enterprise:         23                                           ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP TENANTS (by data volume)                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. Acme Corp         12.4 GB    45,000 customers                 ║
║ 2. Globex Inc         8.2 GB    32,000 customers                 ║
║ 3. Initech            5.1 GB    18,000 customers                 ║
╠══════════════════════════════════════════════════════════════════╣
║ ISOLATION STATUS                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ All 15 tables have RLS policies                               ║
║ ✓ All queries filtered by tenant_id                              ║
║ ✓ No cross-tenant access detected                                ║
╚══════════════════════════════════════════════════════════════════╝
```

## Integration Points

- **SQL Audit**: Log all tenant access
- **SQL Comply**: Per-tenant compliance reports
- **SQL Anonymize**: Tenant-aware anonymization
- **SQL API**: Tenant-scoped API generation
