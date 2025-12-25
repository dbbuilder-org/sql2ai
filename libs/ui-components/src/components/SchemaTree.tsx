import React from 'react';

export interface SchemaTreeProps {
  schema: unknown;
  onSelect?: (item: { type: string; name: string }) => void;
}

export function SchemaTree({ onSelect }: SchemaTreeProps): JSX.Element {
  return <div className="text-sm" onClick={() => onSelect?.({ type: 'table', name: 'example' })}>Schema Tree (TODO)</div>;
}
