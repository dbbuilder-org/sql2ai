'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Database,
  Table2,
  Eye,
  FileCode,
  Search,
  ChevronRight,
  ChevronDown,
  Key,
  Link2,
  RefreshCw,
  Copy,
} from 'lucide-react';

// Mock schema data
const mockSchema = {
  tables: [
    {
      name: 'customers',
      schema: 'dbo',
      rowCount: 15420,
      columns: [
        { name: 'CustomerID', type: 'int', nullable: false, isPK: true, isFK: false },
        { name: 'Email', type: 'nvarchar(255)', nullable: false, isPK: false, isFK: false },
        { name: 'Name', type: 'nvarchar(100)', nullable: true, isPK: false, isFK: false },
        { name: 'Status', type: 'nvarchar(20)', nullable: false, isPK: false, isFK: false },
        { name: 'CreatedAt', type: 'datetime2', nullable: false, isPK: false, isFK: false },
      ],
    },
    {
      name: 'orders',
      schema: 'dbo',
      rowCount: 89234,
      columns: [
        { name: 'OrderID', type: 'int', nullable: false, isPK: true, isFK: false },
        { name: 'CustomerID', type: 'int', nullable: false, isPK: false, isFK: true },
        { name: 'TotalAmount', type: 'decimal(18,2)', nullable: false, isPK: false, isFK: false },
        { name: 'Status', type: 'nvarchar(20)', nullable: false, isPK: false, isFK: false },
        { name: 'OrderDate', type: 'datetime2', nullable: false, isPK: false, isFK: false },
      ],
    },
    {
      name: 'products',
      schema: 'dbo',
      rowCount: 1234,
      columns: [
        { name: 'ProductID', type: 'int', nullable: false, isPK: true, isFK: false },
        { name: 'Name', type: 'nvarchar(200)', nullable: false, isPK: false, isFK: false },
        { name: 'Price', type: 'decimal(18,2)', nullable: false, isPK: false, isFK: false },
        { name: 'CategoryID', type: 'int', nullable: true, isPK: false, isFK: true },
      ],
    },
    {
      name: 'order_items',
      schema: 'dbo',
      rowCount: 234567,
      columns: [
        { name: 'OrderItemID', type: 'int', nullable: false, isPK: true, isFK: false },
        { name: 'OrderID', type: 'int', nullable: false, isPK: false, isFK: true },
        { name: 'ProductID', type: 'int', nullable: false, isPK: false, isFK: true },
        { name: 'Quantity', type: 'int', nullable: false, isPK: false, isFK: false },
        { name: 'UnitPrice', type: 'decimal(18,2)', nullable: false, isPK: false, isFK: false },
      ],
    },
  ],
  views: [
    { name: 'vw_CustomerOrders', schema: 'dbo' },
    { name: 'vw_ProductSales', schema: 'dbo' },
  ],
  procedures: [
    { name: 'sp_GetCustomerOrders', schema: 'dbo' },
    { name: 'sp_ProcessOrder', schema: 'dbo' },
    { name: 'sp_UpdateInventory', schema: 'dbo' },
  ],
};

type ObjectType = 'table' | 'view' | 'procedure';

interface SchemaObject {
  name: string;
  schema: string;
  type: ObjectType;
  rowCount?: number;
  columns?: Array<{
    name: string;
    type: string;
    nullable: boolean;
    isPK: boolean;
    isFK: boolean;
  }>;
}

export default function SchemaPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedTables, setExpandedTables] = useState<string[]>(['customers']);
  const [selectedObject, setSelectedObject] = useState<SchemaObject | null>(
    { ...mockSchema.tables[0], type: 'table' }
  );

  const toggleTable = (tableName: string) => {
    setExpandedTables((prev) =>
      prev.includes(tableName)
        ? prev.filter((t) => t !== tableName)
        : [...prev, tableName]
    );
  };

  const filteredTables = mockSchema.tables.filter((t) =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const filteredViews = mockSchema.views.filter((v) =>
    v.name.toLowerCase().includes(searchQuery.toLowerCase())
  );
  const filteredProcedures = mockSchema.procedures.filter((p) =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-4">
      {/* Schema Tree */}
      <Card className="w-80 flex flex-col min-h-0">
        <CardHeader className="pb-2">
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">Schema Explorer</CardTitle>
            <Button variant="ghost" size="icon" className="h-8 w-8">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search objects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-8 text-sm"
            />
          </div>
        </CardHeader>
        <CardContent className="flex-1 overflow-y-auto space-y-4">
          {/* Tables */}
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <Table2 className="h-4 w-4" />
              Tables ({filteredTables.length})
            </div>
            <div className="space-y-1">
              {filteredTables.map((table) => (
                <div key={table.name}>
                  <button
                    className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent ${
                      selectedObject?.name === table.name ? 'bg-accent' : ''
                    }`}
                    onClick={() => {
                      toggleTable(table.name);
                      setSelectedObject({ ...table, type: 'table' });
                    }}
                  >
                    {expandedTables.includes(table.name) ? (
                      <ChevronDown className="h-4 w-4" />
                    ) : (
                      <ChevronRight className="h-4 w-4" />
                    )}
                    <Table2 className="h-4 w-4 text-muted-foreground" />
                    <span className="truncate">{table.name}</span>
                    <span className="ml-auto text-xs text-muted-foreground">
                      {table.rowCount.toLocaleString()}
                    </span>
                  </button>
                  {expandedTables.includes(table.name) && (
                    <div className="ml-6 pl-4 border-l space-y-0.5 mt-1">
                      {table.columns.map((col) => (
                        <div
                          key={col.name}
                          className="flex items-center gap-2 px-2 py-1 text-xs text-muted-foreground"
                        >
                          {col.isPK && <Key className="h-3 w-3 text-yellow-500" />}
                          {col.isFK && <Link2 className="h-3 w-3 text-blue-500" />}
                          {!col.isPK && !col.isFK && <span className="w-3" />}
                          <span className="truncate">{col.name}</span>
                          <span className="ml-auto font-mono text-[10px]">{col.type}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Views */}
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <Eye className="h-4 w-4" />
              Views ({filteredViews.length})
            </div>
            <div className="space-y-1">
              {filteredViews.map((view) => (
                <button
                  key={view.name}
                  className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent ${
                    selectedObject?.name === view.name ? 'bg-accent' : ''
                  }`}
                  onClick={() => setSelectedObject({ ...view, type: 'view' })}
                >
                  <Eye className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{view.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Stored Procedures */}
          <div>
            <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground mb-2">
              <FileCode className="h-4 w-4" />
              Procedures ({filteredProcedures.length})
            </div>
            <div className="space-y-1">
              {filteredProcedures.map((proc) => (
                <button
                  key={proc.name}
                  className={`w-full flex items-center gap-2 px-2 py-1.5 rounded text-sm hover:bg-accent ${
                    selectedObject?.name === proc.name ? 'bg-accent' : ''
                  }`}
                  onClick={() => setSelectedObject({ ...proc, type: 'procedure' })}
                >
                  <FileCode className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{proc.name}</span>
                </button>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Object Details */}
      <Card className="flex-1 min-h-0 flex flex-col">
        {selectedObject ? (
          <>
            <CardHeader className="pb-2 border-b">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  {selectedObject.type === 'table' && <Table2 className="h-5 w-5" />}
                  {selectedObject.type === 'view' && <Eye className="h-5 w-5" />}
                  {selectedObject.type === 'procedure' && <FileCode className="h-5 w-5" />}
                  <div>
                    <CardTitle>{selectedObject.name}</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      {selectedObject.schema}.{selectedObject.name}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="sm">
                    <Copy className="h-4 w-4 mr-2" />
                    Copy DDL
                  </Button>
                  <Button size="sm">
                    Query
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-y-auto p-4">
              {selectedObject.type === 'table' && selectedObject.columns && (
                <div className="space-y-6">
                  {/* Stats */}
                  <div className="grid grid-cols-4 gap-4">
                    <div className="p-3 rounded-lg border">
                      <div className="text-2xl font-bold">
                        {selectedObject.rowCount?.toLocaleString()}
                      </div>
                      <div className="text-sm text-muted-foreground">Rows</div>
                    </div>
                    <div className="p-3 rounded-lg border">
                      <div className="text-2xl font-bold">
                        {selectedObject.columns.length}
                      </div>
                      <div className="text-sm text-muted-foreground">Columns</div>
                    </div>
                    <div className="p-3 rounded-lg border">
                      <div className="text-2xl font-bold">
                        {selectedObject.columns.filter((c) => c.isPK).length}
                      </div>
                      <div className="text-sm text-muted-foreground">Primary Keys</div>
                    </div>
                    <div className="p-3 rounded-lg border">
                      <div className="text-2xl font-bold">
                        {selectedObject.columns.filter((c) => c.isFK).length}
                      </div>
                      <div className="text-sm text-muted-foreground">Foreign Keys</div>
                    </div>
                  </div>

                  {/* Columns Table */}
                  <div>
                    <h3 className="text-sm font-medium mb-3">Columns</h3>
                    <table className="w-full text-sm">
                      <thead className="bg-muted/50">
                        <tr>
                          <th className="px-4 py-2 text-left font-medium">Name</th>
                          <th className="px-4 py-2 text-left font-medium">Type</th>
                          <th className="px-4 py-2 text-left font-medium">Nullable</th>
                          <th className="px-4 py-2 text-left font-medium">Key</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedObject.columns.map((col) => (
                          <tr key={col.name} className="border-t">
                            <td className="px-4 py-2 font-mono">{col.name}</td>
                            <td className="px-4 py-2 font-mono text-muted-foreground">
                              {col.type}
                            </td>
                            <td className="px-4 py-2">
                              {col.nullable ? 'Yes' : 'No'}
                            </td>
                            <td className="px-4 py-2">
                              {col.isPK && (
                                <span className="inline-flex items-center gap-1 text-yellow-600">
                                  <Key className="h-3 w-3" /> PK
                                </span>
                              )}
                              {col.isFK && (
                                <span className="inline-flex items-center gap-1 text-blue-600">
                                  <Link2 className="h-3 w-3" /> FK
                                </span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {selectedObject.type === 'view' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg border bg-muted/30">
                    <p className="text-sm text-muted-foreground mb-2">View Definition</p>
                    <pre className="text-sm font-mono whitespace-pre-wrap">
{`CREATE VIEW ${selectedObject.schema}.${selectedObject.name}
AS
SELECT
    c.CustomerID,
    c.Name,
    COUNT(o.OrderID) as OrderCount,
    SUM(o.TotalAmount) as TotalSpent
FROM Customers c
LEFT JOIN Orders o ON c.CustomerID = o.CustomerID
GROUP BY c.CustomerID, c.Name;`}
                    </pre>
                  </div>
                </div>
              )}

              {selectedObject.type === 'procedure' && (
                <div className="space-y-4">
                  <div className="p-4 rounded-lg border bg-muted/30">
                    <p className="text-sm text-muted-foreground mb-2">Procedure Definition</p>
                    <pre className="text-sm font-mono whitespace-pre-wrap">
{`CREATE PROCEDURE ${selectedObject.schema}.${selectedObject.name}
    @CustomerID INT,
    @StartDate DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        o.OrderID,
        o.OrderDate,
        o.TotalAmount,
        o.Status
    FROM Orders o
    WHERE o.CustomerID = @CustomerID
      AND (@StartDate IS NULL OR o.OrderDate >= @StartDate)
    ORDER BY o.OrderDate DESC;
END;`}
                    </pre>
                  </div>
                </div>
              )}
            </CardContent>
          </>
        ) : (
          <CardContent className="flex-1 flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <Database className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>Select an object to view details</p>
            </div>
          </CardContent>
        )}
      </Card>
    </div>
  );
}
