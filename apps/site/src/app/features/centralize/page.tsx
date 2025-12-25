import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Centralize - Multi-Tier Replication Platform | SQL2.AI',
  description:
    'Foreign key aware, multi-tier replication with consolidation, distribution, and ETL variants. Minimally invasive for SQL Server and PostgreSQL.',
};

export default function CentralizePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#14B8A6]/10 flex items-center justify-center text-[#14B8A6]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Centralize</h1>
                <p className="text-lg text-[#14B8A6] font-medium">Data Replication Platform</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Minimally invasive, foreign key aware, multi-tier replication platform. Consolidation,
              distribution (pub/sub), and ETL variants for SQL Server and PostgreSQL.
            </p>
          </div>
        </div>
      </section>

      {/* Replication Modes */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Replication Modes</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { name: 'Consolidation', icon: '⬇️', desc: 'Many sources → One central database' },
              { name: 'Distribution', icon: '⬆️', desc: 'One source → Many targets' },
              { name: 'Pub/Sub', icon: '🔄', desc: 'Event-driven selective sync' },
              { name: 'ETL', icon: '🔀', desc: 'Transform during replication' },
            ].map((mode) => (
              <div key={mode.name} className="card p-6 text-center">
                <div className="text-3xl mb-3">{mode.icon}</div>
                <h3 className="text-h5 text-text-primary mb-1">{mode.name}</h3>
                <p className="text-sm text-text-muted">{mode.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Foreign Key Awareness */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Foreign Key Awareness</h2>
            <p className="text-text-secondary text-center mb-12">
              Replicates data in the correct order to maintain referential integrity
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`DEPENDENCY-AWARE REPLICATION ORDER
═══════════════════════════════════════════════════════════════

Source Database Analysis:
┌─────────────────────────────────────────────────────────────┐
│  Orders ──FK──► Customers                                   │
│  OrderItems ──FK──► Orders ──FK──► Products                │
│  Shipments ──FK──► Orders                                   │
│  Invoices ──FK──► Orders ──FK──► Customers                 │
└─────────────────────────────────────────────────────────────┘

Generated Replication Order:
  Step 1: Customers, Products       (no dependencies)
  Step 2: Orders                    (depends on Customers)
  Step 3: OrderItems, Shipments     (depends on Orders)
  Step 4: Invoices                  (depends on Orders)

Benefits:
  ✓ No FK violation errors
  ✓ No need to disable constraints
  ✓ Transactionally consistent
  ✓ Automatic rollback on failure`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Topology */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Multi-Tier Topology</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`MULTI-TIER REPLICATION EXAMPLE
═══════════════════════════════════════════════════════════════

                        ┌─────────────────┐
                        │   HEADQUARTERS  │
                        │   (Central DB)  │
                        └────────┬────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
    ┌───────────────┐   ┌───────────────┐   ┌───────────────┐
    │   REGION US   │   │  REGION EU    │   │  REGION APAC  │
    │   (Tier 1)    │   │   (Tier 1)    │   │   (Tier 1)    │
    └───────┬───────┘   └───────┬───────┘   └───────┬───────┘
            │                   │                   │
     ┌──────┼──────┐           ...                 ...
     │      │      │
     ▼      ▼      ▼
  ┌─────┐┌─────┐┌─────┐
  │ NY  ││ LA  ││ CHI │
  │(T2) ││(T2) ││(T2) │
  └─────┘└─────┘└─────┘

Sync Direction: ↕ Bidirectional (configurable)
Conflict Resolution: Last-write-wins / Custom rules`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Simple Configuration</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-centralize.yaml
topology:
  mode: consolidation
  sources:
    - name: branch_ny
      connection: \${NY_DB_CONNECTION}
      tables: [Customers, Orders, Products]

    - name: branch_la
      connection: \${LA_DB_CONNECTION}
      tables: [Customers, Orders, Products]

  target:
    name: headquarters
    connection: \${HQ_DB_CONNECTION}

replication:
  schedule: "*/5 * * * *"  # Every 5 minutes
  batch_size: 1000
  parallel_tables: 4

  conflict_resolution:
    strategy: last_write_wins
    timestamp_column: ModifiedAt

  filters:
    - table: Orders
      where: "Status != 'Draft'"

  transforms:
    - table: Customers
      add_column:
        name: SourceBranch
        value: "\${source.name}"`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Key Features</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'FK Awareness', desc: 'Automatic dependency ordering based on foreign keys' },
              { title: 'Minimally Invasive', desc: 'No triggers or schema changes required on source' },
              { title: 'Change Tracking', desc: 'Uses CDC, temporal tables, or polling' },
              { title: 'Conflict Resolution', desc: 'Configurable strategies for bidirectional sync' },
              { title: 'Transform Support', desc: 'Apply transformations during replication' },
              { title: 'Monitoring', desc: 'Real-time sync status and lag metrics' },
            ].map((feature) => (
              <div key={feature.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-2">{feature.title}</h3>
                <p className="text-sm text-text-muted">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Replication Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL CENTRALIZE STATUS                          ║
╠══════════════════════════════════════════════════════════════════╣
║ TOPOLOGY: Consolidation (3 sources → 1 target)                   ║
╠══════════════════════════════════════════════════════════════════╣
║ SOURCE STATUS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ branch_ny     │ ✓ Connected │ Lag: 12s  │ Last: 2min ago        ║
║ branch_la     │ ✓ Connected │ Lag: 8s   │ Last: 2min ago        ║
║ branch_chi    │ ✓ Connected │ Lag: 15s  │ Last: 2min ago        ║
╠══════════════════════════════════════════════════════════════════╣
║ LAST SYNC CYCLE                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Duration:     45 seconds                                          ║
║ Rows synced:  12,847                                              ║
║ Conflicts:    3 (resolved: last-write-wins)                       ║
║ Errors:       0                                                   ║
╠══════════════════════════════════════════════════════════════════╣
║ TABLE SYNC STATUS                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ Customers     │ 2,341 rows │ ✓ In sync                           ║
║ Orders        │ 8,472 rows │ ✓ In sync                           ║
║ Products      │ 1,234 rows │ ✓ In sync                           ║
║ OrderItems    │ 45,892 rows│ ✓ In sync                           ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Centralize Your Data"
        description="Multi-tier replication with FK awareness and minimal source impact."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
