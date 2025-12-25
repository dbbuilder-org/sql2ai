import React from 'react';

export interface QueryResultsProps {
  columns: string[];
  rows: Record<string, unknown>[];
  loading?: boolean;
}

export function QueryResults({ columns, rows, loading }: QueryResultsProps): JSX.Element {
  if (loading) return <div>Loading...</div>;
  return (
    <table className="w-full text-sm">
      <thead><tr>{columns.map(c => <th key={c} className="text-left p-2 border-b">{c}</th>)}</tr></thead>
      <tbody>{rows.map((row, i) => <tr key={i}>{columns.map(c => <td key={c} className="p-2 border-b">{String(row[c])}</td>)}</tr>)}</tbody>
    </table>
  );
}

export function MetricsChart(): JSX.Element { return <div>MetricsChart (TODO)</div>; }
export function PerformanceGraph(): JSX.Element { return <div>PerformanceGraph (TODO)</div>; }
export function ConnectionForm(): JSX.Element { return <div>ConnectionForm (TODO)</div>; }
export function QueryBuilder(): JSX.Element { return <div>QueryBuilder (TODO)</div>; }
export function Toast(): JSX.Element { return <div>Toast (TODO)</div>; }
export function Loading(): JSX.Element { return <div className="animate-pulse">Loading...</div>; }
export function ErrorBoundary({ children }: { children: React.ReactNode }): JSX.Element { return <>{children}</>; }
