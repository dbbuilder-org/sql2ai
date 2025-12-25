import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Standardize - Database Standards Enforcement | SQL2.AI',
  description:
    'Enforce naming conventions, coding standards, normalization rules, and best practices across your SQL Server and PostgreSQL databases.',
};

export default function StandardizePage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#8B5CF6]/10 flex items-center justify-center text-[#8B5CF6]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Standardize</h1>
                <p className="text-lg text-[#8B5CF6] font-medium">Standards Enforcement</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Enforce naming conventions, coding standards, normalization rules, and best practices
              across all your SQL Server and PostgreSQL database objects.
            </p>
          </div>
        </div>
      </section>

      {/* Standards Categories */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">What Gets Standardized</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Naming Conventions', items: ['Table prefixes/suffixes', 'Column naming patterns', 'Index naming', 'Constraint naming'] },
              { title: 'Coding Standards', items: ['Consistent formatting', 'Comment requirements', 'Error handling patterns', 'Transaction patterns'] },
              { title: 'Object Selection', items: ['View vs Table decisions', 'Function vs SP guidance', 'Table types vs Variables', 'Trigger appropriateness'] },
              { title: 'Data Types', items: ['Appropriate type selection', 'Size optimization', 'Nullable consistency', 'Default value patterns'] },
              { title: 'Normalization', items: ['1NF through BCNF checks', 'Denormalization justification', 'Redundancy detection', 'Dependency analysis'] },
              { title: 'Security', items: ['Permission patterns', 'Schema separation', 'Dynamic SQL safety', 'Injection prevention'] },
            ].map((category) => (
              <div key={category.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">{category.title}</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  {category.items.map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-[#8B5CF6] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Rule Configuration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Configurable Rules</h2>
            <p className="text-text-secondary text-center mb-12">
              Define your organization&apos;s standards in a simple YAML configuration
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# sql2ai-standards.yaml
naming:
  tables:
    pattern: "^[A-Z][a-zA-Z]+$"  # PascalCase
    prefix: null
    suffix: null

  columns:
    pattern: "^[A-Z][a-zA-Z]+$"
    primary_key: "{Table}Id"
    foreign_key: "{ReferencedTable}Id"

  indexes:
    pattern: "IX_{Table}_{Columns}"
    unique: "UX_{Table}_{Columns}"

  stored_procedures:
    pattern: "^(Get|Set|Insert|Update|Delete|Process)[A-Z]"

coding:
  require_try_catch: true
  require_transaction: "for_modifications"
  max_procedure_length: 500
  require_comments: "public_objects"

normalization:
  minimum_form: "3NF"
  allow_denormalization: "with_justification"`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Scan Results */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Sample Scan Results</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`SQL Standardize Scan Results
════════════════════════════════════════════════════════════

Database: ProductionDB
Scanned: 156 tables, 89 procedures, 45 views, 23 functions

NAMING VIOLATIONS (47 found)
────────────────────────────────────────────────────────────
⚠ Table 'tbl_customers' → Should be 'Customers' (no prefix)
⚠ Column 'cust_id' → Should be 'CustomerId' (PascalCase)
⚠ Index 'idx1' → Should be 'IX_Customers_Email' (descriptive)
⚠ Procedure 'sp_GetData' → Should be 'GetCustomerData' (no sp_)

CODING VIOLATIONS (23 found)
────────────────────────────────────────────────────────────
✗ Procedure 'UpdateInventory' missing TRY/CATCH
✗ Procedure 'ProcessOrders' has 847 lines (max: 500)
✗ Function 'fn_Calculate' uses dynamic SQL (security risk)

NORMALIZATION ISSUES (8 found)
────────────────────────────────────────────────────────────
⚠ Table 'Orders' has repeating group in columns 'Item1-Item10'
⚠ Table 'Customers' has transitive dependency: City → State

[Generate Fix Script] [Export Report] [Configure Rules]`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CI/CD Integration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">CI/CD Integration</h2>
            <p className="text-text-secondary mb-12">
              Block deployments that violate standards before they reach production
            </p>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="card p-6">
                <div className="text-3xl mb-4">🔄</div>
                <h3 className="text-h6 text-text-primary mb-2">Pre-Commit Hooks</h3>
                <p className="text-sm text-text-muted">Check standards before code is committed</p>
              </div>
              <div className="card p-6">
                <div className="text-3xl mb-4">🚀</div>
                <h3 className="text-h6 text-text-primary mb-2">Pipeline Gates</h3>
                <p className="text-sm text-text-muted">Fail builds that violate standards</p>
              </div>
              <div className="card p-6">
                <div className="text-3xl mb-4">📊</div>
                <h3 className="text-h6 text-text-primary mb-2">PR Comments</h3>
                <p className="text-sm text-text-muted">Automated review comments on violations</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Enforce Your Standards"
        description="Consistent naming, coding conventions, and best practices across all your databases."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
