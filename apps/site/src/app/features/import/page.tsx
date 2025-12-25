import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'SQL Import - Intelligent Data Ingestion | SQL2.AI',
  description:
    'Smart data import from CSV, Excel, JSON, and external databases with automatic schema detection, validation, and transformation.',
};

export default function ImportPage() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="py-20 md:py-32 bg-gradient-to-b from-bg-surface to-bg-primary">
        <div className="container">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-success/10 border border-success/30 text-success mb-6">
              <span className="text-sm font-medium">Integration Tools</span>
            </div>
            <h1 className="text-h1 mb-6">
              SQL <span className="gradient-text">Import</span>
            </h1>
            <p className="text-xl text-text-secondary mb-8 max-w-2xl mx-auto">
              Smart data import from CSV, Excel, JSON, and external databases with automatic schema
              detection, validation, and transformation.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/contact" className="btn-primary">
                Get Started
              </Link>
              <Link href="/docs/import" className="btn-secondary">
                View Documentation
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-5xl mx-auto">
            <h2 className="text-h2 text-center mb-12">Import Workflow</h2>
            <div className="card p-8 bg-bg-surface">
              <pre className="text-sm text-text-secondary overflow-x-auto font-mono">
{`┌─────────────────────────────────────────────────────────────────┐
│                    SQL IMPORT WORKFLOW                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  SOURCE  │ →  │  DETECT  │ →  │ VALIDATE │ →  │  IMPORT  │  │
│  │   DATA   │    │  SCHEMA  │    │   DATA   │    │  TO DB   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │              │                │               │         │
│       ▼              ▼                ▼               ▼         │
│  • CSV, Excel   • Column types   • Type checks    • Bulk or    │
│  • JSON, XML    • Nullable       • FK validation    incremental│
│  • Parquet      • Constraints    • Duplicate       • Logging   │
│  • External DB  • FK relations     detection      • Rollback   │
│                                                                  │
├─────────────────────────────────────────────────────────────────┤
│  EXAMPLE: Import customers.csv                                   │
│  ──────────────────────────────────────────────────────────────│
│                                                                  │
│  Source: customers.csv (15,000 rows)                            │
│                                                                  │
│  Detected Schema:                                                │
│  ┌─────────────┬──────────────┬──────────┬───────────────┐      │
│  │ Column      │ Detected Type│ Nullable │ Sample        │      │
│  ├─────────────┼──────────────┼──────────┼───────────────┤      │
│  │ customer_id │ INT          │ No       │ 1001          │      │
│  │ email       │ VARCHAR(255) │ No       │ john@acme.com │      │
│  │ name        │ NVARCHAR(100)│ No       │ John Smith    │      │
│  │ created_at  │ DATETIME     │ No       │ 2024-01-15    │      │
│  │ tier        │ VARCHAR(20)  │ Yes      │ premium       │      │
│  └─────────────┴──────────────┴──────────┴───────────────┘      │
│                                                                  │
│  Validation Results:                                             │
│  ✓ 14,987 rows valid                                            │
│  ⚠ 13 rows with invalid email format → Quarantine               │
│  ✓ 0 duplicate customer_ids                                     │
│  ✓ FK check passed (tier → tiers.name)                          │
│                                                                  │
│  [Import Valid Rows] [Review Quarantine] [Edit Mappings]        │
└─────────────────────────────────────────────────────────────────┘`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Supported Sources */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <h2 className="text-h2 text-center mb-12">Supported Data Sources</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            {[
              { name: 'CSV', icon: '📄', desc: 'Comma/tab delimited' },
              { name: 'Excel', icon: '📊', desc: 'XLSX, XLS files' },
              { name: 'JSON', icon: '🔤', desc: 'Nested structures' },
              { name: 'Parquet', icon: '📦', desc: 'Columnar format' },
              { name: 'SQL Server', icon: '🗄️', desc: 'Direct connection' },
              { name: 'PostgreSQL', icon: '🐘', desc: 'Direct connection' },
              { name: 'MySQL', icon: '🐬', desc: 'Direct connection' },
              { name: 'APIs', icon: '🌐', desc: 'REST endpoints' },
            ].map((source) => (
              <div key={source.name} className="card p-6 text-center">
                <div className="text-3xl mb-2">{source.icon}</div>
                <div className="font-medium text-text-primary">{source.name}</div>
                <div className="text-xs text-text-muted">{source.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Key Features */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <h2 className="text-h2 text-center mb-12">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                title: 'Auto Schema Detection',
                description:
                  'AI-powered column type detection from file contents. Automatically infers data types, nullability, and constraints.',
                icon: '🔍',
              },
              {
                title: 'Data Validation',
                description:
                  'Validate data types, check foreign key relationships, detect duplicates, and enforce business rules before import.',
                icon: '✅',
              },
              {
                title: 'Transformation Rules',
                description:
                  'Apply transformations during import: trim whitespace, normalize case, parse dates, map values, and more.',
                icon: '🔄',
              },
              {
                title: 'Incremental Import',
                description:
                  'Import only new or changed records. Track last import position for efficient delta processing.',
                icon: '📈',
              },
              {
                title: 'Error Quarantine',
                description:
                  'Invalid rows are quarantined for review rather than failing the entire import. Fix and retry problematic records.',
                icon: '🚫',
              },
              {
                title: 'Audit Trail',
                description:
                  'Full logging of import operations. Track who imported what, when, and from where.',
                icon: '📋',
              },
            ].map((feature) => (
              <div key={feature.title} className="card p-6">
                <div className="text-3xl mb-4">{feature.icon}</div>
                <h3 className="text-h5 mb-2">{feature.title}</h3>
                <p className="text-text-secondary text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CLI Example */}
      <section className="py-20 bg-bg-surface">
        <div className="container">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-center mb-8">CLI Usage</h2>
            <div className="card p-6 bg-bg-primary">
              <pre className="text-sm text-text-secondary overflow-x-auto">
{`# Detect schema from CSV file
sql2ai import detect customers.csv

# Import with auto-detected schema
sql2ai import run customers.csv --table Customers

# Import with validation and error handling
sql2ai import run orders.xlsx \\
  --table Orders \\
  --validate-fk \\
  --quarantine-errors \\
  --on-duplicate update

# Import from external database
sql2ai import database \\
  --source "postgres://legacy-db/customers" \\
  --target "sqlserver://new-db/Customers" \\
  --incremental

# Schedule recurring import
sql2ai import schedule \\
  --source s3://bucket/daily-export.csv \\
  --table DailyImport \\
  --cron "0 2 * * *"`}
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 bg-bg-primary">
        <div className="container">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-h2 mb-6">Streamline Your Data Imports</h2>
            <p className="text-text-secondary mb-8">
              Stop wrestling with data imports. Let SQL Import handle detection, validation, and transformation.
            </p>
            <Link href="/contact" className="btn-primary">
              Request Demo
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
