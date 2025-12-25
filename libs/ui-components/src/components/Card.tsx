import React from 'react';

export interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}

export function Card({ title, children, className = '', actions }: CardProps): JSX.Element {
  return (
    <div className={`bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 ${className}`}>
      {(title || actions) && (
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
          {title && <h3 className="font-semibold text-slate-900 dark:text-white">{title}</h3>}
          {actions && <div className="flex gap-2">{actions}</div>}
        </div>
      )}
      <div className="p-4">{children}</div>
    </div>
  );
}
