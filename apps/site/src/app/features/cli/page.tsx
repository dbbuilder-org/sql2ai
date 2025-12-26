import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL CLI - Command-Line Power Tools | SQL2.AI',
  description:
    'Full-featured CLI for SQL2.AI. Script migrations, run compliance checks, generate code, and integrate with CI/CD pipelines from your terminal.',
};

export default function CLIPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-lime-500/10 flex items-center justify-center text-lime-500">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL CLI</h1>
                <p className="text-lg text-lime-500 font-medium">Command-Line Power Tools</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              All of SQL2.AI from your terminal. Script migrations, run compliance checks, generate
              TypeScript types, and integrate seamlessly with CI/CD pipelines.
            </p>

            <div className="card p-4 bg-bg-surface">
              <pre className="text-sm overflow-x-auto">
                <code className="text-text-secondary">{`$ npm install -g @sql2ai/cli
$ sql2ai init
$ sql2ai query "Show customers who haven't ordered in 90 days" --generate`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Use Cases */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Built for Every Workflow</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Local Development</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto mb-4">
                <code className="text-text-secondary">{`# Quick schema inspection
sql2ai schema show customers

# Generate SQL with AI
sql2ai query "Get monthly sales" --generate

# Run migrations locally
sql2ai migrate up`}</code>
              </pre>
              <p className="text-small text-text-muted">
                Inspect schemas, generate queries, and manage migrations without leaving your terminal.
              </p>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">CI/CD Integration</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto mb-4">
                <code className="text-text-secondary">{`# In your pipeline
sql2ai migrate validate
sql2ai comply check --framework soc2
sql2ai codegen --lang typescript`}</code>
              </pre>
              <p className="text-small text-text-muted">
                Validate migrations, run compliance checks, and generate types in your CI/CD pipeline.
              </p>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Automation</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto mb-4">
                <code className="text-text-secondary">{`# Batch operations
for db in prod staging dev; do
  sql2ai --connection $db \\
    comply check --framework hipaa
done`}</code>
              </pre>
              <p className="text-small text-text-muted">
                Script complex workflows across multiple databases with full automation.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Core Commands */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Core Commands</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Schema Operations</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                <code className="text-text-secondary">{`# View schema
sql2ai schema show
sql2ai schema show customers

# Export to different formats
sql2ai schema export --format json
sql2ai schema export --format sql

# Search across schema
sql2ai schema search "customer"`}</code>
              </pre>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Query Operations</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                <code className="text-text-secondary">{`# Execute queries
sql2ai query "SELECT * FROM customers"
sql2ai query --file report.sql

# AI-powered generation
sql2ai query "Show top spenders" --generate

# Optimize queries
sql2ai query optimize --file slow.sql`}</code>
              </pre>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Migration Management</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                <code className="text-text-secondary">{`# Generate new migration
sql2ai migrate new "add loyalty points"

# Apply migrations
sql2ai migrate up
sql2ai migrate up --to 20250115_001

# Rollback
sql2ai migrate down

# Preview without applying
sql2ai migrate up --dry-run`}</code>
              </pre>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-4">Code Generation</h3>
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                <code className="text-text-secondary">{`# Generate TypeScript types
sql2ai codegen --lang typescript

# Generate C# Dapper models
sql2ai codegen --lang csharp

# Generate API from stored procs
sql2ai codegen api --framework fastapi

# Watch mode for development
sql2ai codegen --lang typescript --watch`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CI/CD Examples */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">CI/CD Integration</h2>
            <p className="text-text-secondary text-center mb-12">
              Drop SQL2.AI CLI into your existing pipelines
            </p>

            <div className="space-y-8">
              <div className="card p-6">
                <h3 className="text-h6 text-text-primary mb-3">GitHub Actions</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                  <code className="text-text-secondary">{`name: Database CI
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install SQL2AI CLI
        run: npm install -g @sql2ai/cli

      - name: Validate Migrations
        run: sql2ai migrate validate
        env:
          SQL2AI_API_KEY: \${{ secrets.SQL2AI_API_KEY }}

      - name: Run Compliance Check
        run: sql2ai comply check --framework soc2

      - name: Verify Generated Types
        run: |
          sql2ai codegen --lang typescript --output ./src/types
          git diff --exit-code src/types`}</code>
                </pre>
              </div>

              <div className="card p-6">
                <h3 className="text-h6 text-text-primary mb-3">Pre-commit Hook</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                  <code className="text-text-secondary">{`#!/bin/bash
# .git/hooks/pre-commit

# Validate SQL files
sql2ai query validate --files "**/*.sql"

# Check for migrations
if git diff --cached --name-only | grep -q "migrations/"; then
  sql2ai migrate validate
fi`}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* MCP Integration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Works with Claude</h2>
            <p className="text-text-secondary mb-8">
              SQL CLI includes an MCP server mode for seamless Claude Desktop and Claude Code integration.
            </p>

            <div className="card p-6 text-left">
              <pre className="bg-bg-surface rounded-lg p-4 text-xs overflow-x-auto">
                <code className="text-text-secondary">{`# Start MCP server mode
sql2ai mcp serve

# Configure in Claude Desktop (~/.config/claude/claude_desktop_config.json)
{
  "mcpServers": {
    "sql2ai": {
      "command": "sql2ai",
      "args": ["mcp", "serve"]
    }
  }
}`}</code>
              </pre>
              <p className="text-small text-text-muted mt-4">
                Once configured, Claude can directly query your databases, generate SQL, and analyze schemas.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Installation */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Installation</h2>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-3">NPM</h3>
              <pre className="bg-bg-surface rounded-lg p-3 text-xs">
                <code className="text-text-secondary">npm install -g @sql2ai/cli</code>
              </pre>
            </div>

            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-3">Homebrew</h3>
              <pre className="bg-bg-surface rounded-lg p-3 text-xs">
                <code className="text-text-secondary">{`brew tap sql2ai/tap
brew install sql2ai`}</code>
              </pre>
            </div>

            <div className="card p-6 text-center">
              <h3 className="text-h6 text-text-primary mb-3">Direct Download</h3>
              <pre className="bg-bg-surface rounded-lg p-3 text-xs">
                <code className="text-text-secondary">curl -L sql2ai.com/install.sh | sh</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Everything You Need</h2>

          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-lime-500/10 flex items-center justify-center text-lime-500 mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Multi-Database</h3>
              <p className="text-small text-text-muted">SQL Server, PostgreSQL, MySQL</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-lime-500/10 flex items-center justify-center text-lime-500 mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Compliance Built-in</h3>
              <p className="text-small text-text-muted">SOC2, HIPAA, GDPR checks</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-lime-500/10 flex items-center justify-center text-lime-500 mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Code Generation</h3>
              <p className="text-small text-text-muted">TypeScript, C#, Python types</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-lime-500/10 flex items-center justify-center text-lime-500 mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">AI-Powered</h3>
              <p className="text-small text-text-muted">Generate queries from text</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Automate Your Database Workflow?"
        description="Install SQL CLI and bring SQL2.AI to your terminal in seconds."
        primaryCTA={{ text: 'Get Started', href: '/docs/cli' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
