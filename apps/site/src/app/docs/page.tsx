import { Metadata } from 'next';
import Link from 'next/link';
import { TerminalBlock } from '../../components/ui';

export const metadata: Metadata = {
  title: 'Documentation',
  description:
    'Learn how to use SQL2.AI for database development. Installation guides, API reference, and tutorials for SQL Server and PostgreSQL.',
};

interface DocCategory {
  title: string;
  description: string;
  icon: React.ReactNode;
  links: { title: string; href: string }[];
}

const categories: DocCategory[] = [
  {
    title: 'Getting Started',
    description: 'Installation, configuration, and your first analysis.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    links: [
      { title: 'Quick Start Guide', href: '/docs/quickstart' },
      { title: 'Installation', href: '/docs/installation' },
      { title: 'Configuration', href: '/docs/configuration' },
      { title: 'Your First Analysis', href: '/docs/first-analysis' },
    ],
  },
  {
    title: 'CLI Reference',
    description: 'Complete command-line interface documentation.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    links: [
      { title: 'CLI Overview', href: '/docs/cli' },
      { title: 'analyze command', href: '/docs/cli/analyze' },
      { title: 'optimize command', href: '/docs/cli/optimize' },
      { title: 'All Commands', href: '/docs/cli/commands' },
    ],
  },
  {
    title: 'MCP Integration',
    description: 'Using SQL2.AI with Claude and other AI assistants.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
      </svg>
    ),
    links: [
      { title: 'MCP Overview', href: '/docs/mcp' },
      { title: 'Setup with Claude', href: '/docs/mcp/claude-setup' },
      { title: 'Available Tools', href: '/docs/mcp/tools' },
      { title: 'Best Practices', href: '/docs/mcp/best-practices' },
    ],
  },
  {
    title: 'SDK & API',
    description: 'Programmatic access for custom integrations.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
      </svg>
    ),
    links: [
      { title: 'SDK Overview', href: '/docs/sdk' },
      { title: 'TypeScript SDK', href: '/docs/sdk/typescript' },
      { title: 'REST API Reference', href: '/docs/api' },
      { title: 'Webhooks', href: '/docs/api/webhooks' },
    ],
  },
  {
    title: 'Features',
    description: 'Deep dives into each SQL2.AI capability.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
      </svg>
    ),
    links: [
      { title: 'Schema Analysis', href: '/docs/features/analyze' },
      { title: 'Query Optimization', href: '/docs/features/optimize' },
      { title: 'Migration Generation', href: '/docs/features/migrations' },
      { title: 'All Features', href: '/docs/features' },
    ],
  },
  {
    title: 'Tutorials',
    description: 'Step-by-step guides for common workflows.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
      </svg>
    ),
    links: [
      { title: 'Migrating from SQL Server to PostgreSQL', href: '/docs/tutorials/migration' },
      { title: 'CI/CD Pipeline Setup', href: '/docs/tutorials/ci-cd' },
      { title: 'Optimizing Slow Queries', href: '/docs/tutorials/slow-queries' },
      { title: 'All Tutorials', href: '/docs/tutorials' },
    ],
  },
];

export default function DocsPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20 bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h1 className="text-h1 text-text-primary mb-6">Documentation</h1>
            <p className="text-lg text-text-secondary">
              Everything you need to master SQL2.AI for database development.
            </p>
          </div>

          {/* Search (placeholder) */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <svg
                className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                placeholder="Search documentation..."
                className="w-full pl-12 pr-4 py-4 rounded-xl bg-bg-base border border-border text-text-primary placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-1">
                <kbd className="px-2 py-1 rounded bg-bg-surface border border-border text-xs text-text-muted">
                  ⌘
                </kbd>
                <kbd className="px-2 py-1 rounded bg-bg-surface border border-border text-xs text-text-muted">
                  K
                </kbd>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Quick Start</h2>
            <p className="text-text-secondary">Get up and running in under 5 minutes.</p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="space-y-8">
              {/* Step 1 */}
              <div className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                    1
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-h5 text-text-primary mb-2">Install SQL2.AI</h3>
                  <p className="text-small text-text-secondary mb-4">
                    Install the CLI tool globally using npm or your preferred package manager.
                  </p>
                  <TerminalBlock
                    commands={[
                      { command: 'npm install -g @sql2ai/cli' },
                    ]}
                  />
                </div>
              </div>

              {/* Step 2 */}
              <div className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                    2
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-h5 text-text-primary mb-2">Configure Your Connection</h3>
                  <p className="text-small text-text-secondary mb-4">
                    Set up your database connection using the interactive configuration wizard.
                  </p>
                  <TerminalBlock
                    commands={[
                      {
                        command: 'sql2ai config init',
                        output: `SQL2.AI Configuration Wizard

? Database type: PostgreSQL
? Connection string: postgres://user@localhost/mydb
? Save connection as: dev

✓ Configuration saved to ~/.sql2ai/config.yaml`
                      },
                    ]}
                  />
                </div>
              </div>

              {/* Step 3 */}
              <div className="flex gap-6">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
                    3
                  </div>
                </div>
                <div className="flex-1">
                  <h3 className="text-h5 text-text-primary mb-2">Run Your First Analysis</h3>
                  <p className="text-small text-text-secondary mb-4">
                    Analyze your database schema to discover issues and optimization opportunities.
                  </p>
                  <TerminalBlock
                    commands={[
                      {
                        command: 'sql2ai analyze --connection dev',
                        output: `Connecting to PostgreSQL...
Analyzing schema...

Schema Analysis Complete

Tables: 23 | Views: 5 | Procedures: 12

✓ All tables have primary keys
⚠ 2 tables missing foreign keys
⚠ 3 unused indexes detected
✓ Naming conventions: 98% compliant

Full report saved to ./sql2ai-report.html`
                      },
                    ]}
                  />
                </div>
              </div>
            </div>

            <div className="mt-12 text-center">
              <Link href="/docs/quickstart" className="btn-primary">
                View Full Quick Start Guide
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Documentation Categories */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Browse Documentation</h2>
            <p className="text-text-secondary">
              Find guides, references, and tutorials for every part of SQL2.AI.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {categories.map((category) => (
              <div key={category.title} className="card p-6 hover:border-border-emphasis transition-colors">
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
                  {category.icon}
                </div>
                <h3 className="text-h5 text-text-primary mb-2">{category.title}</h3>
                <p className="text-small text-text-muted mb-4">{category.description}</p>
                <ul className="space-y-2">
                  {category.links.map((link) => (
                    <li key={link.href}>
                      <Link
                        href={link.href}
                        className="text-small text-text-secondary hover:text-primary transition-colors inline-flex items-center gap-1"
                      >
                        {link.title}
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Database-Specific Guides */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Database-Specific Guides</h2>
            <p className="text-text-secondary">
              Detailed documentation for each supported database platform.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            {/* PostgreSQL */}
            <Link href="/docs/postgresql" className="card p-8 hover:border-postgresql/50 transition-colors group">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-postgresql/10 flex items-center justify-center">
                  <span className="text-postgresql font-bold text-xl">PG</span>
                </div>
                <div>
                  <h3 className="text-h4 text-text-primary group-hover:text-postgresql transition-colors">PostgreSQL</h3>
                  <p className="text-small text-text-muted">Version 9.6 and above</p>
                </div>
              </div>
              <ul className="space-y-2 text-small text-text-secondary">
                <li>Analyze PostgreSQL-specific features (CTEs, window functions)</li>
                <li>Optimize EXPLAIN ANALYZE output</li>
                <li>Generate native PL/pgSQL procedures</li>
                <li>Index recommendations for JSONB columns</li>
              </ul>
            </Link>

            {/* SQL Server */}
            <Link href="/docs/sqlserver" className="card p-8 hover:border-sqlserver/50 transition-colors group">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-sqlserver/10 flex items-center justify-center">
                  <span className="text-sqlserver font-bold text-xl">MS</span>
                </div>
                <div>
                  <h3 className="text-h4 text-text-primary group-hover:text-sqlserver transition-colors">SQL Server</h3>
                  <p className="text-small text-text-muted">Version 2016 and above</p>
                </div>
              </div>
              <ul className="space-y-2 text-small text-text-secondary">
                <li>Parse execution plans with missing index hints</li>
                <li>Optimize T-SQL stored procedures</li>
                <li>Analyze columnstore index candidates</li>
                <li>Support for temporal tables and CDC</li>
              </ul>
            </Link>
          </div>
        </div>
      </section>

      {/* Community & Support */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Need Help?</h2>
            <p className="text-text-secondary">
              Our community and support team are here to help you succeed.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <a
              href="https://github.com/sql2ai/sql2ai/discussions"
              target="_blank"
              rel="noopener noreferrer"
              className="card p-6 text-center hover:border-border-emphasis transition-colors"
            >
              <div className="w-12 h-12 rounded-lg bg-bg-elevated flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-text-muted" fill="currentColor" viewBox="0 0 24 24">
                  <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">GitHub Discussions</h3>
              <p className="text-small text-text-muted">Ask questions and share ideas with the community.</p>
            </a>

            <a
              href="https://discord.gg/sql2ai"
              target="_blank"
              rel="noopener noreferrer"
              className="card p-6 text-center hover:border-border-emphasis transition-colors"
            >
              <div className="w-12 h-12 rounded-lg bg-bg-elevated flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-text-muted" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.317 4.37a19.791 19.791 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">Discord Community</h3>
              <p className="text-small text-text-muted">Chat with developers and get real-time help.</p>
            </a>

            <Link href="/contact" className="card p-6 text-center hover:border-border-emphasis transition-colors">
              <div className="w-12 h-12 rounded-lg bg-bg-elevated flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-text-muted" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">Email Support</h3>
              <p className="text-small text-text-muted">For paid plans, get direct email support.</p>
            </Link>
          </div>
        </div>
      </section>
    </>
  );
}
