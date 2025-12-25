import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Simulate - Synthetic Data Generation | SQL2.AI',
  description:
    'Generate realistic synthetic data from schema metadata. No source data required - create test environments from scratch.',
};

export default function SimulatePage(): JSX.Element {
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Simulate</h1>
                <p className="text-lg text-[#10B981] font-medium">Synthetic Data Generation</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Generate realistic synthetic data from schema metadata alone. No source data required -
              create complete test environments from scratch with proper distributions and relationships.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">How It Works</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="card p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-[#10B981] text-white flex items-center justify-center mx-auto mb-4 font-bold">1</div>
              <h3 className="text-h5 text-text-primary mb-2">Analyze Schema</h3>
              <p className="text-sm text-text-muted">Read table structures, data types, constraints, and relationships</p>
            </div>
            <div className="card p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-[#10B981] text-white flex items-center justify-center mx-auto mb-4 font-bold">2</div>
              <h3 className="text-h5 text-text-primary mb-2">Infer Semantics</h3>
              <p className="text-sm text-text-muted">AI determines what each column represents (name, email, date, etc.)</p>
            </div>
            <div className="card p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-[#10B981] text-white flex items-center justify-center mx-auto mb-4 font-bold">3</div>
              <h3 className="text-h5 text-text-primary mb-2">Generate Data</h3>
              <p className="text-sm text-text-muted">Create realistic data respecting all constraints and relationships</p>
            </div>
          </div>
        </div>
      </section>

      {/* AI Inference */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Intelligent Column Detection</h2>
            <p className="text-text-secondary text-center mb-12">
              AI infers data types from column names and generates appropriate values
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`Column Analysis Results
════════════════════════════════════════════════════════════

Table: Customers
┌──────────────────┬─────────────┬──────────────────┬───────────────┐
│ Column           │ SQL Type    │ Inferred Type    │ Generator     │
├──────────────────┼─────────────┼──────────────────┼───────────────┤
│ CustomerId       │ INT         │ Primary Key      │ Sequential    │
│ FirstName        │ NVARCHAR    │ Person.FirstName │ Faker         │
│ LastName         │ NVARCHAR    │ Person.LastName  │ Faker         │
│ Email            │ NVARCHAR    │ Email Address    │ {first}.{last}│
│ PhoneNumber      │ VARCHAR     │ Phone (US)       │ ###-###-####  │
│ DateOfBirth      │ DATE        │ Birth Date       │ 18-80 years   │
│ CreatedAt        │ DATETIME    │ Timestamp        │ Recent dates  │
│ IsActive         │ BIT         │ Boolean          │ 90% true      │
│ CreditScore      │ INT         │ Score (300-850)  │ Normal dist   │
└──────────────────┴─────────────┴──────────────────┴───────────────┘

Confidence: 94% (override any detection in config)`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Configuration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Fine-Tune Generation</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-simulate.yaml
generation:
  seed: 42  # Reproducible results
  locale: en_US

tables:
  Customers:
    row_count: 10000
    columns:
      CreditScore:
        distribution: normal
        mean: 680
        std_dev: 80
        min: 300
        max: 850

      State:
        distribution: weighted
        values:
          CA: 0.15
          TX: 0.12
          FL: 0.10
          NY: 0.08
          other: 0.55

  Orders:
    row_count: 50000
    date_range:
      start: 2023-01-01
      end: 2024-12-31
    parent_distribution:
      table: Customers
      type: pareto  # Some customers order more

relationships:
  preserve_referential_integrity: true
  cascade_generation: true`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Use Cases</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Load Testing', desc: 'Generate millions of rows to stress test your database' },
              { title: 'New Projects', desc: 'Populate empty databases for development' },
              { title: 'Demo Environments', desc: 'Create realistic data for sales demos' },
              { title: 'CI/CD Testing', desc: 'Fresh test data for every pipeline run' },
            ].map((useCase) => (
              <div key={useCase.title} className="card p-6 text-center">
                <h3 className="text-h6 text-text-primary mb-2">{useCase.title}</h3>
                <p className="text-sm text-text-muted">{useCase.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* vs Anonymize */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Simulate vs Anonymize</h2>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6 border-[#10B981] border-2">
                <h3 className="text-h5 text-[#10B981] mb-4">SQL Simulate</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  <li>• No source data required</li>
                  <li>• Generates from schema metadata</li>
                  <li>• Perfect for new projects</li>
                  <li>• Configurable distributions</li>
                  <li>• Zero privacy risk</li>
                </ul>
              </div>

              <div className="card p-6 border-[#F59E0B] border-2">
                <h3 className="text-h5 text-[#F59E0B] mb-4">SQL Anonymize</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  <li>• Requires production data</li>
                  <li>• Preserves data patterns</li>
                  <li>• Maintains distributions</li>
                  <li>• Keeps edge cases</li>
                  <li>• Secure clean room process</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Generate Test Data Instantly"
        description="Create realistic synthetic data from schema alone. No production data needed."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
