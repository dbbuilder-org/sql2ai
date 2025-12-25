import React from 'react';

export interface LayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
  header?: React.ReactNode;
}

export function Layout({ children, sidebar, header }: LayoutProps): JSX.Element {
  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900">
      {sidebar && (
        <aside className="w-64 border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
          {sidebar}
        </aside>
      )}
      <div className="flex-1 flex flex-col overflow-hidden">
        {header && (
          <header className="h-16 border-b border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
            {header}
          </header>
        )}
        <main className="flex-1 overflow-auto p-6">{children}</main>
      </div>
    </div>
  );
}
