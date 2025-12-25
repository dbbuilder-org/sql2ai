import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Comply - Automated Compliance Checking | SQL2.AI',
  description:
    'Automated SOC 2, HIPAA, PCI-DSS, GDPR, and FERPA compliance checking with PII detection and evidence collection.',
};

export default function ComplyPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-success/10 flex items-center justify-center text-success">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Comply</h1>
                <p className="text-lg text-success font-medium">Automated Compliance</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Continuous compliance monitoring for SOC 2, HIPAA, PCI-DSS, GDPR, and FERPA.
              Automated evidence collection, PII detection, and remediation tracking.
            </p>
          </div>
        </div>
      </section>

      {/* Compliance Frameworks */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Supported Frameworks</h2>

          <div className="flex flex-wrap justify-center gap-6 max-w-4xl mx-auto">
            {[
              { name: 'SOC 2', desc: 'Type I & II' },
              { name: 'HIPAA', desc: 'PHI Protection' },
              { name: 'PCI-DSS', desc: 'Cardholder Data' },
              { name: 'GDPR', desc: 'EU Data Protection' },
              { name: 'FERPA', desc: 'Educational Records' },
            ].map((framework) => (
              <div
                key={framework.name}
                className="px-8 py-6 rounded-xl border border-success/30 bg-success/5 flex flex-col items-center gap-2 min-w-[140px]"
              >
                <svg className="w-8 h-8 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
                <span className="font-bold text-text-primary">{framework.name}</span>
                <span className="text-xs text-text-muted">{framework.desc}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Check Categories */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Comprehensive Checks</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Server & Database Configuration</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Encryption at rest (TDE enabled)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Encryption in transit (TLS 1.2+)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Authentication settings (Windows/Mixed)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Audit configuration (C2/Common Criteria)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Backup encryption validation</span>
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Data-Level Analysis</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>PII/PHI detection in actual data</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>SSN, credit card, email detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>ML-based entity recognition</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Custom pattern definitions</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Powered by Microsoft Presidio</span>
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Access Control Review</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Complete permission inventory</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Excessive privilege detection</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Role membership analysis</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Cross-database access review</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Service account audit</span>
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Evidence & Reporting</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Automated evidence gathering</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Audit trail generation</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Compliance report export</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Remediation tracking</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-success shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Historical compliance trends</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* PII Detection */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Intelligent PII Detection</h2>
            <p className="text-text-secondary text-center mb-12">
              Powered by Microsoft Presidio for accurate, ML-based sensitive data discovery
            </p>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Sample Scan Output</h3>
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`Scanning table: dbo.Customers (sample: 1000 rows)

Findings:
┌─────────────────┬────────────────┬────────────┬──────────┐
│ Column          │ Entity Type    │ Confidence │ Count    │
├─────────────────┼────────────────┼────────────┼──────────┤
│ Email           │ EMAIL_ADDRESS  │ 99.2%      │ 1,000    │
│ Phone           │ PHONE_NUMBER   │ 98.7%      │ 892      │
│ Notes           │ US_SSN         │ 95.1%      │ 47       │
│ Notes           │ CREDIT_CARD    │ 94.8%      │ 12       │
│ Address         │ LOCATION       │ 91.3%      │ 1,000    │
└─────────────────┴────────────────┴────────────┴──────────┘

⚠ WARNING: PII found in unmasked 'Notes' column
  Recommendation: Implement column-level encryption or masking

⚠ CRITICAL: Credit card numbers detected in free-text field
  Recommendation: Immediate review - potential PCI-DSS violation`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Continuous Monitoring */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Continuous Compliance</h2>
            <p className="text-text-secondary mb-12 max-w-2xl mx-auto">
              Compliance isn&apos;t a one-time check. SQL Comply monitors continuously and alerts you
              when configurations drift out of compliance.
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-success/10 flex items-center justify-center text-success mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Scheduled Scans</h3>
                <p className="text-small text-text-muted">
                  Daily, weekly, or custom scan schedules
                </p>
              </div>

              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-success/10 flex items-center justify-center text-success mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Drift Alerts</h3>
                <p className="text-small text-text-muted">
                  Immediate notification on compliance changes
                </p>
              </div>

              <div className="card p-6">
                <div className="w-14 h-14 rounded-full bg-success/10 flex items-center justify-center text-success mx-auto mb-4">
                  <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Trend Reports</h3>
                <p className="text-small text-text-muted">
                  Track compliance posture over time
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Audit Ready */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Audit-Ready Evidence</h2>
            <p className="text-text-secondary text-center mb-12">
              When auditors come knocking, be ready with comprehensive evidence packages
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">Evidence Package Includes</h3>
                <ul className="space-y-3 text-text-secondary">
                  <li>Configuration snapshots with timestamps</li>
                  <li>Permission audit reports</li>
                  <li>Encryption validation certificates</li>
                  <li>Access control matrices</li>
                  <li>Change history with attribution</li>
                  <li>Remediation tracking logs</li>
                </ul>
              </div>

              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">Export Formats</h3>
                <ul className="space-y-3 text-text-secondary">
                  <li>PDF reports for auditors</li>
                  <li>Excel spreadsheets for analysis</li>
                  <li>JSON/XML for automation</li>
                  <li>Integration with GRC platforms</li>
                  <li>API for custom workflows</li>
                  <li>Scheduled email reports</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready for Your Next Audit?"
        description="Continuous compliance monitoring with automated evidence collection. Be audit-ready, always."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
