import { Metadata } from 'next';
import { ModuleCard, ModuleGrid, modules, CTASection } from '../../components/marketing';

export const metadata: Metadata = {
  title: 'Features - SQL2.AI Modules',
  description:
    'Explore the 8 SQL2.AI modules: Orchestrator, Migrator, Version, Code, Writer, SSMS Plugin, Optimize, and Comply. Complete database development lifecycle coverage.',
};

export default function FeaturesPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary text-small font-medium mb-6">
              8 Integrated Modules
            </span>
            <h1 className="text-h1 text-text-primary mb-6">
              The Complete Database
              <br />
              <span className="gradient-text">Development Platform</span>
            </h1>
            <p className="text-lg text-text-secondary mb-8 max-w-2xl mx-auto">
              SQL2.AI brings AI-powered sophistication to every stage of database development.
              From monitoring and migrations to compliance and code generation—all in one platform.
            </p>

            {/* Quick navigation */}
            <div className="flex flex-wrap justify-center gap-2">
              {modules.map((module) => (
                <a
                  key={module.id}
                  href={`#${module.id}`}
                  className="px-4 py-2 rounded-full bg-bg-surface border border-border text-small text-text-secondary hover:text-text-primary hover:border-border-emphasis transition-colors"
                >
                  {module.name.replace('SQL ', '')}
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Modules Grid */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <ModuleGrid>
            {modules.map((module) => (
              <div key={module.id} id={module.id}>
                <ModuleCard module={module} />
              </div>
            ))}
          </ModuleGrid>
        </div>
      </section>

      {/* Database-First Philosophy */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-h2 text-text-primary mb-4">Database-First Philosophy</h2>
              <p className="text-lg text-text-secondary">
                While other AI tools treat databases as an afterthought, SQL2.AI puts them first.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {/* Traditional */}
              <div className="card p-6 border-error/30">
                <h3 className="text-h5 text-error mb-4">Traditional Approach</h3>
                <div className="font-mono text-sm text-text-secondary space-y-2">
                  <p>Developer → AI Assistant</p>
                  <p className="pl-4">→ Application Code</p>
                  <p className="pl-8">→ ORM Models</p>
                  <p className="pl-12 text-error">→ Database (afterthought)</p>
                </div>
                <ul className="mt-4 space-y-2 text-small text-text-muted">
                  <li className="flex items-center gap-2">
                    <span className="text-error">✗</span> Inefficient schemas
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-error">✗</span> N+1 query problems
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-error">✗</span> No stored procedure support
                  </li>
                </ul>
              </div>

              {/* SQL2.AI */}
              <div className="card p-6 border-success/30">
                <h3 className="text-h5 text-success mb-4">SQL2.AI Approach</h3>
                <div className="font-mono text-sm text-text-secondary space-y-2">
                  <p className="text-success">Database (source of truth)</p>
                  <p className="pl-4">→ SQL2.AI Analysis</p>
                  <p className="pl-8">→ Generated Code</p>
                  <p className="pl-12">→ Optimized Application</p>
                </div>
                <ul className="mt-4 space-y-2 text-small text-text-muted">
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Schema is truth
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Set-based optimization
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-success">✓</span> Full SP/View/Function support
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Integration Points */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center mb-16">
            <h2 className="text-h2 text-text-primary mb-4">Works With Your Stack</h2>
            <p className="text-lg text-text-secondary">
              SQL2.AI integrates seamlessly with your existing tools and workflows.
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {/* Databases */}
            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-4">Databases</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-postgresql/10 flex items-center justify-center">
                    <span className="text-postgresql font-bold text-sm">PG</span>
                  </div>
                  <span className="text-xs text-text-muted">PostgreSQL</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-sqlserver/10 flex items-center justify-center">
                    <span className="text-sqlserver font-bold text-sm">MS</span>
                  </div>
                  <span className="text-xs text-text-muted">SQL Server</span>
                </div>
              </div>
            </div>

            {/* IDEs */}
            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-4">IDEs</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-sm">SSMS</span>
                  </div>
                  <span className="text-xs text-text-muted">SQL Server</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-sm">VS</span>
                  </div>
                  <span className="text-xs text-text-muted">VS Code</span>
                </div>
              </div>
            </div>

            {/* AI */}
            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-4">AI</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                    <span className="text-primary font-bold text-sm">C</span>
                  </div>
                  <span className="text-xs text-text-muted">Claude</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-sm">MCP</span>
                  </div>
                  <span className="text-xs text-text-muted">Protocol</span>
                </div>
              </div>
            </div>

            {/* CI/CD */}
            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-4">CI/CD</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-sm">GH</span>
                  </div>
                  <span className="text-xs text-text-muted">GitHub</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-10 h-10 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-sm">AZ</span>
                  </div>
                  <span className="text-xs text-text-muted">Azure</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance Badges */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Enterprise Compliance Ready</h2>
            <p className="text-lg text-text-secondary mb-12">
              SQL Comply helps you meet the most demanding regulatory requirements.
            </p>

            <div className="flex flex-wrap justify-center gap-4">
              {['SOC 2', 'HIPAA', 'PCI-DSS', 'GDPR', 'FERPA'].map((framework) => (
                <div
                  key={framework}
                  className="px-6 py-3 rounded-lg border border-border bg-bg-surface flex items-center gap-2"
                >
                  <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                    />
                  </svg>
                  <span className="font-medium text-text-primary">{framework}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Transform Your Database Workflow?"
        description="Start using SQL2.AI today. Free for individual developers, with powerful features for teams."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View Pricing', href: '/pricing' }}
      />
    </>
  );
}
