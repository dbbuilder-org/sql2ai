import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Anonymize - Secure Data Clean Room | SQL2.AI',
  description:
    'Create anonymized copies of production data for development and testing. K-anonymity, data masking, and referential integrity preservation.',
};

export default function AnonymizePage(): JSX.Element {
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Anonymize</h1>
                <p className="text-lg text-[#F59E0B] font-medium">Secure Clean Room</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Create secure, anonymized copies of production data for development and testing.
              Realistic data that bears no resemblance to the source while preserving referential integrity.
            </p>
          </div>
        </div>
      </section>

      {/* Clean Room Concept */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">The Clean Room Approach</h2>
            <p className="text-text-secondary text-center mb-12">
              Data flows one way into the clean room. No production data escapes.
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   PRODUCTION    │     │    CLEAN ROOM    │     │   DEV/TEST      │
│   DATABASE      │ ──► │   PROCESSING     │ ──► │   DATABASE      │
│                 │     │                  │     │                 │
│ • Real names    │     │ • K-anonymity    │     │ • Fake names    │
│ • Real SSNs     │     │ • Data masking   │     │ • Fake SSNs     │
│ • Real emails   │     │ • FK preservation│     │ • Fake emails   │
│ • Real addresses│     │ • Distribution   │     │ • Fake addresses│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               ▲
                               │
                        No data flows back
                        (Audit enforced)`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Anonymization Techniques */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Anonymization Techniques</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'K-Anonymity', desc: 'Ensure each record is indistinguishable from at least k-1 others' },
              { title: 'Data Masking', desc: 'Replace sensitive values with realistic but fake data' },
              { title: 'Tokenization', desc: 'Replace values with tokens that preserve format' },
              { title: 'Generalization', desc: 'Replace specific values with ranges or categories' },
              { title: 'Perturbation', desc: 'Add noise to numeric values while preserving distributions' },
              { title: 'Shuffling', desc: 'Randomize column values while maintaining statistics' },
            ].map((technique) => (
              <div key={technique.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-2">{technique.title}</h3>
                <p className="text-sm text-text-muted">{technique.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Column-Level Configuration</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-anonymize.yaml
tables:
  Customers:
    columns:
      FirstName:
        method: faker
        type: first_name
        locale: en_US

      LastName:
        method: faker
        type: last_name

      Email:
        method: mask
        pattern: "****@{domain}"
        preserve_domain: true

      SSN:
        method: tokenize
        format: "###-##-####"

      DateOfBirth:
        method: perturb
        range: 365  # +/- 1 year

      Salary:
        method: generalize
        buckets: [50000, 75000, 100000, 150000]

  Orders:
    preserve_referential_integrity: true
    sample_percentage: 10  # Only copy 10% of orders`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Before/After */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-12 text-center">Before & After</h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4 text-center">Production Data</h3>
                <div className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                  <table className="w-full text-text-secondary">
                    <thead>
                      <tr className="border-b border-border-primary">
                        <th className="text-left py-2">Name</th>
                        <th className="text-left py-2">Email</th>
                        <th className="text-left py-2">SSN</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td className="py-1">John Smith</td><td>john@acme.com</td><td>123-45-6789</td></tr>
                      <tr><td className="py-1">Jane Doe</td><td>jane@corp.com</td><td>987-65-4321</td></tr>
                      <tr><td className="py-1">Bob Wilson</td><td>bob@tech.io</td><td>456-78-9012</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4 text-center">Anonymized Data</h3>
                <div className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                  <table className="w-full text-text-secondary">
                    <thead>
                      <tr className="border-b border-border-primary">
                        <th className="text-left py-2">Name</th>
                        <th className="text-left py-2">Email</th>
                        <th className="text-left py-2">SSN</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr><td className="py-1">Michael Brown</td><td>****@acme.com</td><td>XXX-XX-7834</td></tr>
                      <tr><td className="py-1">Sarah Johnson</td><td>****@corp.com</td><td>XXX-XX-2156</td></tr>
                      <tr><td className="py-1">David Miller</td><td>****@tech.io</td><td>XXX-XX-4589</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Compliance Ready</h2>
            <p className="text-text-secondary mb-12">
              Meet data privacy requirements while enabling development
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              {['GDPR', 'HIPAA', 'PCI-DSS', 'CCPA', 'SOC 2'].map((badge) => (
                <div key={badge} className="px-6 py-3 rounded-lg bg-[#F59E0B]/10 text-[#F59E0B] font-medium">
                  {badge}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Protect Your Production Data"
        description="Create realistic dev/test environments without exposing sensitive information."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
