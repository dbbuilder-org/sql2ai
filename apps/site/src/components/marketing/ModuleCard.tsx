import Link from 'next/link';

export interface Module {
  id: string;
  name: string;
  tagline: string;
  description: string;
  icon: JSX.Element;
  color: 'primary' | 'success' | 'warning' | 'postgresql' | 'sqlserver' | 'error';
  href: string;
  capabilities: string[];
  comingSoon?: boolean;
}

const colorClasses = {
  primary: {
    bg: 'bg-primary/10',
    text: 'text-primary',
    border: 'border-primary/30',
    hover: 'hover:border-primary',
  },
  success: {
    bg: 'bg-success/10',
    text: 'text-success',
    border: 'border-success/30',
    hover: 'hover:border-success',
  },
  warning: {
    bg: 'bg-warning/10',
    text: 'text-warning',
    border: 'border-warning/30',
    hover: 'hover:border-warning',
  },
  postgresql: {
    bg: 'bg-postgresql/10',
    text: 'text-postgresql',
    border: 'border-postgresql/30',
    hover: 'hover:border-postgresql',
  },
  sqlserver: {
    bg: 'bg-sqlserver/10',
    text: 'text-sqlserver',
    border: 'border-sqlserver/30',
    hover: 'hover:border-sqlserver',
  },
  error: {
    bg: 'bg-error/10',
    text: 'text-error',
    border: 'border-error/30',
    hover: 'hover:border-error',
  },
};

interface ModuleCardProps {
  module: Module;
  size?: 'default' | 'large';
}

export function ModuleCard({ module, size = 'default' }: ModuleCardProps): JSX.Element {
  const colors = colorClasses[module.color];
  const isLarge = size === 'large';

  return (
    <Link
      href={module.href}
      className={`card p-6 ${colors.hover} transition-all group relative ${
        module.comingSoon ? 'opacity-75' : ''
      }`}
    >
      {module.comingSoon && (
        <span className="absolute top-4 right-4 text-xs font-mono bg-bg-surface px-2 py-1 rounded-full border border-border text-text-muted">
          Coming Soon
        </span>
      )}

      <div className="flex items-start gap-4 mb-4">
        <div
          className={`${isLarge ? 'w-14 h-14' : 'w-12 h-12'} rounded-xl ${colors.bg} flex items-center justify-center ${colors.text} shrink-0`}
        >
          {module.icon}
        </div>
        <div>
          <h3 className={`${isLarge ? 'text-h4' : 'text-h5'} text-text-primary mb-1`}>
            {module.name}
          </h3>
          <p className={`text-small ${colors.text} font-medium`}>{module.tagline}</p>
        </div>
      </div>

      <p className="text-small text-text-secondary mb-4">{module.description}</p>

      <ul className="space-y-2 mb-4">
        {module.capabilities.slice(0, isLarge ? 5 : 3).map((capability) => (
          <li key={capability} className="flex items-start gap-2 text-xs text-text-muted">
            <svg
              className={`w-3 h-3 ${colors.text} shrink-0 mt-0.5`}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={3}
                d="M5 13l4 4L19 7"
              />
            </svg>
            {capability}
          </li>
        ))}
      </ul>

      <div className="pt-4 border-t border-border-subtle">
        <span className={`text-small ${colors.text} font-medium group-hover:underline`}>
          Learn more →
        </span>
      </div>
    </Link>
  );
}

export function ModuleGrid({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">{children}</div>
  );
}

// Predefined modules data
export const modules: Module[] = [
  {
    id: 'orchestrator',
    name: 'SQL Orchestrator',
    tagline: 'Unified Monitoring & Compliance',
    description:
      'Centralized monitoring, security auditing, and compliance checking with before/after context for change impact analysis.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        />
      </svg>
    ),
    color: 'primary',
    href: '/features/orchestrator/',
    capabilities: [
      'Multi-trigger check execution (scheduled, deployment, anomaly)',
      'Performance, security, and compliance checks',
      'Schema snapshots for before/after comparison',
      'Agent-based distributed collection',
      'Automated compliance evidence gathering',
    ],
  },
  {
    id: 'migrator',
    name: 'SQL Migrator',
    tagline: 'Database-First Migrations',
    description:
      'Generate code from your database, not the reverse. Auto-generate Dapper models, TypeScript types, and versioned migrations.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
        />
      </svg>
    ),
    color: 'success',
    href: '/features/migrator/',
    capabilities: [
      'Database-first schema capture',
      'Auto-generate Dapper C# models',
      'Generate TypeScript types for APIs',
      'Convert DACPAC to versioned migrations',
      'Dependency-aware rollback scripts',
    ],
  },
  {
    id: 'version',
    name: 'SQL Version',
    tagline: 'Git for Your Database',
    description:
      'Track every change to every database object. Full history, blame, diff, and rollback for stored procedures, views, and more.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    ),
    color: 'warning',
    href: '/features/version/',
    capabilities: [
      'Object-level version history',
      'Diff between any two versions',
      'Line-by-line blame attribution',
      'Branch support for environments',
      'Merge conflict detection',
    ],
  },
  {
    id: 'code',
    name: 'SQL Code',
    tagline: 'Swagger for Databases',
    description:
      'Automated code review, AI-powered data dictionary, and release notes generation. Document your database like an API.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    ),
    color: 'postgresql',
    href: '/features/code/',
    capabilities: [
      'AI-inferred column descriptions',
      'Auto-generate data dictionaries',
      'Security vulnerability scanning',
      'Release notes from migrations',
      'OpenAPI-style schema export',
    ],
  },
  {
    id: 'writer',
    name: 'SQL Writer',
    tagline: 'AI DDL & SP Generation',
    description:
      'Beyond text-to-SQL. Generate complete stored procedures, views, functions, and triggers with proper error handling and transactions.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
        />
      </svg>
    ),
    color: 'primary',
    href: '/features/writer/',
    capabilities: [
      'Generate complete stored procedures',
      'Views with optimization hints',
      'Proper TRY/CATCH error handling',
      'Transaction management',
      'Security best practices built-in',
    ],
  },
  {
    id: 'ssms',
    name: 'SSMS Plugin',
    tagline: 'AI in Your IDE',
    description:
      'Bring SQL2.AI directly into SQL Server Management Studio. Inline AI suggestions, query optimization, and execution plan analysis.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
      </svg>
    ),
    color: 'sqlserver',
    href: '/features/ssms/',
    capabilities: [
      'Inline AI query completions',
      'Right-click "Explain Query"',
      'Execution plan analysis',
      'Generate CRUD procedures',
      'Local LLM for air-gapped environments',
    ],
    comingSoon: true,
  },
  {
    id: 'optimize',
    name: 'SQL Optimize',
    tagline: 'AI-Driven Performance',
    description:
      'Deep analysis of Query Store, wait statistics, and execution plans. Get prioritized remediation with one-click fixes.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M13 10V3L4 14h7v7l9-11h-7z"
        />
      </svg>
    ),
    color: 'warning',
    href: '/features/optimize/',
    capabilities: [
      'Query Store analysis',
      'Plan regression detection',
      'Parameter sniffing fixes',
      'Missing index recommendations',
      'One-click remediation scripts',
    ],
  },
  {
    id: 'comply',
    name: 'SQL Comply',
    tagline: 'SOC2, HIPAA, GDPR & More',
    description:
      'Automated compliance checking at the database level. Scan actual data for PII/PHI with Presidio integration.',
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
        />
      </svg>
    ),
    color: 'error',
    href: '/features/comply/',
    capabilities: [
      'SOC 2 Type I & II controls',
      'HIPAA PHI detection',
      'GDPR data classification',
      'PCI-DSS cardholder checks',
      'Presidio PII scanning',
    ],
  },
];
