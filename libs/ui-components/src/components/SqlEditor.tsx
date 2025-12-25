import React from 'react';

export interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  dialect?: 'postgresql' | 'sqlserver';
  readOnly?: boolean;
  height?: string;
}

export function SqlEditor({ value, onChange, readOnly = false, height = '300px' }: SqlEditorProps): JSX.Element {
  // TODO: Integrate Monaco or CodeMirror
  return (
    <textarea
      value={value}
      onChange={(e) => onChange(e.target.value)}
      readOnly={readOnly}
      style={{ height }}
      className="w-full font-mono text-sm p-4 bg-slate-900 text-slate-100 rounded-lg border border-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
    />
  );
}
