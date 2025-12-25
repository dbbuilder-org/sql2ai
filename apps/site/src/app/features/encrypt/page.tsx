import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Encrypt - Automated Encryption Management | SQL2.AI',
  description:
    'Automated key rotation, vault integration, TDE, and Always Encrypted management. Zero human interaction required for maintenance.',
};

export default function EncryptPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#10B981]/10 flex items-center justify-center text-[#10B981]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Encrypt</h1>
                <p className="text-lg text-[#10B981] font-medium">Encryption Management</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Automated enforcement, management, and verification of encryption at rest.
              Key rotation, vault integration, TDE, and Always Encrypted with zero human interaction.
            </p>
          </div>
        </div>
      </section>

      {/* Key Vault Integration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Key Vault Integration</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="card p-6 text-center">
              <div className="text-3xl mb-4">☁️</div>
              <h3 className="text-h5 text-text-primary mb-2">Azure Key Vault</h3>
              <p className="text-sm text-text-muted">Native integration with Azure managed keys</p>
            </div>
            <div className="card p-6 text-center">
              <div className="text-3xl mb-4">🔐</div>
              <h3 className="text-h5 text-text-primary mb-2">AWS KMS</h3>
              <p className="text-sm text-text-muted">Full AWS Key Management Service support</p>
            </div>
            <div className="card p-6 text-center">
              <div className="text-3xl mb-4">🗝️</div>
              <h3 className="text-h5 text-text-primary mb-2">HashiCorp Vault</h3>
              <p className="text-sm text-text-muted">Enterprise secrets management</p>
            </div>
          </div>
        </div>
      </section>

      {/* Encryption Types */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Managed Encryption Types</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">TDE (Transparent Data Encryption)</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Full database encryption at rest
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Automatic key rotation scheduling
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Zero-downtime key changes
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Backup encryption verification
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Always Encrypted (Column-Level)</h3>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Per-column encryption control
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Deterministic & randomized options
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Column Master Key management
                </li>
                <li className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#10B981]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  PII column recommendations
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Key Rotation */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Automatic Key Rotation</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    KEY ROTATION IN PROGRESS                       ║
╠══════════════════════════════════════════════════════════════════╣
║ Rotation Type: TDE Protector Key                                  ║
║ Database: ProductionDB                                            ║
║ Started: 2024-01-21 02:00:00                                      ║
╠══════════════════════════════════════════════════════════════════╣
║ PROGRESS                                                          ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ Step 1/5: Create new key in Azure Key Vault                    ║
║ ✓ Step 2/5: Set new TDE protector                                 ║
║ ► Step 3/5: Re-encrypt database encryption key                    ║
║   [████████████████░░░░░░░░░░░░░] 62%                             ║
║ ○ Step 4/5: Verify encryption                                     ║
║ ○ Step 5/5: Archive old key                                       ║
╠══════════════════════════════════════════════════════════════════╣
║ Estimated completion: 02:45:00                                    ║
║ Zero downtime: ✓ Database remains online                          ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance Dashboard */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Encryption Status Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    TDE ENCRYPTION STATUS                          ║
╠══════════════════════════════════════════════════════════════════╣
║ DATABASE            │ STATUS      │ KEY SOURCE  │ ROTATION DUE   ║
║ ───────────────────┼─────────────┼─────────────┼─────────────── ║
║ ProductionDB        │ ✓ Encrypted │ Azure KV    │ 2024-04-15     ║
║ StagingDB           │ ✓ Encrypted │ Azure KV    │ 2024-04-15     ║
║ DevelopmentDB       │ ⚠ Not Set   │ -           │ -              ║
║ ArchiveDB           │ ✓ Encrypted │ Azure KV    │ 2024-05-01     ║
╠══════════════════════════════════════════════════════════════════╣
║ COLUMN ENCRYPTION STATUS                                          ║
║ ──────────────────┼──────────────────┼──────────────┼────────── ║
║ Customers          │ SSN              │ Deterministic│ ✓ Active  ║
║ Customers          │ CreditCardNumber │ Randomized   │ ✓ Active  ║
║ Employees          │ Salary           │ Randomized   │ ✓ Active  ║
║ Patients           │ MedicalRecord    │ -            │ ⚠ Not Set ║
╠══════════════════════════════════════════════════════════════════╣
║ RECOMMENDATIONS                                                   ║
║ ⚠ DevelopmentDB not encrypted - Enable TDE?                      ║
║ ⚠ Patients.MedicalRecord contains PHI - Enable encryption?       ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Simple Configuration</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-encrypt.yaml
key_vault:
  provider: azure
  config:
    vault_url: https://mycompany-keys.vault.azure.net/

rotation:
  schedule:
    tde_keys:
      interval: 90d
      window: "Sunday 02:00-06:00"
      notification: 7d_before

    column_master_keys:
      interval: 365d
      notification: 30d_before

always_encrypted:
  columns:
    - table: Customers
      column: SSN
      encryption_type: deterministic

    - table: Customers
      column: CreditCardNumber
      encryption_type: randomized`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Automate Your Encryption"
        description="Key rotation, vault integration, and compliance verification with zero manual intervention."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
