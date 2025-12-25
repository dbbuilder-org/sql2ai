import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Tenant - Enterprise Multi-Tenancy | SQL2.AI',
  description:
    'Supabase-style multi-tenancy for SQL Server and PostgreSQL with Clerk integration. Standardized RLS patterns with complete data isolation.',
};

export default function TenantPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-[#6366F1]/10 flex items-center justify-center text-[#6366F1]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Tenant</h1>
                <p className="text-lg text-[#6366F1] font-medium">Multi-Tenancy Platform</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Supabase-style multi-tenancy for SQL Server and PostgreSQL with Clerk integration.
              Standardized Row-Level Security patterns that eliminate complexity while ensuring
              complete data isolation with full certainty.
            </p>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">How It Works</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
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
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* RLS Implementation */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Automatic RLS Policies</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">PostgreSQL</h3>
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Enable RLS on table
ALTER TABLE customers
ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation
ON customers
USING (
  tenant_id = current_setting('app.tenant_id')::uuid
);

-- Set tenant context
SET app.tenant_id = 'abc-123-def';

-- All queries auto-filtered!
SELECT * FROM customers;
-- Internally: WHERE tenant_id = 'abc-123-def'`}</code>
              </pre>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">SQL Server (2016+)</h3>
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Security predicate function
CREATE FUNCTION dbo.fn_TenantPredicate
  (@TenantId UNIQUEIDENTIFIER)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN SELECT 1 AS result
WHERE @TenantId = CAST(
  SESSION_CONTEXT(N'tenant_id')
  AS UNIQUEIDENTIFIER
);

-- Security policy
CREATE SECURITY POLICY TenantPolicy
ADD FILTER PREDICATE
  dbo.fn_TenantPredicate(tenant_id)
  ON dbo.Customers
WITH (STATE = ON);`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Clerk Integration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Clerk Integration</h2>
            <p className="text-text-secondary text-center mb-12">
              Clerk organizations map directly to tenants - authentication and authorization in one
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`// Generated middleware: tenantContext.ts
import { Clerk } from '@clerk/clerk-sdk-node';

export async function tenantContextMiddleware(req, res, next) {
  const token = req.headers.authorization?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    // Verify JWT and extract tenant
    const session = await clerk.verifyToken(token);
    const tenantId = session.org_id;  // Clerk org = tenant

    if (!tenantId) {
      return res.status(403).json({ error: 'No tenant context' });
    }

    // Set tenant context on database connection
    await req.db.execute(
      \`EXEC sp_set_session_context @key = 'tenant_id', @value = @tenantId\`,
      { tenantId }
    );

    req.tenantId = tenantId;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
}`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Isolation Patterns */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Isolation Patterns</h2>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            <div className="card p-6 border-[#6366F1] border-2">
              <h3 className="text-h5 text-[#6366F1] mb-4">Shared Database</h3>
              <p className="text-sm text-text-muted mb-4">Recommended</p>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• All tenants in one database</li>
                <li>• RLS enforces isolation</li>
                <li>• Cost-effective</li>
                <li>• Easy maintenance</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Schema Per Tenant</h3>
              <p className="text-sm text-text-muted mb-4">Better isolation</p>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• Separate schemas</li>
                <li>• Per-tenant optimization</li>
                <li>• Schema management overhead</li>
                <li>• Middle ground</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Database Per Tenant</h3>
              <p className="text-sm text-text-muted mb-4">Complete isolation</p>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• Separate databases</li>
                <li>• Maximum isolation</li>
                <li>• Higher cost</li>
                <li>• Enterprise compliance</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Tenant Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL TENANT DASHBOARD                           ║
╠══════════════════════════════════════════════════════════════════╣
║ TENANT OVERVIEW                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Tenants:      247                                           ║
║ Active (30d):       189                                           ║
║ Trial:              45                                            ║
║ Enterprise:         23                                            ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP TENANTS (by data volume)                                      ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. Acme Corp         12.4 GB    45,000 customers                  ║
║ 2. Globex Inc         8.2 GB    32,000 customers                  ║
║ 3. Initech            5.1 GB    18,000 customers                  ║
╠══════════════════════════════════════════════════════════════════╣
║ ISOLATION STATUS                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ All 15 tables have RLS policies                                ║
║ ✓ All queries filtered by tenant_id                               ║
║ ✓ No cross-tenant access detected                                 ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Build Multi-Tenant Apps"
        description="Enterprise multi-tenancy with complete data isolation and zero complexity."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
