import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Code - Automated Review & Data Dictionary | SQL2.AI',
  description:
    'Automated code review, release notes generation, and AI-driven data dictionary. Swagger for your database.',
};

export default function CodePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-info/10 flex items-center justify-center text-info">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Code</h1>
                <p className="text-lg text-info font-medium">Review & Data Dictionary</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Automated code review, intelligent release notes, and AI-powered data documentation.
              Think of it as Swagger for your database—auto-generated, always current.
            </p>
          </div>
        </div>
      </section>

      {/* Three Pillars */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Three Pillars</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-info/10 flex items-center justify-center text-info mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Code Review</h3>
              <p className="text-text-secondary mb-4">
                Automated review of SQL code changes with style, security, and performance checks.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Style/convention enforcement</li>
                <li>Security vulnerability scanning</li>
                <li>Performance anti-patterns</li>
                <li>Best practice enforcement</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-info/10 flex items-center justify-center text-info mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Release Notes</h3>
              <p className="text-text-secondary mb-4">
                Auto-generate release notes from migrations with categorized changes.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>Breaking change detection</li>
                <li>Feature categorization</li>
                <li>Markdown/HTML output</li>
                <li>GitHub release integration</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="w-12 h-12 rounded-xl bg-info/10 flex items-center justify-center text-info mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                  />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-3">Data Dictionary</h3>
              <p className="text-text-secondary mb-4">
                AI-powered documentation that stays current. Swagger for your database.
              </p>
              <ul className="space-y-2 text-small text-text-muted">
                <li>AI-inferred descriptions</li>
                <li>Relationship mapping</li>
                <li>OpenAPI-compatible export</li>
                <li>Interactive portal</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Data Dictionary Deep Dive */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Swagger for Your Database</h2>
            <p className="text-text-secondary text-center mb-12">
              Auto-generated, always-current documentation for every table, column, and relationship.
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">Auto-Generated YAML</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto">
                  <code className="text-text-secondary">{`# Auto-generated data dictionary
tables:
  Customers:
    description: "Core customer records"
    columns:
      CustomerId:
        type: int
        description: "Primary identifier"
        pii: false
      Email:
        type: nvarchar(255)
        description: "Customer email"
        pii: true
        gdpr_category: "contact_info"`}</code>
                </pre>
              </div>

              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">AI-Inferred Context</h3>
                <ul className="space-y-4">
                  <li className="flex items-start gap-3">
                    <span className="text-info text-lg">1</span>
                    <div>
                      <p className="text-text-primary font-medium">Semantic Understanding</p>
                      <p className="text-small text-text-muted">
                        AI analyzes column names, types, and sample data to infer purpose
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-info text-lg">2</span>
                    <div>
                      <p className="text-text-primary font-medium">PII Detection</p>
                      <p className="text-small text-text-muted">
                        Automatically flags sensitive data for GDPR/HIPAA compliance
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-info text-lg">3</span>
                    <div>
                      <p className="text-text-primary font-medium">Relationship Discovery</p>
                      <p className="text-small text-text-muted">
                        Maps foreign keys and implicit relationships
                      </p>
                    </div>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-info text-lg">4</span>
                    <div>
                      <p className="text-text-primary font-medium">Usage Patterns</p>
                      <p className="text-small text-text-muted">
                        Documents how data flows through stored procedures
                      </p>
                    </div>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Code Review Features */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-12 text-center">Intelligent Code Review</h2>

            <div className="space-y-6">
              <div className="card p-6">
                <div className="flex items-start gap-4">
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
                    <h3 className="text-h6 text-text-primary mb-2">Security Issues</h3>
                    <p className="text-text-secondary mb-2">
                      Detects SQL injection vulnerabilities, dynamic SQL risks, and permission issues.
                    </p>
                    <code className="text-small text-error">
                      WARNING: Dynamic SQL without parameterization on line 45
                    </code>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-warning/10 flex items-center justify-center text-warning shrink-0">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 10V3L4 14h7v7l9-11h-7z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-h6 text-text-primary mb-2">Performance Warnings</h3>
                    <p className="text-text-secondary mb-2">
                      Identifies cursors, implicit conversions, and missing indexes.
                    </p>
                    <code className="text-small text-warning">
                      PERF: Cursor detected - consider set-based alternative
                    </code>
                  </div>
                </div>
              </div>

              <div className="card p-6">
                <div className="flex items-start gap-4">
                  <div className="w-10 h-10 rounded-lg bg-info/10 flex items-center justify-center text-info shrink-0">
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-h6 text-text-primary mb-2">Style Suggestions</h3>
                    <p className="text-text-secondary mb-2">
                      Enforces naming conventions, formatting standards, and best practices.
                    </p>
                    <code className="text-small text-info">
                      STYLE: Use schema prefix for table references (dbo.Customers)
                    </code>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Document Your Database?"
        description="Auto-generated documentation that stays current. Code review that catches issues before production."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
