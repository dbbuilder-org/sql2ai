import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Migrate - Database-First Migrations | SQL2.AI',
  description:
    'Generate code from your database, not the reverse. Auto-generate Dapper models, TypeScript types, and versioned migrations.',
};

export default function MigratePage(): JSX.Element {
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
                    d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Migrate</h1>
                <p className="text-lg text-success font-medium">Database-First Migrations</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Finally, migrations that work the right way. Your database schema is the source of truth.
              SQL Migrate generates Dapper models, TypeScript types, and rollback scripts automatically.
            </p>
          </div>
        </div>
      </section>

      {/* Problem/Solution */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Why Database-First?</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6 border-error/30">
              <h3 className="text-h5 text-error mb-4">Traditional Code-First</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-error mt-1">✗</span>
                  <span>ORM models define schema (abstraction leak)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-error mt-1">✗</span>
                  <span>No stored procedure support</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-error mt-1">✗</span>
                  <span>Manual Dapper model maintenance</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-error mt-1">✗</span>
                  <span>DACPAC is all-or-nothing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-error mt-1">✗</span>
                  <span>Flyway can&apos;t handle complex objects</span>
                </li>
              </ul>
            </div>

            <div className="card p-6 border-success/30">
              <h3 className="text-h5 text-success mb-4">SQL Migrate Database-First</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>Schema is the source of truth</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>Full SP, view, function support</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>Auto-generated Dapper models</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>Incremental versioned migrations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-success mt-1">✓</span>
                  <span>Dependency-aware deployment order</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Code Generation */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Automatic Code Generation</h2>
            <p className="text-text-secondary text-center mb-12">
              From one schema, generate code for multiple languages and frameworks.
            </p>

            <div className="grid md:grid-cols-2 gap-8">
              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">Dapper Models (C#)</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto">
                  <code className="text-text-secondary">{`// Auto-generated from dbo.Customers
public class Customer
{
    public int CustomerId { get; set; }
    public string Email { get; set; }
    public string Name { get; set; }
    public string? LoyaltyTier { get; set; }
}`}</code>
                </pre>
              </div>

              <div className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">TypeScript Types</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto">
                  <code className="text-text-secondary">{`// Auto-generated from dbo.Customers
export interface Customer {
  customerId: number;
  email: string;
  name: string;
  loyaltyTier: string | null;
}`}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-12 text-center">Simple Workflow</h2>

            <div className="grid md:grid-cols-4 gap-6 text-center">
              <div>
                <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center text-success font-bold text-xl mx-auto mb-4">
                  1
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Change Database</h3>
                <p className="text-small text-text-muted">Use SSMS, Azure Data Studio, or any SQL tool</p>
              </div>

              <div>
                <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center text-success font-bold text-xl mx-auto mb-4">
                  2
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Detect Changes</h3>
                <p className="text-small text-text-muted">sql2ai migrate diff</p>
              </div>

              <div>
                <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center text-success font-bold text-xl mx-auto mb-4">
                  3
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Generate Code</h3>
                <p className="text-small text-text-muted">Migration + Dapper + TypeScript</p>
              </div>

              <div>
                <div className="w-16 h-16 rounded-full bg-success/10 flex items-center justify-center text-success font-bold text-xl mx-auto mb-4">
                  4
                </div>
                <h3 className="text-h6 text-text-primary mb-2">Commit & Deploy</h3>
                <p className="text-small text-text-muted">CI/CD handles the rest</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready for Database-First Migrations?"
        description="Stop fighting your ORM. Let SQL Migrate generate code from your database."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
