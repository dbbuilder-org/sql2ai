import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'SQL Monitor - Real-Time Database Monitoring | SQL2.AI',
  description:
    'Comprehensive monitoring dashboard for SQL Server and PostgreSQL. Track performance, connections, queries, and health metrics in real-time.',
};

export default function MonitorPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 bg-gradient-to-b from-bg-surface to-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-info/10 border border-info/30 text-info mb-6">
              <span className="text-sm font-medium">DBA Tools</span>
            </div>
            <h1 className="text-h1 mb-6">
              SQL <span className="gradient-text">Monitor</span>
            </h1>
            <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
              Comprehensive monitoring dashboard for SQL Server and PostgreSQL. Track performance,
              connections, queries, and health metrics in real-time.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact" className="btn-primary">
                Get Started
              </Link>
              <Link href="/docs/monitor" className="btn-secondary">
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <div className="card p-8 bg-bg-surface border-info/30">
              <pre className="text-sm text-text-secondary overflow-x-auto font-mono">
{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL MONITOR DASHBOARD                          ║
╠══════════════════════════════════════════════════════════════════╣
║ DATABASE: production-db-01          STATUS: ✓ Healthy             ║
╠══════════════════════════════════════════════════════════════════╣
║ PERFORMANCE METRICS                    CONNECTIONS                ║
║ ─────────────────────────────────      ─────────────────────────  ║
║ CPU Usage:     ████████░░ 78%          Active:     245 / 500      ║
║ Memory:        ██████░░░░ 62%          Idle:       180            ║
║ Disk I/O:      █████░░░░░ 45%          Blocked:    3 ⚠️           ║
║ Buffer Hit:    █████████░ 94%          Waiting:    12             ║
╠══════════════════════════════════════════════════════════════════╣
║ TOP QUERIES BY DURATION (Last Hour)                               ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. SELECT * FROM Orders WHERE...        4.2s   ▲ 340% from avg   ║
║ 2. UPDATE Inventory SET...              2.8s   ▲ 120% from avg   ║
║ 3. INSERT INTO AuditLog...              1.1s   → Normal          ║
╠══════════════════════════════════════════════════════════════════╣
║ ALERTS                                                            ║
║ ─────────────────────────────────────────────────────────────── ║
║ ⚠️  High CPU usage on replica-02 (92%)           2 min ago        ║
║ ⚠️  Blocking chain detected (3 sessions)         5 min ago        ║
║ ✓  Backup completed successfully                 15 min ago       ║
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
                title: 'Real-Time Dashboards',
                description:
                  'Live performance metrics with customizable widgets. Track CPU, memory, I/O, and query performance at a glance.',
                icon: '📊',
              },
              {
                title: 'Query Performance',
                description:
                  'Identify slow queries, track execution plans, and monitor query patterns over time with historical analysis.',
                icon: '🔍',
              },
              {
                title: 'Connection Monitoring',
                description:
                  'Track active connections, detect blocking chains, and monitor connection pool utilization.',
                icon: '🔗',
              },
              {
                title: 'Alert System',
                description:
                  'Configurable alerts for CPU, memory, blocking, and custom thresholds. Integrates with Slack, Teams, and email.',
                icon: '🔔',
              },
              {
                title: 'Historical Trends',
                description:
                  'Store and analyze performance data over time. Identify patterns and predict capacity needs.',
                icon: '📈',
              },
              {
                title: 'Multi-Database Support',
                description:
                  'Monitor SQL Server and PostgreSQL from a single dashboard. Unified metrics across platforms.',
                icon: '🗄️',
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

      {/* Integrations */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 mb-6">Integrated with SQL2.AI Platform</h2>
            <p className="text-text-secondary mb-12">
              SQL Monitor provides the observability foundation for the entire SQL2.AI platform.
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
              {[
                { name: 'SQL Orchestrate', desc: 'Job monitoring' },
                { name: 'SQL Optimize', desc: 'Performance insights' },
                { name: 'SQL Audit', desc: 'Audit dashboards' },
                { name: 'SQL Agent', desc: 'AI observability' },
              ].map((integration) => (
                <div key={integration.name} className="card p-4 text-center">
                  <div className="text-sm font-medium text-text-primary">{integration.name}</div>
                  <div className="text-xs text-text-muted">{integration.desc}</div>
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
            <h2 className="text-h2 mb-6">Start Monitoring Today</h2>
            <p className="text-text-secondary mb-8">
              Get real-time visibility into your database performance with SQL Monitor.
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
