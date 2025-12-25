import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Convert - Cross-Platform Database Migration | SQL2.AI',
  description:
    'AI-powered database migration between SQL Server and PostgreSQL with automated code translation, Azure Functions generation, and intelligent dependency resolution.',
};

export default function ConvertPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#EC4899]/10 flex items-center justify-center text-[#EC4899]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Convert</h1>
                <p className="text-lg text-[#EC4899] font-medium">Cross-Platform Migration</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              AI-powered migration between SQL Server variants and PostgreSQL. Automated code translation,
              Azure Functions for Agent jobs, and intelligent dependency resolution.
            </p>
          </div>
        </div>
      </section>

      {/* Migration Paths */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Supported Migration Paths</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { from: 'SQL Server On-Prem', to: 'Azure SQL', icon: '🏢 → ☁️' },
              { from: 'SQL Server MI', to: 'Azure SQL', icon: '☁️ → ☁️' },
              { from: 'SQL Server', to: 'PostgreSQL', icon: '🔷 → 🐘' },
              { from: 'PostgreSQL', to: 'SQL Server', icon: '🐘 → 🔷' },
              { from: 'SQL Server On-Prem', to: 'SQL Server MI', icon: '🏢 → ☁️' },
              { from: 'Any', to: 'Any', icon: '🔄' },
            ].map((path, i) => (
              <div key={i} className="card p-6 text-center">
                <div className="text-3xl mb-3">{path.icon}</div>
                <div className="text-sm text-text-muted">{path.from}</div>
                <div className="text-[#EC4899] my-1">↓</div>
                <div className="text-text-primary font-medium">{path.to}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Translation */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Intelligent Code Translation</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">What Gets Translated</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>T-SQL to PL/pgSQL (and reverse)</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Data types with precision preservation</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Stored procedures and functions</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Triggers with event mapping</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Views and materialized views</span>
                </li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Azure Functions Generation</h3>
              <ul className="space-y-3 text-text-secondary">
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>SQL Agent jobs → Timer triggers</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Alerts → Event Grid triggers</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>xp_cmdshell → HTTP triggers</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>CLR assemblies → .NET Functions</span>
                </li>
                <li className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-[#EC4899] shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  <span>Linked servers → API intermediaries</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Agent-Based Migration */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">AI Agent Migration Pipeline</h2>
            <p className="text-text-secondary text-center mb-12">
              Plan, Execute, Test, Integrate - A complete migration lifecycle
            </p>

            <div className="grid md:grid-cols-4 gap-4">
              {[
                { step: '1', title: 'Plan', desc: 'Analyze source, map dependencies, generate migration plan' },
                { step: '2', title: 'Execute', desc: 'Run migrations with rollback checkpoints' },
                { step: '3', title: 'Test', desc: 'Automated validation of data integrity and functionality' },
                { step: '4', title: 'Integrate', desc: 'Update connection strings, deploy, verify' },
              ].map((phase) => (
                <div key={phase.step} className="card p-4 text-center">
                  <div className="w-10 h-10 rounded-full bg-[#EC4899] text-white flex items-center justify-center mx-auto mb-3 font-bold">
                    {phase.step}
                  </div>
                  <h3 className="text-h6 text-text-primary mb-2">{phase.title}</h3>
                  <p className="text-xs text-text-muted">{phase.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Cross-DB Query Handling */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Cross-Database Query Resolution</h2>
            <p className="text-text-secondary text-center mb-12">
              Automatically handles cross-database dependencies that break in cloud environments
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Original: Cross-database query (breaks in Azure SQL)
SELECT c.*, o.OrderTotal
FROM Sales.dbo.Customers c
JOIN Inventory.dbo.Orders o ON c.CustomerId = o.CustomerId

-- SQL Convert generates:
-- 1. Database intermediary API endpoint
-- 2. Synonyms pointing to intermediary
-- 3. Application-level join logic
-- 4. Or: Consolidated schema migration

┌─────────────────────────────────────────────────────┐
│  Option 1: API Intermediary                         │
│  Sales DB ←→ API Gateway ←→ Inventory DB           │
├─────────────────────────────────────────────────────┤
│  Option 2: Schema Consolidation                     │
│  All tables → Single Azure SQL Database             │
├─────────────────────────────────────────────────────┤
│  Option 3: Elastic Query (Azure)                    │
│  External tables with cross-database access         │
└─────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Migrate?"
        description="AI-powered database migration with automated code translation and Azure Functions generation."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
