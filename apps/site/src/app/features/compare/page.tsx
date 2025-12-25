import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'SQL Compare - AI Schema Comparison | SQL2.AI',
  description:
    'AI-powered hands-off comparison between databases. Generates modular, implementable sync scripts to align DDL and code across environments.',
};

export default function ComparePage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 bg-gradient-to-b from-bg-surface to-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-500 mb-6">
              <span className="text-sm font-medium">Developer Tools</span>
            </div>
            <h1 className="text-h1 mb-6">
              SQL <span className="gradient-text">Compare</span>
            </h1>
            <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
              AI-powered hands-off comparison between databases. Generates modular, implementable
              sync scripts to align DDL and code across environments.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact" className="btn-primary">
                Get Started
              </Link>
              <Link href="/docs/compare" className="btn-secondary">
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Output */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-h2 text-center mb-8">Intelligent Schema Comparison</h2>
            <div className="card p-8 bg-bg-surface">
              <pre className="text-sm text-text-secondary overflow-x-auto font-mono">
{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL COMPARE RESULTS                            ║
║                                                                   ║
║  Source: dev-database        Target: prod-database               ║
║  Compared: 2024-12-25 10:30  Duration: 4.2 seconds                ║
╠══════════════════════════════════════════════════════════════════╣
║ SUMMARY                                                           ║
║ ─────────────────────────────────────────────────────────────── ║
║  Tables:         +3 new    2 modified    0 deleted               ║
║  Views:          +1 new    1 modified    0 deleted               ║
║  Stored Procs:   +5 new    8 modified    1 deleted               ║
║  Functions:      +0 new    2 modified    0 deleted               ║
║  Indexes:        +4 new    0 modified    2 deleted               ║
╠══════════════════════════════════════════════════════════════════╣
║ MODULAR SYNC SCRIPTS GENERATED                                    ║
║ ─────────────────────────────────────────────────────────────── ║
║                                                                   ║
║  📁 sync-scripts/                                                 ║
║  ├── 01-tables/                                                   ║
║  │   ├── 01-create-CustomerPreferences.sql                       ║
║  │   ├── 02-create-OrderAuditLog.sql                             ║
║  │   ├── 03-create-ShippingZones.sql                             ║
║  │   ├── 04-alter-Orders-add-tracking.sql                        ║
║  │   └── 05-alter-Products-add-weight.sql                        ║
║  ├── 02-views/                                                    ║
║  │   ├── 01-create-vw_CustomerOrders.sql                         ║
║  │   └── 02-alter-vw_SalesReport.sql                             ║
║  ├── 03-procedures/                                               ║
║  │   ├── 01-create-sp_ProcessRefund.sql                          ║
║  │   ├── 02-alter-sp_GetCustomerOrders.sql                       ║
║  │   └── ... (11 more)                                           ║
║  ├── 04-functions/                                                ║
║  │   └── 01-alter-fn_CalculateDiscount.sql                       ║
║  ├── 05-indexes/                                                  ║
║  │   ├── 01-create-IX_Orders_CustomerDate.sql                    ║
║  │   └── ... (3 more)                                            ║
║  └── 00-deploy-all.sql          ← Master deployment script       ║
║                                                                   ║
║  [Deploy to Target] [Export Scripts] [View Details]              ║
╚══════════════════════════════════════════════════════════════════╝`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <h2 className="text-h2 text-center mb-12">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                title: 'AI-Driven Comparison',
                description:
                  'Intelligent comparison that understands semantic differences, not just text changes. Detects refactored code and renamed objects.',
                icon: '🤖',
              },
              {
                title: 'Modular Scripts',
                description:
                  'Generates individual, reviewable scripts for each change. No monolithic deployment files that are impossible to debug.',
                icon: '📦',
              },
              {
                title: 'Safe Deployment Order',
                description:
                  'Automatically orders scripts based on dependencies. Tables before FKs, functions before procedures that use them.',
                icon: '🔒',
              },
              {
                title: 'DDL & Code Coverage',
                description:
                  'Compares tables, views, stored procedures, functions, triggers, indexes, constraints, and permissions.',
                icon: '📋',
              },
              {
                title: 'Environment Aware',
                description:
                  'Handles environment-specific configurations. Excludes dev-only objects, adjusts for staging vs production.',
                icon: '🌍',
              },
              {
                title: 'Rollback Scripts',
                description:
                  'Automatically generates rollback scripts for each change. One-click undo if something goes wrong.',
                icon: '↩️',
              },
            ].map((feature) => (
              <div key={feature.title} className="card p-6">
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h3 className="text-h5 mb-2">{feature.title}</h3>
                <p className="text-text-secondary text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Detailed Diff View */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-h2 text-center mb-8">Detailed Diff View</h2>
            <div className="card p-6 bg-bg-surface">
              <div className="text-sm font-mono mb-4 text-text-muted">
                Comparing: dbo.sp_GetCustomerOrders
              </div>
              <pre className="text-sm overflow-x-auto">
{`  CREATE PROCEDURE dbo.sp_GetCustomerOrders
    @CustomerId INT,
-   @StartDate DATE = NULL
+   @StartDate DATE = NULL,
+   @IncludeReturns BIT = 0
  AS
  BEGIN
    SELECT
      o.OrderId,
      o.OrderDate,
      o.Total,
-     o.Status
+     o.Status,
+     o.TrackingNumber,
+     CASE WHEN r.ReturnId IS NOT NULL THEN 1 ELSE 0 END AS HasReturn
    FROM Orders o
+   LEFT JOIN Returns r ON o.OrderId = r.OrderId
+     AND @IncludeReturns = 1
    WHERE o.CustomerId = @CustomerId
      AND (@StartDate IS NULL OR o.OrderDate >= @StartDate)
    ORDER BY o.OrderDate DESC
  END`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CLI Example */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-center mb-8">CLI Usage</h2>
            <div className="card p-6 bg-bg-primary">
              <pre className="text-sm text-text-secondary overflow-x-auto">
{`# Compare two databases
sql2ai compare \\
  --source "Server=dev-db;Database=AppDB" \\
  --target "Server=prod-db;Database=AppDB" \\
  --output ./sync-scripts

# Compare with options
sql2ai compare \\
  --source dev-db \\
  --target prod-db \\
  --include tables,views,procedures \\
  --exclude "*_backup,*_temp" \\
  --generate-rollback \\
  --output ./deployment

# Preview changes without generating scripts
sql2ai compare --source dev-db --target prod-db --preview

# Compare specific objects
sql2ai compare \\
  --source dev-db \\
  --target prod-db \\
  --objects "dbo.Orders,dbo.sp_*"

# Deploy generated scripts
sql2ai compare deploy \\
  --scripts ./sync-scripts \\
  --target prod-db \\
  --dry-run

# Generate deployment report
sql2ai compare report \\
  --source dev-db \\
  --target prod-db \\
  --format html \\
  --output comparison-report.html`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 mb-12">Deployment Workflow</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { step: '1', title: 'Compare', desc: 'Analyze source and target schemas' },
                { step: '2', title: 'Review', desc: 'Examine modular sync scripts' },
                { step: '3', title: 'Test', desc: 'Dry-run on staging environment' },
                { step: '4', title: 'Deploy', desc: 'Execute with rollback ready' },
              ].map((item) => (
                <div key={item.step} className="card p-6 text-center">
                  <div className="w-10 h-10 rounded-full bg-cyan-500/20 text-cyan-500 flex items-center justify-center mx-auto mb-4 font-bold">
                    {item.step}
                  </div>
                  <div className="font-medium text-text-primary mb-2">{item.title}</div>
                  <div className="text-xs text-text-muted">{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-h2 mb-6">Stop Manual Schema Comparisons</h2>
            <p className="text-text-secondary mb-8">
              Let SQL Compare handle the tedious work of finding differences and generating
              deployment-ready sync scripts.
            </p>
            <Link href="/contact" className="btn-primary">
              Request Demo
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
