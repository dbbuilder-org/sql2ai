'use client';

import { useDatabaseDialect, DatabaseDialect } from '../contexts/DatabaseDialectContext';
import { DatabaseDialectToggle } from './DatabaseDialectToggle';

interface CodeExampleProps {
  sqlserver: string;
  postgresql: string;
  title?: string;
  showToggle?: boolean;
  className?: string;
}

/**
 * A code example component that shows SQL Server or PostgreSQL code
 * based on the user's dialect preference.
 *
 * Usage:
 * ```tsx
 * <CodeExample
 *   title="Create Table"
 *   sqlserver={`CREATE TABLE Customers (
 *     CustomerId INT IDENTITY(1,1) PRIMARY KEY,
 *     Name NVARCHAR(100) NOT NULL
 *   )`}
 *   postgresql={`CREATE TABLE customers (
 *     customer_id SERIAL PRIMARY KEY,
 *     name VARCHAR(100) NOT NULL
 *   )`}
 * />
 * ```
 */
export function CodeExample({
  sqlserver,
  postgresql,
  title,
  showToggle = true,
  className = ''
}: CodeExampleProps) {
  const { dialect } = useDatabaseDialect();

  const code = dialect === 'sqlserver' ? sqlserver : postgresql;

  return (
    <div className={`rounded-xl border border-border-primary overflow-hidden ${className}`}>
      {(title || showToggle) && (
        <div className="flex items-center justify-between px-4 py-2 bg-bg-surface border-b border-border-primary">
          {title && (
            <span className="text-sm font-medium text-text-secondary">{title}</span>
          )}
          {showToggle && (
            <DatabaseDialectToggle variant="compact" />
          )}
        </div>
      )}
      <pre className="bg-bg-primary p-4 text-sm overflow-x-auto">
        <code className="text-text-secondary">{code}</code>
      </pre>
    </div>
  );
}

interface CodeBlockProps {
  children: {
    sqlserver: React.ReactNode;
    postgresql: React.ReactNode;
  };
  className?: string;
}

/**
 * A component that renders different content based on dialect.
 * Useful for more complex examples with JSX.
 *
 * Usage:
 * ```tsx
 * <CodeBlock>
 *   {{
 *     sqlserver: <div>SQL Server specific content</div>,
 *     postgresql: <div>PostgreSQL specific content</div>
 *   }}
 * </CodeBlock>
 * ```
 */
export function CodeBlock({ children, className = '' }: CodeBlockProps) {
  const { dialect } = useDatabaseDialect();

  return (
    <div className={className}>
      {dialect === 'sqlserver' ? children.sqlserver : children.postgresql}
    </div>
  );
}

interface DialectContentProps {
  dialect: DatabaseDialect;
  children: React.ReactNode;
}

/**
 * Only renders children if the current dialect matches.
 *
 * Usage:
 * ```tsx
 * <DialectContent dialect="sqlserver">
 *   <p>This only shows for SQL Server users</p>
 * </DialectContent>
 * ```
 */
export function DialectContent({ dialect: targetDialect, children }: DialectContentProps) {
  const { dialect } = useDatabaseDialect();

  if (dialect !== targetDialect) return null;

  return <>{children}</>;
}

/**
 * Shows a badge indicating the current dialect
 */
export function DialectBadge({ className = '' }: { className?: string }) {
  const { dialect, dialectLabel } = useDatabaseDialect();

  const colors = dialect === 'sqlserver'
    ? 'bg-[#CC2927]/10 text-[#CC2927] border-[#CC2927]/30'
    : 'bg-[#336791]/10 text-[#336791] border-[#336791]/30';

  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded border text-xs font-medium ${colors} ${className}`}>
      {dialect === 'sqlserver' ? '🔷' : '🐘'}
      {dialectLabel}
    </span>
  );
}
