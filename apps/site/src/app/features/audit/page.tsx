import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Audit - Tamper-Proof Audit Logging | SQL2.AI',
  description:
    'Blockchain-level tamper-proofing for SQL Server audit logs. Presidio PII detection, AI severity scoring, and comprehensive telemetry.',
};

export default function AuditPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#F59E0B]/10 flex items-center justify-center text-[#F59E0B]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Audit</h1>
                <p className="text-lg text-[#F59E0B] font-medium">Tamper-Proof Logging</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Blockchain-level tamper-proofing for SQL Server audit logs. Integrated telemetry,
              Presidio PII protection, AI-powered severity scoring, and real-time dashboards.
            </p>
          </div>
        </div>
      </section>

      {/* Tamper-Proofing */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Blockchain-Style Integrity</h2>
            <p className="text-text-secondary text-center mb-12">
              Every audit record is cryptographically chained - any tampering is immediately detectable
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌──────────────────────────────────────────────────────────────┐
│  AUDIT RECORD #1                                              │
│  ─────────────────────────────────────────────────────────── │
│  Timestamp: 2024-01-21 14:30:00.123                          │
│  Event: SELECT on Customers                                   │
│  User: john.doe@company.com                                   │
│  Rows: 150                                                    │
│  Previous Hash: 0x0000...                                     │
│  Record Hash: 0x7f3a...                                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  AUDIT RECORD #2                                              │
│  ─────────────────────────────────────────────────────────── │
│  Timestamp: 2024-01-21 14:30:05.456                          │
│  Event: UPDATE on Orders                                      │
│  User: admin@company.com                                      │
│  Rows: 1                                                      │
│  Previous Hash: 0x7f3a...  ◄── Links to #1                   │
│  Record Hash: 0x2b8c...                                       │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
                         [...]

⚠️ If any record is modified, all subsequent hashes become invalid
✓ Verification: sql2ai audit verify --database ProductionDB`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Enterprise Features</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Tamper Detection', desc: 'Cryptographic chaining ensures any modification is immediately detected' },
              { title: 'PII Protection', desc: 'Presidio-powered scanning redacts sensitive data before logging' },
              { title: 'AI Severity Scoring', desc: 'ML models assess risk level of each audit event' },
              { title: 'Telemetry Integration', desc: 'Unified view with error logs and performance data' },
              { title: 'Real-Time Alerts', desc: 'Instant notification on high-severity events' },
              { title: 'Compliance Reports', desc: 'Pre-built reports for SOC 2, HIPAA, PCI-DSS' },
            ].map((feature) => (
              <div key={feature.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-2">{feature.title}</h3>
                <p className="text-sm text-text-muted">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Severity Scoring */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">AI-Powered Severity Scoring</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`AI SEVERITY ANALYSIS
════════════════════════════════════════════════════════════

Event: DELETE FROM Customers WHERE Status = 'Inactive'
User: contractor@external.com
Time: 2024-01-21 02:30:00 (outside business hours)

RISK FACTORS DETECTED:
┌─────────────────────────────────┬──────────┬───────────────┐
│ Factor                          │ Weight   │ Score         │
├─────────────────────────────────┼──────────┼───────────────┤
│ Destructive operation (DELETE)  │ High     │ +30           │
│ Bulk operation (847 rows)       │ High     │ +25           │
│ External contractor account     │ Medium   │ +15           │
│ Outside business hours          │ Medium   │ +15           │
│ Target: Customer PII table      │ High     │ +20           │
│ First time this operation       │ Low      │ +5            │
├─────────────────────────────────┼──────────┼───────────────┤
│ TOTAL SEVERITY SCORE            │          │ 110 / CRITICAL│
└─────────────────────────────────┴──────────┴───────────────┘

RECOMMENDED ACTIONS:
✗ Block operation (threshold: 80)
✗ Require manager approval
✓ Alert security team immediately
✓ Create incident ticket`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard Preview */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Unified Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL AUDIT DASHBOARD                            ║
╠══════════════════════════════════════════════════════════════════╣
║ LAST 24 HOURS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Events:     147,832                                         ║
║ Critical:         3 ⚠️                                            ║
║ High:             47                                              ║
║ Medium:           1,234                                           ║
║ Low:              146,548                                         ║
╠══════════════════════════════════════════════════════════════════╣
║ INTEGRITY STATUS                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ Chain Status:     ✓ VERIFIED                                     ║
║ Last Verified:    2024-01-21 14:30:00                            ║
║ Total Records:    2,847,293                                       ║
║ Tamper Attempts:  0                                               ║
╠══════════════════════════════════════════════════════════════════╣
║ PII EXPOSURE PREVENTION                                           ║
║ ─────────────────────────────────────────────────────────────── ║
║ Queries Scanned:  147,832                                         ║
║ PII Detected:     2,341 (1.6%)                                   ║
║ Auto-Redacted:    2,341 ✓                                        ║
║ Types: SSN (847), Email (1,204), Phone (290)                     ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Integration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Integrated with SQL Monitor</h2>
            <p className="text-text-secondary mb-12">
              Audit data flows directly into your monitoring dashboard for unified visibility
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              {['Error Logs', 'Performance Data', 'Query Stats', 'Security Events', 'Compliance Status'].map((item) => (
                <div key={item} className="px-4 py-2 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B] text-sm font-medium">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Secure Your Audit Trail"
        description="Tamper-proof logging with AI severity scoring and real-time monitoring."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
