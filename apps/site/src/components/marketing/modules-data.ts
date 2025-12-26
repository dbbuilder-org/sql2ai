// Module data - shared between server and client components
// This file intentionally does NOT have 'use client' so it can be used in server components

export interface Module {
  id: string;
  name: string;
  tagline: string;
  description: string;
  icon: string;
  color: string;
  href: string;
  capabilities: string[];
  comingSoon?: boolean;
}

// Icon SVGs as strings
const icons = {
  orchestrate: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
  monitor: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
  optimize: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>`,
  centralize: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>`,
  migrate: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"/></svg>`,
  convert: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>`,
  containerize: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>`,
  version: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`,
  code: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>`,
  writer: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>`,
  ssms: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`,
  test: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"/></svg>`,
  simulate: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"/></svg>`,
  anonymize: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z"/></svg>`,
  standardize: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"/></svg>`,
  comply: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>`,
  audit: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>`,
  encrypt: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/></svg>`,
  tenant: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg>`,
  send: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/></svg>`,
  receive: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4 0v8m0 0l3-3m-3 3L9 9"/></svg>`,
  connect: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`,
  import: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/></svg>`,
  agent: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>`,
  converse: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>`,
  compare: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>`,
  cli: `<svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>`,
};

// Colors for each module
const colors = {
  primary: '#7C3AED',
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  postgresql: '#336791',
  sqlserver: '#CC2927',
  teal: '#14B8A6',
  indigo: '#6366F1',
  pink: '#EC4899',
  cyan: '#06B6D4',
  orange: '#F97316',
  lime: '#84CC16',
  rose: '#F43F5E',
};

// All 26 modules organized by category
export const modules: Module[] = [
  // DBA TOOLS
  {
    id: 'monitor',
    name: 'SQL Monitor',
    tagline: 'Real-Time Database Monitoring',
    description:
      'Comprehensive monitoring dashboard for SQL Server and PostgreSQL. Track performance, connections, queries, and health metrics in real-time.',
    icon: icons.monitor,
    color: colors.info,
    href: '/features/monitor/',
    capabilities: [
      'Real-time performance dashboards',
      'Query performance tracking',
      'Connection pool monitoring',
      'Alert and notification system',
      'Historical trend analysis',
    ],
  },
  {
    id: 'orchestrate',
    name: 'SQL Orchestrate',
    tagline: 'Unified Job & Check Management',
    description:
      'Central hub for all database monitoring, job scheduling, and compliance checking. Manages Azure Functions, Lambda, GCP Cloud Functions, and cron jobs from one platform.',
    icon: icons.orchestrate,
    color: colors.primary,
    href: '/features/orchestrate/',
    capabilities: [
      'Unified scheduler for Azure Functions, Lambda, cron',
      'Multi-trigger execution (scheduled, deployment, anomaly)',
      'Performance, security, and compliance checks',
      'Schema snapshots for before/after comparison',
      'Dashboard integration with SQL Monitor',
    ],
  },
  {
    id: 'optimize',
    name: 'SQL Optimize',
    tagline: 'AI-Driven Performance',
    description:
      'Deep analysis of Query Store, wait statistics, and execution plans. Get prioritized remediation with one-click fixes.',
    icon: icons.optimize,
    color: colors.orange,
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
    id: 'centralize',
    name: 'SQL Centralize',
    tagline: 'Multi-Tier Replication',
    description:
      'FK-aware data replication, consolidation, and ETL. Supports SQL Server and PostgreSQL with minimal source impact.',
    icon: icons.centralize,
    color: colors.postgresql,
    href: '/features/centralize/',
    capabilities: [
      'FK-sensitive sync ordering',
      'Real-time and batch modes',
      'Bidirectional replication',
      'Multi-tier architectures',
      'Cross-platform (SQL ↔ PG)',
    ],
  },
  // MIGRATION TOOLS
  {
    id: 'migrate',
    name: 'SQL Migrate',
    tagline: 'Database-First Migrations',
    description:
      'Generate code from your database, not the reverse. Auto-generate Dapper models, TypeScript types, and versioned migrations.',
    icon: icons.migrate,
    color: colors.success,
    href: '/features/migrate/',
    capabilities: [
      'Database-first schema capture',
      'Auto-generate Dapper C# models',
      'Generate TypeScript types for APIs',
      'Convert DACPAC to versioned migrations',
      'Dependency-aware rollback scripts',
    ],
  },
  {
    id: 'convert',
    name: 'SQL Convert',
    tagline: 'Cross-Platform Migration',
    description:
      'AI-powered migration between SQL Server (On-Prem, MI, Azure SQL) and PostgreSQL. Converts Agent jobs to Azure Functions, handles cross-DB queries.',
    icon: icons.convert,
    color: colors.teal,
    href: '/features/convert/',
    capabilities: [
      'SQL Server ↔ PostgreSQL conversion',
      'Agent jobs → Azure Functions',
      'Cross-database query resolution',
      'xp_cmdshell replacement',
      'Plan-Execute-Test-Integrate workflow',
    ],
  },
  {
    id: 'containerize',
    name: 'SQL Containerize',
    tagline: 'Docker & Kubernetes Migration',
    description:
      'Migrate databases from on-prem or cloud VMs to Docker, Kubernetes (AKS/EKS/GKE), or cloud container services.',
    icon: icons.containerize,
    color: colors.cyan,
    href: '/features/containerize/',
    capabilities: [
      'Docker Compose generation',
      'Kubernetes StatefulSet configs',
      'Agent jobs → K8s CronJobs',
      'Zero-downtime migration',
      'Multi-cloud support (Azure, AWS, GCP)',
    ],
    comingSoon: true,
  },
  // DEVELOPER TOOLS
  {
    id: 'version',
    name: 'SQL Version',
    tagline: 'Git for Your Database',
    description:
      'Track every change to every database object. Full history, blame, diff, and rollback for stored procedures, views, and more.',
    icon: icons.version,
    color: colors.warning,
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
    icon: icons.code,
    color: colors.info,
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
    icon: icons.writer,
    color: colors.indigo,
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
    icon: icons.ssms,
    color: colors.sqlserver,
    href: '/features/ssms/',
    capabilities: [
      'Inline AI query completions',
      'Right-click "Explain Query"',
      'Execution plan analysis',
      'Generate CRUD procedures',
      'Local LLM for air-gapped environments',
    ],
  },
  {
    id: 'test',
    name: 'SQL Test',
    tagline: 'AI-Powered DB Testing',
    description:
      'Generate comprehensive unit and integration tests using tSQLt, pgTAP, and application testing frameworks.',
    icon: icons.test,
    color: colors.success,
    href: '/features/test/',
    capabilities: [
      'tSQLt test generation',
      'pgTAP test generation',
      'Multi-step integration tests',
      'Constraint and trigger testing',
      'Performance regression tests',
    ],
  },
  {
    id: 'compare',
    name: 'SQL Compare',
    tagline: 'AI Schema Comparison',
    description:
      'AI-powered hands-off comparison between databases. Generates modular, implementable sync scripts to align DDL and code across environments.',
    icon: icons.compare,
    color: colors.cyan,
    href: '/features/compare/',
    capabilities: [
      'AI-driven schema comparison',
      'Modular sync script generation',
      'DDL and stored procedure diff',
      'Safe deployment ordering',
      'Environment-aware migrations',
    ],
  },
  {
    id: 'cli',
    name: 'SQL CLI',
    tagline: 'Command-Line Power Tools',
    description:
      'Full-featured command-line interface for all SQL2.AI operations. Script migrations, run checks, generate code, and integrate with CI/CD pipelines.',
    icon: icons.cli,
    color: colors.lime,
    href: '/features/cli/',
    capabilities: [
      'Schema extraction and diff',
      'Migration generation and execution',
      'AI query generation from terminal',
      'CI/CD pipeline integration',
      'Batch operations and scripting',
    ],
  },
  // SYNTHETIC DATA
  {
    id: 'anonymize',
    name: 'SQL Anonymize',
    tagline: 'Secure Clean Room Data',
    description:
      'Create clean room environments with realistic data that bears no resemblance to source. Full privacy with FK integrity preserved.',
    icon: icons.anonymize,
    color: colors.pink,
    href: '/features/anonymize/',
    capabilities: [
      'Presidio-powered PII detection',
      'K-anonymity validation',
      'Consistent fake data generation',
      'FK relationship preservation',
      'Re-identification prevention',
    ],
  },
  {
    id: 'simulate',
    name: 'SQL Simulate',
    tagline: 'Synthetic Data Generation',
    description:
      'Generate realistic synthetic data from metadata without source access. Perfect for new systems, load testing, and demos.',
    icon: icons.simulate,
    color: colors.rose,
    href: '/features/simulate/',
    capabilities: [
      'AI-powered column understanding',
      'Distribution modeling',
      'FK-aware generation',
      'Edge case scenarios',
      'Scalable data volumes',
    ],
  },
  // INTEGRATION TOOLS
  {
    id: 'connect',
    name: 'SQL Connect',
    tagline: 'Data Layer Generation',
    description:
      'Generate complete APIs in FastAPI, .NET Core, Next.js, or Node.js with type-safe clients. Native SP integration with SAGA pattern support.',
    icon: icons.connect,
    color: colors.indigo,
    href: '/features/connect/',
    capabilities: [
      'FastAPI, .NET, Node.js generation',
      'Type-safe React/Vue clients',
      'Stored procedure integration',
      'SAGA pattern transactions',
      'Auto-sync with schema changes',
    ],
  },
  {
    id: 'import',
    name: 'SQL Import',
    tagline: 'Intelligent Data Ingestion',
    description:
      'Smart data import from CSV, Excel, JSON, and external databases with automatic schema detection, validation, and transformation.',
    icon: icons.import,
    color: colors.success,
    href: '/features/import/',
    capabilities: [
      'Auto-detect schema from files',
      'CSV, Excel, JSON, Parquet support',
      'Data validation and cleansing',
      'Incremental and bulk import modes',
      'External database connections',
    ],
  },
  {
    id: 'send',
    name: 'SQL Send',
    tagline: 'Database Messaging',
    description:
      'Unified email and SMS from database via SendGrid, Resend, Twilio. Transactional outbox pattern ensures reliable delivery.',
    icon: icons.send,
    color: colors.info,
    href: '/features/send/',
    capabilities: [
      'SendGrid, Resend, Twilio',
      'Transactional outbox pattern',
      'Template support',
      'Delivery tracking',
      'Native SQL/PG procedures',
    ],
  },
  {
    id: 'receive',
    name: 'SQL Receive',
    tagline: 'Secure Inbound Gateway',
    description:
      'Unified readers for files, APIs, and emails with malware scanning, SQL injection prevention, and PII detection.',
    icon: icons.receive,
    color: colors.cyan,
    href: '/features/receive/',
    capabilities: [
      'ClamAV/VirusTotal scanning',
      'SQL injection prevention',
      'PII detection (Presidio)',
      'File integrity validation',
      'SFTP, S3, API, email sources',
    ],
  },
  // COMPLIANCE & SECURITY
  {
    id: 'comply',
    name: 'SQL Comply',
    tagline: 'SOC2, HIPAA, GDPR & More',
    description:
      'Automated compliance checking at the database level. Scan actual data for PII/PHI with Presidio integration.',
    icon: icons.comply,
    color: colors.error,
    href: '/features/comply/',
    capabilities: [
      'SOC 2 Type I & II controls',
      'HIPAA PHI detection',
      'GDPR data classification',
      'PCI-DSS cardholder checks',
      'Presidio PII scanning',
    ],
  },
  {
    id: 'audit',
    name: 'SQL Audit',
    tagline: 'Tamper-Proof Audit Logs',
    description:
      'Blockchain-level tamper proofing for audit logs. Integrates with telemetry, AI severity scoring, and Presidio data leak detection.',
    icon: icons.audit,
    color: colors.error,
    href: '/features/audit/',
    capabilities: [
      'Blockchain-level tamper proofing',
      'AI-powered severity scoring',
      'Presidio data leak detection',
      'Telemetry integration',
      'SQL Monitor dashboard',
    ],
  },
  {
    id: 'encrypt',
    name: 'SQL Encrypt',
    tagline: 'Automated Key Management',
    description:
      'Zero-touch encryption management. Automated key rotation, vault integration, TDE, and Always Encrypted with no human intervention.',
    icon: icons.encrypt,
    color: colors.warning,
    href: '/features/encrypt/',
    capabilities: [
      'Automated key rotation',
      'Azure/AWS/HashiCorp vault',
      'TDE management',
      'Always Encrypted columns',
      'Compliance reporting',
    ],
  },
  {
    id: 'tenant',
    name: 'SQL Tenant',
    tagline: 'Multi-Tenant RLS',
    description:
      'Supabase-style multi-tenancy with Clerk integration. Standardized RLS patterns eliminate complexity while ensuring complete isolation.',
    icon: icons.tenant,
    color: colors.teal,
    href: '/features/tenant/',
    capabilities: [
      'Clerk authentication integration',
      'Standardized RLS policies',
      'Automatic tenant filtering',
      'Cross-platform (SQL + PG)',
      'Tenant onboarding automation',
    ],
    comingSoon: true,
  },
  {
    id: 'standardize',
    name: 'SQL Standardize',
    tagline: 'Naming Convention Enforcement',
    description:
      'Enforce consistent naming conventions across your database objects. Auto-fix violations and prevent drift from standards.',
    icon: icons.standardize,
    color: colors.lime,
    href: '/features/standardize/',
    capabilities: [
      'Convention rule engine',
      'Auto-fix suggestions',
      'CI/CD integration',
      'Custom rule definitions',
      'Migration script generation',
    ],
  },
  // AGENTIC AI
  {
    id: 'agent',
    name: 'SQL Agent',
    tagline: 'Autonomous AI DBA',
    description:
      'Agentic AI that autonomously performs DBA, analyst, auditor, and optimizer tasks based on context and compliance rather than rigid schedules.',
    icon: icons.agent,
    color: colors.primary,
    href: '/features/agent/',
    capabilities: [
      'AI-driven index management',
      'Proactive compliance detection',
      'Autonomous backup optimization',
      'Human-in-the-loop approval workflows',
      'Configurable autonomy levels',
    ],
  },
  {
    id: 'converse',
    name: 'SQL Converse',
    tagline: 'Bidirectional AI Bridge',
    description:
      'Two-way conversation between databases and AI using LangChain/LiteLLM. Table-based middleware with PII filtering ensures no data leaks.',
    icon: icons.converse,
    color: colors.primary,
    href: '/features/converse/',
    capabilities: [
      'LangChain/LangGraph integration',
      'LiteLLM model flexibility',
      'Table-based request/response',
      'Presidio PII filtering',
      'Multi-turn conversations',
    ],
    comingSoon: true,
  },
];

// Group modules by category for features page
export const moduleCategories = [
  {
    name: 'DBA Tools',
    description: 'Database administration, monitoring, performance, and replication',
    modules: ['monitor', 'orchestrate', 'optimize', 'centralize'],
  },
  {
    name: 'Migration Tools',
    description: 'Database migrations and platform conversions',
    modules: ['migrate', 'convert', 'containerize'],
  },
  {
    name: 'Developer Tools',
    description: 'Code generation, testing, versioning, comparison, CLI, and IDE integration',
    modules: ['version', 'code', 'writer', 'ssms', 'test', 'compare', 'cli'],
  },
  {
    name: 'Synthetic Data',
    description: 'Test data generation and anonymization',
    modules: ['anonymize', 'simulate'],
  },
  {
    name: 'Integration Tools',
    description: 'APIs, messaging, and data import/export',
    modules: ['connect', 'import', 'send', 'receive'],
  },
  {
    name: 'Compliance & Security',
    description: 'Regulatory compliance, encryption, auditing, and standards',
    modules: ['comply', 'audit', 'encrypt', 'tenant', 'standardize'],
  },
  {
    name: 'Agentic AI',
    description: 'Autonomous AI operations and conversational database interfaces',
    modules: ['agent', 'converse'],
  },
];
