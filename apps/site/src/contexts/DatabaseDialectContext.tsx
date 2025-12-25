'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

export type DatabaseDialect = 'sqlserver' | 'postgresql';

interface DatabaseDialectContextType {
  dialect: DatabaseDialect;
  setDialect: (dialect: DatabaseDialect) => void;
  toggle: () => void;
  dialectLabel: string;
  dialectShort: string;
}

const DatabaseDialectContext = createContext<DatabaseDialectContextType | undefined>(undefined);

const STORAGE_KEY = 'sql2ai-dialect';

// Detect dialect from URL parameters (for marketing campaigns)
function detectDialectFromURL(): DatabaseDialect | null {
  if (typeof window === 'undefined') return null;

  const params = new URLSearchParams(window.location.search);
  const source = params.get('source') || params.get('db') || params.get('dialect');

  if (source) {
    const lowerSource = source.toLowerCase();
    if (lowerSource.includes('postgres') || lowerSource === 'pg' || lowerSource === 'pgsql') {
      return 'postgresql';
    }
    if (lowerSource.includes('sqlserver') || lowerSource === 'mssql' || lowerSource === 'tsql') {
      return 'sqlserver';
    }
  }

  return null;
}

// Get stored preference
function getStoredDialect(): DatabaseDialect | null {
  if (typeof window === 'undefined') return null;
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === 'sqlserver' || stored === 'postgresql') {
    return stored;
  }
  return null;
}

export function DatabaseDialectProvider({ children }: { children: React.ReactNode }) {
  // Default to SQL Server (most common enterprise use case)
  const [dialect, setDialectState] = useState<DatabaseDialect>('sqlserver');
  const [isHydrated, setIsHydrated] = useState(false);

  useEffect(() => {
    // First check URL params (marketing source)
    const urlDialect = detectDialectFromURL();
    if (urlDialect) {
      setDialectState(urlDialect);
      localStorage.setItem(STORAGE_KEY, urlDialect);
      setIsHydrated(true);
      return;
    }

    // Then check localStorage
    const storedDialect = getStoredDialect();
    if (storedDialect) {
      setDialectState(storedDialect);
    }

    setIsHydrated(true);
  }, []);

  const setDialect = useCallback((newDialect: DatabaseDialect) => {
    setDialectState(newDialect);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, newDialect);
    }
  }, []);

  const toggle = useCallback(() => {
    setDialect(dialect === 'sqlserver' ? 'postgresql' : 'sqlserver');
  }, [dialect, setDialect]);

  const dialectLabel = dialect === 'sqlserver' ? 'SQL Server' : 'PostgreSQL';
  const dialectShort = dialect === 'sqlserver' ? 'T-SQL' : 'PL/pgSQL';

  // Prevent flash of wrong content during SSR
  if (!isHydrated) {
    return (
      <DatabaseDialectContext.Provider
        value={{
          dialect: 'sqlserver',
          setDialect: () => {},
          toggle: () => {},
          dialectLabel: 'SQL Server',
          dialectShort: 'T-SQL',
        }}
      >
        {children}
      </DatabaseDialectContext.Provider>
    );
  }

  return (
    <DatabaseDialectContext.Provider
      value={{
        dialect,
        setDialect,
        toggle,
        dialectLabel,
        dialectShort,
      }}
    >
      {children}
    </DatabaseDialectContext.Provider>
  );
}

export function useDatabaseDialect() {
  const context = useContext(DatabaseDialectContext);
  if (context === undefined) {
    throw new Error('useDatabaseDialect must be used within a DatabaseDialectProvider');
  }
  return context;
}
