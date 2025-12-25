import { Metadata } from 'next';
import Link from 'next/link';
import { TerminalBlock } from '../../components/ui';
import { CTASection } from '../../components/marketing';

export const metadata: Metadata = {
  title: 'Features',
  description:
    'Explore SQL2.AI features: schema analysis, query optimization, refactoring, indexing, documentation, versioning, and deployment for SQL Server and PostgreSQL.',
};

interface FeatureSection {
  id: string;
  stage: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  capabilities: string[];
  example?: {
    title: string;
    commands: { command: string; output?: string }[];
  };
}

const features: FeatureSection[] = [
  {
    id: 'analyze',
    stage: '01',
    title: 'Schema Analysis',
    description:
      'Deep understanding of your database structure. Detect anti-patterns, identify optimization opportunities, and get actionable insights about your schema health.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    color: 'primary',
    capabilities: [
      'Detect missing foreign keys and orphaned relationships',
      'Identify unused indexes consuming resources',
      'Find tables without primary keys',
      'Analyze naming convention consistency',
      'Map dependencies between objects',
      'Generate ER diagrams from live databases',
    ],
    example: {
      title: 'Analyze your schema',
      commands: [
        {
          command: 'sql2ai analyze --connection postgres://localhost/mydb',
          output: `Schema Analysis Complete

Tables: 47 | Views: 12 | Procedures: 23

Issues Found:
  ⚠ 3 tables missing primary keys
  ⚠ 7 unused indexes (12.4 GB)
  ⚠ 2 circular dependencies detected
  ✓ Naming conventions: 94% compliant`,
        },
      ],
    },
  },
  {
    id: 'optimize',
    stage: '02',
    title: 'Query Optimization',
    description:
      'AI-powered query analysis that understands execution plans. Get specific recommendations to improve performance, reduce resource usage, and eliminate bottlenecks.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    color: 'warning',
    capabilities: [
      'Parse and analyze execution plans automatically',
      'Identify table scans and missing indexes',
      'Detect implicit conversions causing slowdowns',
      'Suggest query rewrites for better performance',
      'Compare before/after performance metrics',
      'Batch optimize multiple queries at once',
    ],
    example: {
      title: 'Optimize a slow query',
      commands: [
        {
          command: 'sql2ai optimize --file slow-query.sql',
          output: `Query Analysis Complete

Original Cost: 847.32 | Optimized Cost: 12.45
Improvement: 98.5%

Recommendations Applied:
  1. Added covering index on Orders(CustomerID, OrderDate)
  2. Replaced correlated subquery with JOIN
  3. Added WHERE clause predicate pushdown

✓ Optimized query saved to slow-query.optimized.sql`,
        },
      ],
    },
  },
  {
    id: 'refactor',
    stage: '03',
    title: 'Code Refactoring',
    description:
      'Modernize legacy SQL code without breaking functionality. Refactor stored procedures, update deprecated syntax, and improve maintainability while preserving behavior.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    color: 'success',
    capabilities: [
      'Convert cursors to set-based operations',
      'Update deprecated SQL syntax',
      'Extract common logic into reusable functions',
      'Standardize error handling patterns',
      'Add transaction management where missing',
      'Generate migration scripts for changes',
    ],
    example: {
      title: 'Refactor a stored procedure',
      commands: [
        {
          command: 'sql2ai refactor --file legacy-proc.sql --style modern',
          output: `Refactoring Analysis

Changes Applied:
  ✓ Converted 3 cursors to set-based CTEs
  ✓ Updated 12 deprecated RAISERROR calls
  ✓ Added TRY/CATCH error handling
  ✓ Replaced dynamic SQL with parameterized queries

Lines: 847 → 412 (-51%)
Complexity Score: 89 → 34 (improved)`,
        },
      ],
    },
  },
  {
    id: 'index',
    stage: '04',
    title: 'Index Management',
    description:
      'Intelligent index recommendations based on actual query patterns. Find missing indexes, identify redundant ones, and optimize your indexing strategy.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
      </svg>
    ),
    color: 'postgresql',
    capabilities: [
      'Analyze query workload for index opportunities',
      'Detect duplicate and overlapping indexes',
      'Calculate index usage statistics',
      'Recommend covering indexes',
      'Generate CREATE/DROP INDEX scripts',
      'Estimate storage and maintenance impact',
    ],
    example: {
      title: 'Analyze index usage',
      commands: [
        {
          command: 'sql2ai index analyze --connection mssql://localhost/mydb',
          output: `Index Analysis Complete

Current Indexes: 127 | Size: 45.2 GB

Recommendations:
  + Add 4 new indexes (est. +2.1 GB)
  - Remove 11 unused indexes (-8.7 GB)
  ~ Modify 3 indexes for better coverage

Net Impact: -6.6 GB storage, +47% query performance`,
        },
      ],
    },
  },
  {
    id: 'document',
    stage: '05',
    title: 'Documentation',
    description:
      'Auto-generate comprehensive documentation from your database. Create data dictionaries, document stored procedures, and keep documentation in sync with schema changes.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    ),
    color: 'primary',
    capabilities: [
      'Generate data dictionaries automatically',
      'Document stored procedures with parameters',
      'Create relationship diagrams',
      'Track schema change history',
      'Export to Markdown, HTML, or PDF',
      'Integrate with your documentation system',
    ],
    example: {
      title: 'Generate documentation',
      commands: [
        {
          command: 'sql2ai docs generate --format markdown --output ./docs',
          output: `Documentation Generated

Files Created:
  ./docs/schema/README.md
  ./docs/schema/tables/*.md (47 files)
  ./docs/schema/procedures/*.md (23 files)
  ./docs/diagrams/er-diagram.svg
  ./docs/data-dictionary.md

✓ Documentation published to ./docs`,
        },
      ],
    },
  },
  {
    id: 'version',
    stage: '06',
    title: 'Version Control',
    description:
      'Database-native version control that understands SQL. Track schema changes, manage migrations, and maintain a complete history of your database evolution.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    ),
    color: 'warning',
    capabilities: [
      'Track all schema objects in git-friendly format',
      'Generate reversible migration scripts',
      'Detect schema drift between environments',
      'Compare database versions side-by-side',
      'Merge changes from multiple developers',
      'Integrate with CI/CD pipelines',
    ],
    example: {
      title: 'Generate migrations',
      commands: [
        {
          command: 'sql2ai version diff --source dev --target prod',
          output: `Schema Comparison: dev → prod

Differences Found:
  + 3 new tables
  ~ 7 modified columns
  + 2 new stored procedures
  - 1 removed index

Migration scripts generated:
  ./migrations/20241224_001_up.sql
  ./migrations/20241224_001_down.sql`,
        },
      ],
    },
  },
  {
    id: 'deploy',
    stage: '07',
    title: 'Deployment',
    description:
      'Safe, automated database deployments with rollback support. Validate changes before applying, track deployment history, and ensure zero-downtime updates.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
      </svg>
    ),
    color: 'success',
    capabilities: [
      'Validate migrations before deployment',
      'Execute with automatic rollback on failure',
      'Track deployment history and status',
      'Support for blue-green deployments',
      'Integrate with GitHub Actions, Azure DevOps',
      'Dry-run mode for safety',
    ],
    example: {
      title: 'Deploy to production',
      commands: [
        {
          command: 'sql2ai deploy --target prod --dry-run',
          output: `Deployment Preview: prod

Validating migrations...
  ✓ Syntax validation passed
  ✓ Dependency check passed
  ✓ Rollback scripts validated

Changes to Apply:
  1. ALTER TABLE Customers ADD LoyaltyTier
  2. CREATE INDEX IX_Orders_Status
  3. UPDATE sp_ProcessOrder (v2.1.0)

Ready to deploy. Run without --dry-run to apply.`,
        },
      ],
    },
  },
];

function getColorClasses(color: string) {
  const colors: Record<string, { bg: string; text: string; border: string }> = {
    primary: { bg: 'bg-primary/10', text: 'text-primary', border: 'border-primary/30' },
    success: { bg: 'bg-success/10', text: 'text-success', border: 'border-success/30' },
    warning: { bg: 'bg-warning/10', text: 'text-warning', border: 'border-warning/30' },
    postgresql: { bg: 'bg-postgresql/10', text: 'text-postgresql', border: 'border-postgresql/30' },
    sqlserver: { bg: 'bg-sqlserver/10', text: 'text-sqlserver', border: 'border-sqlserver/30' },
  };
  return colors[color] || colors.primary;
}

export default function FeaturesPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-h1 text-text-primary mb-6">
              The Complete Database
              <br />
              <span className="gradient-text">Development Lifecycle</span>
            </h1>
            <p className="text-lg text-text-secondary mb-8">
              Seven stages, one platform. From initial analysis to production deployment,
              SQL2.AI provides AI-powered tools for every step of database development.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {features.map((feature) => (
                <a
                  key={feature.id}
                  href={`#${feature.id}`}
                  className="px-4 py-2 rounded-full bg-bg-surface border border-border text-small text-text-secondary hover:text-text-primary hover:border-border-emphasis transition-colors"
                >
                  {feature.title.split(' ')[0]}
                </a>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Feature Sections */}
      {features.map((feature, index) => {
        const colorClasses = getColorClasses(feature.color);
        const isEven = index % 2 === 0;

        return (
          <section
            key={feature.id}
            id={feature.id}
            className={`py-20 md:py-32 ${isEven ? 'bg-bg-surface' : ''}`}
          >
            <div className="container-wide">
              <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
                {/* Content */}
                <div className={isEven ? 'lg:order-1' : 'lg:order-2'}>
                  <div className="flex items-center gap-4 mb-6">
                    <span className={`text-xs font-mono ${colorClasses.text}`}>
                      STAGE {feature.stage}
                    </span>
                    <div className={`h-px flex-1 ${colorClasses.border} border-t`} />
                  </div>

                  <div className="flex items-center gap-4 mb-4">
                    <div className={`w-12 h-12 rounded-xl ${colorClasses.bg} flex items-center justify-center ${colorClasses.text}`}>
                      {feature.icon}
                    </div>
                    <h2 className="text-h2 text-text-primary">{feature.title}</h2>
                  </div>

                  <p className="text-lg text-text-secondary mb-8">
                    {feature.description}
                  </p>

                  <ul className="grid sm:grid-cols-2 gap-3 mb-8">
                    {feature.capabilities.map((capability) => (
                      <li key={capability} className="flex items-start gap-2 text-small text-text-secondary">
                        <svg className={`w-4 h-4 ${colorClasses.text} shrink-0 mt-0.5`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        {capability}
                      </li>
                    ))}
                  </ul>

                  <Link
                    href={`/docs/${feature.id}`}
                    className="inline-flex items-center gap-2 text-primary hover:underline font-medium"
                  >
                    Learn more about {feature.title.toLowerCase()}
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </Link>
                </div>

                {/* Example */}
                <div className={isEven ? 'lg:order-2' : 'lg:order-1'}>
                  {feature.example && (
                    <TerminalBlock
                      title={feature.example.title}
                      commands={feature.example.commands}
                    />
                  )}
                </div>
              </div>
            </div>
          </section>
        );
      })}

      {/* Platform Support */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-h2 text-text-primary mb-4">
              Works With Your Stack
            </h2>
            <p className="text-lg text-text-secondary">
              SQL2.AI integrates seamlessly with your existing tools and workflows.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {/* Databases */}
            <div className="card p-6 text-center">
              <h3 className="text-h5 text-text-primary mb-4">Databases</h3>
              <div className="flex justify-center gap-6">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-postgresql/10 flex items-center justify-center">
                    <span className="text-postgresql font-bold">PG</span>
                  </div>
                  <span className="text-xs text-text-muted">PostgreSQL</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-sqlserver/10 flex items-center justify-center">
                    <span className="text-sqlserver font-bold">MS</span>
                  </div>
                  <span className="text-xs text-text-muted">SQL Server</span>
                </div>
              </div>
            </div>

            {/* Interfaces */}
            <div className="card p-6 text-center">
              <h3 className="text-h5 text-text-primary mb-4">Interfaces</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted font-mono text-sm">&gt;_</span>
                  </div>
                  <span className="text-xs text-text-muted">CLI</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted font-bold text-sm">MCP</span>
                  </div>
                  <span className="text-xs text-text-muted">Claude</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted font-mono text-sm">{'{}'}</span>
                  </div>
                  <span className="text-xs text-text-muted">SDK</span>
                </div>
              </div>
            </div>

            {/* Integrations */}
            <div className="card p-6 text-center">
              <h3 className="text-h5 text-text-primary mb-4">CI/CD</h3>
              <div className="flex justify-center gap-4">
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-lg">GH</span>
                  </div>
                  <span className="text-xs text-text-muted">GitHub</span>
                </div>
                <div className="flex flex-col items-center gap-2">
                  <div className="w-12 h-12 rounded-lg bg-bg-surface flex items-center justify-center">
                    <span className="text-text-muted text-lg">AZ</span>
                  </div>
                  <span className="text-xs text-text-muted">Azure</span>
                </div>
              </div>
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
