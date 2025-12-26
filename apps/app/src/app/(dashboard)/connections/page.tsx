'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Database,
  Plus,
  Search,
  MoreVertical,
  CheckCircle2,
  XCircle,
  Clock,
  Trash2,
  Edit,
  RefreshCw,
} from 'lucide-react';

// Mock data - will be replaced with API calls
const connections = [
  {
    id: '1',
    name: 'Production',
    type: 'sqlserver',
    host: 'prod-db.example.com',
    database: 'app_production',
    status: 'connected',
    lastUsed: '2 minutes ago',
    queriesCount: 1247,
  },
  {
    id: '2',
    name: 'Analytics',
    type: 'postgresql',
    host: 'analytics.example.com',
    database: 'analytics',
    status: 'connected',
    lastUsed: '15 minutes ago',
    queriesCount: 432,
  },
  {
    id: '3',
    name: 'Development',
    type: 'sqlserver',
    host: 'localhost',
    database: 'app_dev',
    status: 'error',
    lastUsed: '1 hour ago',
    queriesCount: 89,
  },
];

function getStatusIcon(status: string) {
  switch (status) {
    case 'connected':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'error':
      return <XCircle className="h-4 w-4 text-red-500" />;
    default:
      return <Clock className="h-4 w-4 text-yellow-500" />;
  }
}

function getTypeIcon(type: string) {
  const color = type === 'sqlserver' ? 'text-sqlserver' : 'text-postgresql';
  return (
    <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${type === 'sqlserver' ? 'bg-sqlserver/10' : 'bg-postgresql/10'}`}>
      <Database className={`h-5 w-5 ${color}`} />
    </div>
  );
}

export default function ConnectionsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const filteredConnections = connections.filter(
    (conn) =>
      conn.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      conn.host.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Connections</h1>
          <p className="text-muted-foreground">Manage your database connections</p>
        </div>
        <Link href="/connections/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            Add Connection
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search connections..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Connections Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredConnections.map((connection) => (
          <Card key={connection.id} className="hover:border-primary/50 transition-colors">
            <CardHeader className="flex flex-row items-start justify-between space-y-0">
              <div className="flex items-center gap-3">
                {getTypeIcon(connection.type)}
                <div>
                  <CardTitle className="text-base">{connection.name}</CardTitle>
                  <CardDescription className="text-xs">
                    {connection.type === 'sqlserver' ? 'SQL Server' : 'PostgreSQL'}
                  </CardDescription>
                </div>
              </div>
              <div className="flex items-center gap-1">
                {getStatusIcon(connection.status)}
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="text-sm">
                  <span className="text-muted-foreground">Host: </span>
                  <span className="font-mono">{connection.host}</span>
                </div>
                <div className="text-sm">
                  <span className="text-muted-foreground">Database: </span>
                  <span className="font-mono">{connection.database}</span>
                </div>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Last used: {connection.lastUsed}</span>
                  <span>{connection.queriesCount} queries</span>
                </div>

                <div className="flex items-center gap-2 pt-2 border-t">
                  <Link href={`/query?connection=${connection.id}`} className="flex-1">
                    <Button variant="outline" size="sm" className="w-full">
                      Query
                    </Button>
                  </Link>
                  <Link href={`/schema?connection=${connection.id}`} className="flex-1">
                    <Button variant="outline" size="sm" className="w-full">
                      Schema
                    </Button>
                  </Link>
                  <Button variant="ghost" size="icon" className="h-8 w-8">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}

        {/* Empty State */}
        {filteredConnections.length === 0 && (
          <Card className="col-span-full">
            <CardContent className="flex flex-col items-center justify-center py-12">
              <Database className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No connections found</h3>
              <p className="text-muted-foreground text-center mb-4">
                {searchQuery
                  ? 'No connections match your search query.'
                  : 'Get started by adding your first database connection.'}
              </p>
              {!searchQuery && (
                <Link href="/connections/new">
                  <Button>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Connection
                  </Button>
                </Link>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
