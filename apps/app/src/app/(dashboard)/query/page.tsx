'use client';

import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  Play,
  Sparkles,
  Download,
  Copy,
  Clock,
  Database,
  ChevronDown,
  Loader2,
  CheckCircle2,
} from 'lucide-react';

// Mock connections
const connections = [
  { id: '1', name: 'Production', type: 'sqlserver' },
  { id: '2', name: 'Analytics', type: 'postgresql' },
  { id: '3', name: 'Development', type: 'sqlserver' },
];

// Mock query results
const mockResults = {
  columns: ['CustomerID', 'Name', 'Email', 'CreatedAt', 'Status'],
  rows: [
    { CustomerID: 1, Name: 'John Doe', Email: 'john@example.com', CreatedAt: '2024-01-15', Status: 'Active' },
    { CustomerID: 2, Name: 'Jane Smith', Email: 'jane@example.com', CreatedAt: '2024-01-12', Status: 'Active' },
    { CustomerID: 3, Name: 'Bob Wilson', Email: 'bob@example.com', CreatedAt: '2024-01-10', Status: 'Inactive' },
    { CustomerID: 4, Name: 'Alice Brown', Email: 'alice@example.com', CreatedAt: '2024-01-08', Status: 'Active' },
    { CustomerID: 5, Name: 'Charlie Davis', Email: 'charlie@example.com', CreatedAt: '2024-01-05', Status: 'Active' },
  ],
  rowCount: 5,
  duration: 45,
};

export default function QueryPage() {
  const [selectedConnection, setSelectedConnection] = useState(connections[0]);
  const [query, setQuery] = useState('SELECT * FROM customers LIMIT 10;');
  const [aiPrompt, setAiPrompt] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [results, setResults] = useState<typeof mockResults | null>(null);
  const [showConnectionDropdown, setShowConnectionDropdown] = useState(false);

  const handleExecute = async () => {
    setIsExecuting(true);
    // Simulate query execution
    await new Promise((resolve) => setTimeout(resolve, 1500));
    setResults(mockResults);
    setIsExecuting(false);
  };

  const handleGenerate = async () => {
    if (!aiPrompt.trim()) return;
    setIsGenerating(true);
    // Simulate AI generation
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setQuery(`-- Generated from: "${aiPrompt}"
SELECT
  c.CustomerID,
  c.Name,
  c.Email,
  COUNT(o.OrderID) as OrderCount,
  SUM(o.TotalAmount) as TotalSpent
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
WHERE c.Status = 'Active'
GROUP BY c.CustomerID, c.Name, c.Email
HAVING COUNT(o.OrderID) > 0
ORDER BY TotalSpent DESC;`);
    setAiPrompt('');
    setIsGenerating(false);
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(query);
  };

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-2xl font-bold">Query Editor</h1>

          {/* Connection selector */}
          <div className="relative">
            <Button
              variant="outline"
              className="gap-2"
              onClick={() => setShowConnectionDropdown(!showConnectionDropdown)}
            >
              <Database className="h-4 w-4" />
              {selectedConnection.name}
              <ChevronDown className="h-4 w-4" />
            </Button>

            {showConnectionDropdown && (
              <div className="absolute top-full left-0 mt-1 w-48 rounded-md border bg-popover shadow-lg z-10">
                {connections.map((conn) => (
                  <button
                    key={conn.id}
                    className="w-full px-3 py-2 text-left text-sm hover:bg-accent flex items-center gap-2"
                    onClick={() => {
                      setSelectedConnection(conn);
                      setShowConnectionDropdown(false);
                    }}
                  >
                    <Database className={`h-4 w-4 ${conn.type === 'sqlserver' ? 'text-sqlserver' : 'text-postgresql'}`} />
                    {conn.name}
                    {conn.id === selectedConnection.id && (
                      <CheckCircle2 className="h-4 w-4 text-primary ml-auto" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleCopy}>
            <Copy className="h-4 w-4 mr-2" />
            Copy
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button onClick={handleExecute} disabled={isExecuting || !query.trim()}>
            {isExecuting ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {isExecuting ? 'Running...' : 'Run Query'}
          </Button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-3 gap-4 min-h-0">
        {/* Query Editor */}
        <div className="col-span-2 flex flex-col gap-4 min-h-0">
          {/* AI Prompt */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-primary" />
                <input
                  type="text"
                  placeholder="Describe what you want to query... (e.g., 'Show me top 10 customers by total orders')"
                  className="flex-1 bg-transparent border-none outline-none text-sm"
                  value={aiPrompt}
                  onChange={(e) => setAiPrompt(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleGenerate()}
                />
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={handleGenerate}
                  disabled={isGenerating || !aiPrompt.trim()}
                >
                  {isGenerating ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    'Generate'
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* SQL Editor */}
          <Card className="flex-1 min-h-0">
            <CardContent className="p-0 h-full">
              <textarea
                className="w-full h-full p-4 font-mono text-sm bg-transparent resize-none outline-none"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Enter your SQL query here..."
                spellCheck={false}
              />
            </CardContent>
          </Card>
        </div>

        {/* History & Saved Queries */}
        <Card className="min-h-0">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Query History</CardTitle>
          </CardHeader>
          <CardContent className="overflow-y-auto">
            <div className="space-y-2">
              {[
                'SELECT * FROM customers WHERE...',
                'UPDATE orders SET status = ...',
                'SELECT COUNT(*) FROM products...',
                'INSERT INTO logs VALUES...',
                'DELETE FROM temp_data WHERE...',
              ].map((q, i) => (
                <button
                  key={i}
                  className="w-full text-left p-2 rounded text-xs font-mono hover:bg-accent truncate"
                  onClick={() => setQuery(q)}
                >
                  {q}
                </button>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Results */}
      {results && (
        <Card className="max-h-[300px] overflow-hidden">
          <CardHeader className="py-3 px-4 border-b flex flex-row items-center justify-between">
            <div className="flex items-center gap-4">
              <CardTitle className="text-sm">Results</CardTitle>
              <span className="text-xs text-muted-foreground">
                {results.rowCount} rows
              </span>
              <span className="text-xs text-muted-foreground flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {results.duration}ms
              </span>
            </div>
          </CardHeader>
          <CardContent className="p-0 overflow-auto">
            <table className="w-full query-results-table">
              <thead className="bg-muted/50 sticky top-0">
                <tr>
                  {results.columns.map((col) => (
                    <th key={col} className="px-4 py-2 text-left text-xs font-medium">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.rows.map((row, i) => (
                  <tr key={i} className="border-t hover:bg-muted/30">
                    {results.columns.map((col) => (
                      <td key={col} className="px-4 py-2 text-xs">
                        {String(row[col as keyof typeof row])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
