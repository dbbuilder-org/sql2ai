import React from 'react';

export interface PanelProps {
  children: React.ReactNode;
  className?: string;
}

export function Panel({ children, className = '' }: PanelProps): JSX.Element {
  return (
    <div className={`bg-white dark:bg-slate-800 rounded-lg shadow-sm ${className}`}>
      {children}
    </div>
  );
}
