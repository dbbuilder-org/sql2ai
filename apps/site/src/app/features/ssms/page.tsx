import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SSMS Plugin - AI Inside SQL Server Management Studio | SQL2.AI',
  description:
    'Bring AI capabilities directly into SSMS. Inline suggestions, query optimization, and code generation without leaving your IDE.',
};

export default function SSMSPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-sqlserver/10 flex items-center justify-center text-sqlserver">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SSMS Plugin</h1>
                <p className="text-lg text-sqlserver font-medium">AI in Your IDE</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Stop context-switching between SSMS and AI tools. Get inline suggestions,
              query optimization, and code generation right where you work.
            </p>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Plugin Features</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">AI Query Assist</h3>
              <p className="text-text-secondary">
                Intelligent code completions as you type. Context-aware suggestions based on your schema.
              </p>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Explain Query</h3>
              <p className="text-text-secondary">
                Right-click any query to get a plain-English explanation of what it does and how.
              </p>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Optimize Query</h3>
              <p className="text-text-secondary">
                Get optimization suggestions with one click. See before/after performance estimates.
              </p>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Generate CRUD</h3>
              <p className="text-text-secondary">
                Right-click a table to generate complete Create, Read, Update, Delete procedures.
              </p>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Review Code</h3>
              <p className="text-text-secondary">
                Highlight any code and get instant review for security, performance, and best practices.
              </p>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-sqlserver/10 flex items-center justify-center text-sqlserver mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Plan Analysis</h3>
              <p className="text-text-secondary">
                AI-powered execution plan analysis. Understand why your query is slow.
              </p>
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
                <div className="w-12 h-12 rounded-full bg-sqlserver/10 flex items-center justify-center text-sqlserver font-bold shrink-0">
                  1
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Install the Plugin</h3>
                  <p className="text-text-secondary">
                    Download and install the SQL2.AI extension for SSMS 18 or 19. Takes less than
                    a minute with our installer.
                  </p>
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-sqlserver/10 flex items-center justify-center text-sqlserver font-bold shrink-0">
                  2
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Connect Your Account</h3>
                  <p className="text-text-secondary">
                    Sign in with your SQL2.AI account to enable AI features. Your queries never leave
                    your network—only metadata is sent for analysis.
                  </p>
                </div>
              </div>

              <div className="flex gap-6">
                <div className="w-12 h-12 rounded-full bg-sqlserver/10 flex items-center justify-center text-sqlserver font-bold shrink-0">
                  3
                </div>
                <div>
                  <h3 className="text-h5 text-text-primary mb-2">Start Using AI</h3>
                  <p className="text-text-secondary">
                    Access AI features through the toolbar, context menu, or keyboard shortcuts.
                    Works with any SQL Server database you can connect to.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Context Menu Preview */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Right-Click Intelligence</h2>
            <p className="text-text-secondary text-center mb-12">
              All AI features are just a right-click away
            </p>

            <div className="card p-8">
              <div className="bg-bg-primary rounded-lg p-4 mb-6">
                <code className="text-text-secondary text-sm">
                  SELECT * FROM Customers WHERE Status = &apos;Active&apos;
                </code>
              </div>

              <div className="bg-bg-surface border border-border rounded-lg p-2 max-w-xs">
                <div className="space-y-1">
                  <div className="px-3 py-2 hover:bg-bg-primary rounded flex items-center gap-2">
                    <svg className="w-4 h-4 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span className="text-text-primary text-sm">Optimize Query</span>
                  </div>
                  <div className="px-3 py-2 hover:bg-bg-primary rounded flex items-center gap-2">
                    <svg className="w-4 h-4 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-text-primary text-sm">Explain Query</span>
                  </div>
                  <div className="px-3 py-2 hover:bg-bg-primary rounded flex items-center gap-2">
                    <svg className="w-4 h-4 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    <span className="text-text-primary text-sm">Review for Issues</span>
                  </div>
                  <div className="px-3 py-2 hover:bg-bg-primary rounded flex items-center gap-2">
                    <svg className="w-4 h-4 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                    <span className="text-text-primary text-sm">Rewrite Query</span>
                  </div>
                  <div className="border-t border-border my-1"></div>
                  <div className="px-3 py-2 hover:bg-bg-primary rounded flex items-center gap-2">
                    <svg className="w-4 h-4 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    <span className="text-text-primary text-sm">Analyze Execution Plan</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Air-Gapped Support */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Air-Gapped Environment Support</h2>
            <p className="text-text-secondary mb-8 max-w-2xl mx-auto">
              For secure environments that can&apos;t connect to external services, we offer a local
              LLM option that runs entirely within your network.
            </p>

            <div className="grid md:grid-cols-2 gap-6 max-w-2xl mx-auto">
              <div className="card p-6 text-left">
                <h3 className="text-h6 text-text-primary mb-3">Cloud Mode</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Full AI capabilities
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Always up-to-date models
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> No local GPU required
                  </li>
                </ul>
              </div>

              <div className="card p-6 text-left">
                <h3 className="text-h6 text-text-primary mb-3">Local Mode</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> 100% air-gapped
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Data never leaves network
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Local LLM deployment
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Supercharge SSMS?"
        description="Install the SQL2.AI plugin and bring AI directly into your SQL Server workflow."
        primaryCTA={{ text: 'Download Plugin', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
