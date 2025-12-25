'use client';

import { useDatabaseDialect } from '../contexts/DatabaseDialectContext';

interface DatabaseDialectToggleProps {
  className?: string;
  variant?: 'default' | 'compact' | 'pill';
}

export function DatabaseDialectToggle({ className = '', variant = 'default' }: DatabaseDialectToggleProps) {
  const { dialect, setDialect } = useDatabaseDialect();

  if (variant === 'pill') {
    return (
      <div className={`inline-flex rounded-full bg-bg-surface border border-border-primary p-1 ${className}`}>
        <button
          onClick={() => setDialect('sqlserver')}
          className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
            dialect === 'sqlserver'
              ? 'bg-primary text-white'
              : 'text-text-muted hover:text-text-secondary'
          }`}
          aria-pressed={dialect === 'sqlserver'}
        >
          SQL Server
        </button>
        <button
          onClick={() => setDialect('postgresql')}
          className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
            dialect === 'postgresql'
              ? 'bg-primary text-white'
              : 'text-text-muted hover:text-text-secondary'
          }`}
          aria-pressed={dialect === 'postgresql'}
        >
          PostgreSQL
        </button>
      </div>
    );
  }

  if (variant === 'compact') {
    return (
      <button
        onClick={() => setDialect(dialect === 'sqlserver' ? 'postgresql' : 'sqlserver')}
        className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md bg-bg-surface border border-border-primary hover:border-border-secondary transition-colors text-sm ${className}`}
        title={`Switch to ${dialect === 'sqlserver' ? 'PostgreSQL' : 'SQL Server'} examples`}
      >
        {dialect === 'sqlserver' ? (
          <SqlServerIcon className="w-4 h-4" />
        ) : (
          <PostgresIcon className="w-4 h-4" />
        )}
        <span className="text-text-secondary">{dialect === 'sqlserver' ? 'T-SQL' : 'pgSQL'}</span>
      </button>
    );
  }

  // Default variant
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <span className="text-sm text-text-muted">Show examples in:</span>
      <div className="inline-flex rounded-lg bg-bg-surface border border-border-primary">
        <button
          onClick={() => setDialect('sqlserver')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-l-lg text-sm font-medium transition-all ${
            dialect === 'sqlserver'
              ? 'bg-[#CC2927]/10 text-[#CC2927] border-r border-[#CC2927]/30'
              : 'text-text-muted hover:text-text-secondary hover:bg-bg-primary'
          }`}
          aria-pressed={dialect === 'sqlserver'}
        >
          <SqlServerIcon className="w-4 h-4" />
          SQL Server
        </button>
        <button
          onClick={() => setDialect('postgresql')}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-r-lg text-sm font-medium transition-all ${
            dialect === 'postgresql'
              ? 'bg-[#336791]/10 text-[#336791]'
              : 'text-text-muted hover:text-text-secondary hover:bg-bg-primary'
          }`}
          aria-pressed={dialect === 'postgresql'}
        >
          <PostgresIcon className="w-4 h-4" />
          PostgreSQL
        </button>
      </div>
    </div>
  );
}

function SqlServerIcon({ className = '' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/>
      <path d="M12 6c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm0 10c-2.21 0-4-1.79-4-4s1.79-4 4-4 4 1.79 4 4-1.79 4-4 4z"/>
      <circle cx="12" cy="12" r="2"/>
    </svg>
  );
}

function PostgresIcon({ className = '' }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-6h2v6zm0-8h-2V7h2v2zm4 8h-2v-4h2v4zm0-6h-2V9h2v2zm4 6h-2v-2h2v2zm0-4h-2v-2h2v2z"/>
    </svg>
  );
}

// Export for use in Header
export function DatabaseDialectIndicator() {
  const { dialect } = useDatabaseDialect();

  return (
    <div className="flex items-center gap-1.5 text-xs text-text-muted">
      {dialect === 'sqlserver' ? (
        <>
          <SqlServerIcon className="w-3 h-3 text-[#CC2927]" />
          <span>T-SQL</span>
        </>
      ) : (
        <>
          <PostgresIcon className="w-3 h-3 text-[#336791]" />
          <span>PostgreSQL</span>
        </>
      )}
    </div>
  );
}
