import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Orchestrator - Unified Monitoring & Compliance | SQL2.AI',
  description:
    'Centralized monitoring, security auditing, and compliance checking with before/after context for change impact analysis.',
};

export default function OrchestratorPage(): JSX.Element {
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
                <h1 className="text-h1 text-text-primary">SQL Orchestrator</h1>
                <p className="text-lg text-primary font-medium">Unified Monitoring & Compliance</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              The central hub for all database monitoring, security auditing, and compliance checking.
              Track changes with before/after context and automate evidence collection.
            </p>
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Key Capabilities</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Multi-Trigger System</h3>
              <p className="text-text-secondary mb-4">
                Run checks on schedule, during deployments, or when anomalies are detected.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Scheduled (cron-based)</li>
                <li>Deployment hooks (CI/CD)</li>
                <li>Anomaly-triggered</li>
                <li>On-demand API</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Unified Check Framework</h3>
              <p className="text-text-secondary mb-4">
                Performance, security, and compliance checks in one extensible framework.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Query performance</li>
                <li>Permission auditing</li>
                <li>Encryption validation</li>
                <li>Compliance controls</li>
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
                <li>Migration scripts</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-12 text-center">How It Works</h2>

            <div className="space-y-8">
              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shrink-0">
                  1
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Configure Checks</h3>
                  <p className="text-text-secondary">
                    Enable the checks you need for your environment. Configure thresholds,
                    schedules, and notification channels.
                  </p>
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shrink-0">
                  2
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Deploy Agents</h3>
                  <p className="text-text-secondary">
                    Install lightweight agents on your database servers. They collect metrics
                    and execute checks with minimal overhead.
                  </p>
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shrink-0">
                  3
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Monitor & Alert</h3>
                  <p className="text-text-secondary">
                    View results in the dashboard, receive alerts on issues, and track
                    compliance status over time.
                  </p>
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary font-bold shrink-0">
                  4
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Remediate</h3>
                  <p className="text-text-secondary">
                    Get AI-powered remediation suggestions. Apply fixes with one click or
                    generate scripts for review.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Integrates With</h2>
            <p className="text-text-secondary mb-8">
              SQL Orchestrator works seamlessly with other SQL2.AI modules.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="card p-4 text-center">
                <h4 className="text-h6 text-text-primary">SQL Optimize</h4>
                <p className="text-small text-text-muted">Receive performance findings for remediation</p>
              </div>
              <div className="card p-4 text-center">
                <h4 className="text-h6 text-text-primary">SQL Comply</h4>
                <p className="text-small text-text-muted">Provide compliance evidence</p>
              </div>
              <div className="card p-4 text-center">
                <h4 className="text-h6 text-text-primary">SQL Version</h4>
                <p className="text-small text-text-muted">Trigger on deployments</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Unify Your Database Monitoring?"
        description="Get started with SQL Orchestrator today. Free for individual developers."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
