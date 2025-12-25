import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Receive - Secure Inbound Gateway | SQL2.AI',
  description:
    'Secure inbound gateway for files, APIs, and emails with malware scanning, data leak detection, and SQL injection prevention.',
};

export default function ReceivePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#EF4444]/10 flex items-center justify-center text-[#EF4444]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Receive</h1>
                <p className="text-lg text-[#EF4444] font-medium">Secure Inbound Gateway</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Secure inbound gateway for files, APIs, and emails. Malware scanning, data integrity checks,
              data leak prevention, and SQL injection detection before data enters your database.
            </p>
          </div>
        </div>
      </section>

      {/* Input Sources */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Supported Input Sources</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { name: 'File Uploads', icon: '📁', desc: 'CSV, Excel, JSON, XML' },
              { name: 'API Webhooks', icon: '🔗', desc: 'REST endpoints' },
              { name: 'Email Inbox', icon: '📥', desc: 'IMAP/POP3 polling' },
              { name: 'SFTP/FTP', icon: '🔒', desc: 'Secure file transfer' },
            ].map((source) => (
              <div key={source.name} className="card p-6 text-center">
                <div className="text-3xl mb-3">{source.icon}</div>
                <h3 className="text-h5 text-text-primary mb-1">{source.name}</h3>
                <p className="text-sm text-text-muted">{source.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security Pipeline */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Security Pipeline</h2>
            <p className="text-text-secondary text-center mb-12">
              Every inbound item passes through multiple security checks before reaching your database
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`INBOUND SECURITY PIPELINE
═══════════════════════════════════════════════════════════════

   Incoming Data
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  1. MALWARE SCAN                                          │
│  • ClamAV integration                                     │
│  • Virus signature detection                              │
│  • Macro/script detection in files                        │
│  • ✓ Pass / ✗ Quarantine                                 │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  2. DATA INTEGRITY CHECK                                  │
│  • File format validation                                 │
│  • Schema compliance                                      │
│  • Required field verification                            │
│  • Encoding detection (UTF-8, etc.)                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  3. DATA LEAK DETECTION                                   │
│  • Presidio PII scanning                                  │
│  • Secret/credential detection                            │
│  • Policy violation alerts                                │
│  • Redaction or rejection                                 │
└───────────────────────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────────────────────┐
│  4. SQL INJECTION PREVENTION                              │
│  • Pattern matching for SQL commands                      │
│  • Comment injection detection                            │
│  • Union/batch attack prevention                          │
│  • Parameterized insert preparation                       │
└───────────────────────────────────────────────────────────┘
        │
        ▼
   ✓ Safe to Insert`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Detection Examples */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Threat Detection Examples</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`SCAN RESULTS: customer_import.csv
════════════════════════════════════════════════════════════

✓ Malware Scan:     Clean (ClamAV 1.2.0)
✓ Format Valid:     CSV with 1,234 rows
⚠ Integrity Issues: 23 rows with missing email

SECURITY THREATS DETECTED:
┌─────────┬───────────────────────────────────────────────────┐
│ Row 47  │ SQL INJECTION ATTEMPT                             │
│         │ Value: "'; DROP TABLE Customers;--"               │
│         │ Action: Row rejected, logged, alert sent          │
├─────────┼───────────────────────────────────────────────────┤
│ Row 156 │ PII IN NOTES FIELD                                │
│         │ Found: SSN (confidence: 98%)                      │
│         │ Action: Redacted to "XXX-XX-XXXX"                 │
├─────────┼───────────────────────────────────────────────────┤
│ Row 892 │ POTENTIAL DATA LEAK                               │
│         │ Found: API key pattern in description             │
│         │ Action: Row quarantined for review                │
└─────────┴───────────────────────────────────────────────────┘

RESULT: 1,210 rows ready for import
        23 rows need review (missing data)
        1 row rejected (SQL injection)`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Configuration</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-receive.yaml
security:
  malware:
    enabled: true
    engine: clamav
    quarantine_path: /secure/quarantine/

  pii_detection:
    enabled: true
    action: redact  # or 'reject', 'flag'
    entities:
      - SSN
      - CREDIT_CARD
      - EMAIL_ADDRESS

  sql_injection:
    enabled: true
    action: reject
    log_attempts: true
    alert_on_detection: true

  integrity:
    validate_schema: true
    required_fields: [id, email, created_at]
    encoding: utf-8

sources:
  file_upload:
    endpoint: /api/receive/files
    max_size: 100MB
    allowed_types: [csv, xlsx, json]

  webhook:
    endpoint: /api/receive/webhook
    auth: hmac_signature
    secret: \${WEBHOOK_SECRET}

  email:
    imap_server: imap.company.com
    poll_interval: 5m
    allowed_senders: ["*@partner.com"]`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Security Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL RECEIVE SECURITY                           ║
╠══════════════════════════════════════════════════════════════════╣
║ LAST 24 HOURS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Items Processed:  4,721                                           ║
║ Clean:            4,683 (99.2%)                                   ║
║ Threats Blocked:  38                                              ║
╠══════════════════════════════════════════════════════════════════╣
║ THREAT BREAKDOWN                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ Malware:              2                                           ║
║ SQL Injection:        8                                           ║
║ PII Detected:         23 (redacted)                              ║
║ Data Leaks:           5 (quarantined)                            ║
╠══════════════════════════════════════════════════════════════════╣
║ BY SOURCE                                                         ║
║ ─────────────────────────────────────────────────────────────── ║
║ File Upload:      2,341 | 3 threats                              ║
║ API Webhook:      1,892 | 4 threats                              ║
║ Email Inbox:      488   | 31 threats                             ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Secure Your Inbound Data"
        description="Multi-layer security scanning for all data entering your database."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
