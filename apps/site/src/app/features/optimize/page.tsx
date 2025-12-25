import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Optimize - AI-Powered Performance Analysis | SQL2.AI',
  description:
    'Deep performance analysis with Query Store integration, wait statistics, and AI-driven remediation suggestions.',
};

export default function OptimizePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-error/10 flex items-center justify-center text-error">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Optimize</h1>
                <p className="text-lg text-error font-medium">Performance Analysis</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Deep performance analysis that goes beyond simple query tuning. Analyze Query Store data,
              wait statistics, execution plans, and get AI-powered remediation suggestions.
            </p>
          </div>
        </div>
      </section>

      {/* Analysis Types */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Multi-Layer Analysis</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-error/10 flex items-center justify-center text-error mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Data Analysis</h3>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Table/index sizes</li>
                <li>Data distribution</li>
                <li>Fragmentation levels</li>
                <li>Growth projections</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-error/10 flex items-center justify-center text-error mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Code Analysis</h3>
              <ul className="space-y-2 text-small text-text-muted">
                <li>SP complexity scoring</li>
                <li>Cursor detection</li>
                <li>Parameter sniffing</li>
                <li>Plan regression</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-error/10 flex items-center justify-center text-error mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Query Store</h3>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Top resource consumers</li>
                <li>Regressed queries</li>
                <li>Plan choice analysis</li>
                <li>Wait correlation</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-error/10 flex items-center justify-center text-error mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Log Analysis</h3>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Error log patterns</li>
                <li>Deadlock graphs</li>
                <li>Blocking chains</li>
                <li>Extended Events</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Finding Example */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">AI-Powered Findings</h2>
            <p className="text-text-secondary text-center mb-12">
              Not just problems—prioritized solutions with impact estimates
            </p>

            <div className="card p-6 border-error/50">
              <div className="flex items-start gap-4 mb-6">
                <div className="w-10 h-10 rounded-lg bg-error/10 flex items-center justify-center text-error shrink-0">
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                    />
                  </svg>
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="px-2 py-1 text-xs font-medium bg-error/10 text-error rounded">CRITICAL</span>
                    <span className="text-small text-text-muted">Query Regression Detected</span>
                  </div>
                  <h3 className="text-h5 text-text-primary mb-2">GetCustomerOrders Performance Degradation</h3>
                  <p className="text-text-secondary mb-4">
                    Query execution time increased 340% since 2024-01-15. Root cause: parameter sniffing
                    after data skew in CustomerRegion column.
                  </p>
                </div>
              </div>

              <div className="bg-bg-surface rounded-lg p-4 mb-6">
                <h4 className="text-h6 text-text-primary mb-3">Impact Analysis</h4>
                <div className="grid md:grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-error">340%</p>
                    <p className="text-small text-text-muted">Slower than baseline</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-text-primary">2,400</p>
                    <p className="text-small text-text-muted">Daily executions</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-warning">47min</p>
                    <p className="text-small text-text-muted">CPU time/day wasted</p>
                  </div>
                </div>
              </div>

              <div className="space-y-3">
                <h4 className="text-h6 text-text-primary">Recommended Fixes</h4>

                <div className="flex items-center justify-between p-3 bg-bg-surface rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-success font-bold">1</span>
                    <div>
                      <p className="text-text-primary text-sm font-medium">Add OPTION (RECOMPILE)</p>
                      <p className="text-xs text-text-muted">Quick fix, minor CPU overhead</p>
                    </div>
                  </div>
                  <button className="px-3 py-1 text-sm bg-success/10 text-success rounded hover:bg-success/20">
                    Apply
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-bg-surface rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-info font-bold">2</span>
                    <div>
                      <p className="text-text-primary text-sm font-medium">Create filtered statistics</p>
                      <p className="text-xs text-text-muted">Better long-term solution</p>
                    </div>
                  </div>
                  <button className="px-3 py-1 text-sm bg-info/10 text-info rounded hover:bg-info/20">
                    Apply
                  </button>
                </div>

                <div className="flex items-center justify-between p-3 bg-bg-surface rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-secondary font-bold">3</span>
                    <div>
                      <p className="text-text-primary text-sm font-medium">Refactor with OPTIMIZE FOR</p>
                      <p className="text-xs text-text-muted">Best for this pattern</p>
                    </div>
                  </div>
                  <button className="px-3 py-1 text-sm bg-secondary/10 text-secondary rounded hover:bg-secondary/20">
                    Preview
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Wait Statistics */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Wait Statistics Intelligence</h2>
            <p className="text-text-secondary text-center mb-12">
              Understand what your queries are actually waiting for
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">Common Wait Types</h3>
                <ul className="space-y-3">
                  <li className="flex items-center justify-between">
                    <span className="text-text-secondary">PAGEIOLATCH_SH</span>
                    <span className="text-error font-medium">Disk I/O</span>
                  </li>
                  <li className="flex items-center justify-between">
                    <span className="text-text-secondary">LCK_M_X</span>
                    <span className="text-warning font-medium">Blocking</span>
                  </li>
                  <li className="flex items-center justify-between">
                    <span className="text-text-secondary">CXPACKET</span>
                    <span className="text-info font-medium">Parallelism</span>
                  </li>
                  <li className="flex items-center justify-between">
                    <span className="text-text-secondary">ASYNC_NETWORK_IO</span>
                    <span className="text-secondary font-medium">Client</span>
                  </li>
                </ul>
              </div>

              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">AI Interpretation</h3>
                <p className="text-text-secondary mb-4">
                  SQL Optimize doesn&apos;t just show wait types—it explains what they mean for your workload:
                </p>
                <blockquote className="border-l-4 border-error pl-4 text-text-secondary italic">
                  &quot;High PAGEIOLATCH waits indicate your working set exceeds buffer pool capacity.
                  Consider: increasing memory, optimizing queries to reduce data reads, or adding
                  covering indexes to reduce page lookups.&quot;
                </blockquote>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Proactive vs Reactive */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Proactive, Not Reactive</h2>
            <p className="text-text-secondary mb-12 max-w-2xl mx-auto">
              SQL Optimize identifies problems before they impact users, not after the phone starts ringing.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-error/10 flex items-center justify-center text-error mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Continuous Monitoring</h3>
                <p className="text-small text-text-muted">
                  24/7 analysis of Query Store, wait stats, and performance counters
                </p>
              </div>

              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-error/10 flex items-center justify-center text-error mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M13 10V3L4 14h7v7l9-11h-7z"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Early Warning</h3>
                <p className="text-small text-text-muted">
                  Detect regressions and anomalies before they become critical
                </p>
              </div>

              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-error/10 flex items-center justify-center text-error mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">One-Click Fixes</h3>
                <p className="text-small text-text-muted">
                  Apply recommended optimizations with confidence
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Optimize Your Database?"
        description="Stop fighting fires. Let SQL Optimize find and fix performance issues proactively."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
