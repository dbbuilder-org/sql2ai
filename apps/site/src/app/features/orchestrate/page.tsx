import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Orchestrate - Unified Job Scheduling & Monitoring | SQL2.AI',
  description:
    'Unified orchestration platform managing Azure Functions, Lambda, GCP Cloud Functions, and cron jobs. One scheduling platform for all SQL2.AI operations.',
};

export default function OrchestratePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-primary/10 flex items-center justify-center text-primary">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Orchestrate</h1>
                <p className="text-lg text-primary font-medium">Unified Job Scheduling</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              The central orchestration platform for all SQL2.AI operations. Manage Azure Functions,
              AWS Lambda, GCP Cloud Functions, and cron jobs from one unified interface with
              integrated monitoring in SQL Monitor.
            </p>
          </div>
        </div>
      </section>

      {/* Supported Platforms */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Managed Platforms</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { name: 'Azure Functions', icon: '⚡', desc: 'Timer & HTTP triggers' },
              { name: 'AWS Lambda', icon: '🔶', desc: 'EventBridge scheduling' },
              { name: 'GCP Cloud Functions', icon: '☁️', desc: 'Cloud Scheduler' },
              { name: 'Cron Jobs', icon: '⏰', desc: 'Traditional cron' },
            ].map((platform) => (
              <div key={platform.name} className="card p-6 text-center">
                <div className="text-3xl mb-3">{platform.icon}</div>
                <h3 className="text-h5 text-text-primary mb-1">{platform.name}</h3>
                <p className="text-sm text-text-muted">{platform.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Key Capabilities</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Unified Scheduling</h3>
              <p className="text-text-secondary mb-4">
                One interface to schedule jobs across all platforms with consistent syntax.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Cron expression support</li>
                <li>Rate-based scheduling</li>
                <li>Event-driven triggers</li>
                <li>Manual invocation</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Module Operations</h3>
              <p className="text-text-secondary mb-4">
                Schedule operations for all SQL2.AI modules from one place.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Key rotation (SQL Encrypt)</li>
                <li>Compliance scans (SQL Comply)</li>
                <li>Replication sync (SQL Centralize)</li>
                <li>Data generation (SQL Simulate)</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Before/After Context</h3>
              <p className="text-text-secondary mb-4">
                Capture schema snapshots and compare changes for impact analysis.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Schema snapshots</li>
                <li>Diff engine</li>
                <li>Breaking change detection</li>
                <li>Migration validation</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Unified Architecture</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`SQL ORCHESTRATE - UNIFIED SCHEDULING
═══════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                    SQL ORCHESTRATE                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │   Unified Job Scheduler                                    │ │
│  │   • Cron expressions                                       │ │
│  │   • Rate-based scheduling                                  │ │
│  │   • Event-driven triggers                                  │ │
│  │   • Dependency chains                                      │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
└─────────────────────────┼───────────────────────────────────────┘
                          │
     ┌────────────────────┼────────────────────┐
     │                    │                    │
     ▼                    ▼                    ▼
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   Azure     │   │    AWS      │   │    GCP      │
│  Functions  │   │   Lambda    │   │  Functions  │
└─────────────┘   └─────────────┘   └─────────────┘
     │                    │                    │
     └────────────────────┼────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL2.AI MODULES                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │ Encrypt  │ │  Comply  │ │Centralize│ │  Audit   │  ...     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL MONITOR                                   │
│  • Execution history    • Performance metrics                   │
│  • Error tracking       • Alerting                              │
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration Example */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Configuration</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-orchestrate.yaml
jobs:
  # Encryption key rotation
  - name: rotate-tde-keys
    module: sql-encrypt
    action: rotate-keys
    schedule: "0 2 * * 0"  # Sundays at 2 AM
    platform: azure-functions
    config:
      key_type: tde
      notify_on_complete: true

  # Compliance scan
  - name: daily-compliance-scan
    module: sql-comply
    action: full-scan
    schedule: "0 6 * * *"  # Daily at 6 AM
    platform: aws-lambda
    config:
      frameworks: [soc2, hipaa, pci-dss]
      report_format: pdf

  # Data replication
  - name: sync-branch-data
    module: sql-centralize
    action: sync
    schedule: "*/5 * * * *"  # Every 5 minutes
    platform: gcp-functions
    config:
      sources: [branch_ny, branch_la, branch_chi]

  # Job dependency chain
  - name: nightly-maintenance
    steps:
      - job: optimize-indexes
      - job: update-statistics
        depends_on: optimize-indexes
      - job: generate-reports
        depends_on: update-statistics`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Orchestration Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL ORCHESTRATE DASHBOARD                      ║
╠══════════════════════════════════════════════════════════════════╣
║ ACTIVE JOBS                                                       ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Jobs:       47                                              ║
║ Running:          3                                               ║
║ Scheduled (24h):  156                                             ║
║ Failed (24h):     2                                               ║
╠══════════════════════════════════════════════════════════════════╣
║ PLATFORM DISTRIBUTION                                             ║
║ ─────────────────────────────────────────────────────────────── ║
║ Azure Functions:  23 jobs  │ ✓ All healthy                       ║
║ AWS Lambda:       15 jobs  │ ✓ All healthy                       ║
║ GCP Functions:    6 jobs   │ ✓ All healthy                       ║
║ Cron:             3 jobs   │ ✓ All healthy                       ║
╠══════════════════════════════════════════════════════════════════╣
║ RECENT EXECUTIONS                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ rotate-tde-keys     │ ✓ Completed │ 2min ago  │ 45s duration     ║
║ sync-branch-data    │ ✓ Completed │ 3min ago  │ 12s duration     ║
║ compliance-scan     │ ► Running   │ Started 5min ago              ║
║ backup-verification │ ✗ Failed    │ 1hr ago   │ Retry scheduled  ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Integration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Orchestrates All SQL2.AI Modules</h2>
            <p className="text-text-secondary mb-8">
              One scheduling platform for every SQL2.AI operation
            </p>

            <div className="grid md:grid-cols-4 gap-4">
              {[
                'SQL Encrypt', 'SQL Comply', 'SQL Centralize', 'SQL Audit',
                'SQL Test', 'SQL Anonymize', 'SQL Simulate', 'SQL Optimize',
              ].map((module) => (
                <div key={module} className="card p-3 text-center">
                  <span className="text-sm text-text-primary">{module}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Unify Your Database Operations"
        description="One scheduling platform for all SQL2.AI modules across Azure, AWS, GCP, and on-prem."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
