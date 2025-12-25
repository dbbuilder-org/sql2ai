import React from 'react';

export interface ExecutionPlanProps {
  plan: unknown;
  dialect: 'postgresql' | 'sqlserver';
}

export function ExecutionPlan({ plan }: ExecutionPlanProps): JSX.Element {
  return (
    <div className="p-4 bg-slate-50 dark:bg-slate-900 rounded-lg">
      <pre className="text-xs font-mono text-slate-600 dark:text-slate-400 overflow-auto">
        {JSON.stringify(plan, null, 2)}
      </pre>
    </div>
  );
}
