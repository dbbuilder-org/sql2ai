'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ArrowLeft, Database, CheckCircle2, Loader2, XCircle } from 'lucide-react';

type DatabaseType = 'sqlserver' | 'postgresql';

interface ConnectionForm {
  name: string;
  type: DatabaseType;
  host: string;
  port: string;
  database: string;
  username: string;
  password: string;
  ssl: boolean;
}

const initialForm: ConnectionForm = {
  name: '',
  type: 'sqlserver',
  host: '',
  port: '',
  database: '',
  username: '',
  password: '',
  ssl: false,
};

const defaultPorts: Record<DatabaseType, string> = {
  sqlserver: '1433',
  postgresql: '5432',
};

export default function NewConnectionPage() {
  const router = useRouter();
  const [form, setForm] = useState<ConnectionForm>(initialForm);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<'success' | 'error' | null>(null);
  const [saving, setSaving] = useState(false);

  const handleTypeChange = (type: DatabaseType) => {
    setForm((prev) => ({
      ...prev,
      type,
      port: prev.port || defaultPorts[type],
    }));
    setTestResult(null);
  };

  const handleInputChange = (field: keyof ConnectionForm, value: string | boolean) => {
    setForm((prev) => ({ ...prev, [field]: value }));
    setTestResult(null);
  };

  const handleTest = async () => {
    setTesting(true);
    setTestResult(null);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));

    // Mock result
    setTestResult(Math.random() > 0.3 ? 'success' : 'error');
    setTesting(false);
  };

  const handleSave = async () => {
    setSaving(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 1000));

    router.push('/connections');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link href="/connections">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-4 w-4" />
          </Button>
        </Link>
        <div>
          <h1 className="text-2xl font-bold">Add Connection</h1>
          <p className="text-muted-foreground">Connect to a new database</p>
        </div>
      </div>

      {/* Database Type Selection */}
      <Card>
        <CardHeader>
          <CardTitle>Database Type</CardTitle>
          <CardDescription>Select the type of database you want to connect to</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => handleTypeChange('sqlserver')}
              className={`p-4 rounded-lg border-2 transition-colors ${
                form.type === 'sqlserver'
                  ? 'border-sqlserver bg-sqlserver/5'
                  : 'border-border hover:border-sqlserver/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-sqlserver/10 flex items-center justify-center">
                  <Database className="h-5 w-5 text-sqlserver" />
                </div>
                <div className="text-left">
                  <div className="font-medium">SQL Server</div>
                  <div className="text-xs text-muted-foreground">Microsoft SQL Server</div>
                </div>
              </div>
            </button>

            <button
              onClick={() => handleTypeChange('postgresql')}
              className={`p-4 rounded-lg border-2 transition-colors ${
                form.type === 'postgresql'
                  ? 'border-postgresql bg-postgresql/5'
                  : 'border-border hover:border-postgresql/50'
              }`}
            >
              <div className="flex items-center gap-3">
                <div className="h-10 w-10 rounded-lg bg-postgresql/10 flex items-center justify-center">
                  <Database className="h-5 w-5 text-postgresql" />
                </div>
                <div className="text-left">
                  <div className="font-medium">PostgreSQL</div>
                  <div className="text-xs text-muted-foreground">PostgreSQL Database</div>
                </div>
              </div>
            </button>
          </div>
        </CardContent>
      </Card>

      {/* Connection Details */}
      <Card>
        <CardHeader>
          <CardTitle>Connection Details</CardTitle>
          <CardDescription>Enter your database connection information</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Connection Name</label>
            <Input
              placeholder="e.g., Production Database"
              value={form.name}
              onChange={(e) => handleInputChange('name', e.target.value)}
            />
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div className="col-span-2 space-y-2">
              <label className="text-sm font-medium">Host</label>
              <Input
                placeholder="e.g., db.example.com"
                value={form.host}
                onChange={(e) => handleInputChange('host', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Port</label>
              <Input
                placeholder={defaultPorts[form.type]}
                value={form.port}
                onChange={(e) => handleInputChange('port', e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Database</label>
            <Input
              placeholder="e.g., my_database"
              value={form.database}
              onChange={(e) => handleInputChange('database', e.target.value)}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Username</label>
              <Input
                placeholder="Username"
                value={form.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Password</label>
              <Input
                type="password"
                placeholder="Password"
                value={form.password}
                onChange={(e) => handleInputChange('password', e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="ssl"
              checked={form.ssl}
              onChange={(e) => handleInputChange('ssl', e.target.checked)}
              className="h-4 w-4 rounded border-input"
            />
            <label htmlFor="ssl" className="text-sm">
              Use SSL/TLS connection
            </label>
          </div>
        </CardContent>
      </Card>

      {/* Test Connection */}
      <Card>
        <CardHeader>
          <CardTitle>Test Connection</CardTitle>
          <CardDescription>Verify your connection settings before saving</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={handleTest}
              disabled={testing || !form.host || !form.database}
            >
              {testing ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Testing...
                </>
              ) : (
                'Test Connection'
              )}
            </Button>

            {testResult === 'success' && (
              <div className="flex items-center gap-2 text-green-600">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-sm">Connection successful!</span>
              </div>
            )}

            {testResult === 'error' && (
              <div className="flex items-center gap-2 text-red-600">
                <XCircle className="h-4 w-4" />
                <span className="text-sm">Connection failed. Check your settings.</span>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-end gap-4">
        <Link href="/connections">
          <Button variant="outline">Cancel</Button>
        </Link>
        <Button
          onClick={handleSave}
          disabled={saving || !form.name || !form.host || !form.database}
        >
          {saving ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Saving...
            </>
          ) : (
            'Save Connection'
          )}
        </Button>
      </div>
    </div>
  );
}
