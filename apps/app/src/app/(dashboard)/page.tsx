'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Database, Code2, Activity, Bot, ArrowRight, Plus } from 'lucide-react';
import Link from 'next/link';

const stats = [
  {
    name: 'Connected Databases',
    value: '3',
    description: '2 SQL Server, 1 PostgreSQL',
    icon: Database,
    href: '/connections',
  },
  {
    name: 'Queries Today',
    value: '127',
    description: '+23% from yesterday',
    icon: Code2,
    href: '/query',
  },
  {
    name: 'AI Tokens Used',
    value: '45.2K',
    description: 'of 100K monthly',
    icon: Bot,
    href: '/ai',
  },
  {
    name: 'Avg Response Time',
    value: '142ms',
    description: 'Last 24 hours',
    icon: Activity,
    href: '/monitoring',
  },
];

const recentQueries = [
  {
    id: '1',
    query: 'SELECT * FROM customers WHERE created_at > ...',
    connection: 'Production',
    duration: '45ms',
    time: '2 min ago',
  },
  {
    id: '2',
    query: 'UPDATE orders SET status = ...',
    connection: 'Production',
    duration: '12ms',
    time: '5 min ago',
  },
  {
    id: '3',
    query: 'SELECT COUNT(*) FROM products WHERE ...',
    connection: 'Analytics',
    duration: '234ms',
    time: '12 min ago',
  },
];

const quickActions = [
  { name: 'New Query', href: '/query', icon: Code2 },
  { name: 'Add Connection', href: '/connections/new', icon: Plus },
  { name: 'AI Assistant', href: '/ai', icon: Bot },
];

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="hover:border-primary/50 transition-colors cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">{stat.name}</CardTitle>
                <stat.icon className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">{stat.description}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
        {/* Recent Queries */}
        <Card className="col-span-4">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Queries</CardTitle>
                <CardDescription>Your latest database queries</CardDescription>
              </div>
              <Link href="/query/history">
                <Button variant="ghost" size="sm">
                  View all
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentQueries.map((query) => (
                <div
                  key={query.id}
                  className="flex items-center justify-between rounded-lg border p-3"
                >
                  <div className="space-y-1">
                    <p className="text-sm font-mono truncate max-w-md">{query.query}</p>
                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <span>{query.connection}</span>
                      <span>•</span>
                      <span>{query.duration}</span>
                      <span>•</span>
                      <span>{query.time}</span>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    Run again
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and shortcuts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {quickActions.map((action) => (
              <Link key={action.name} href={action.href}>
                <Button variant="outline" className="w-full justify-start gap-2">
                  <action.icon className="h-4 w-4" />
                  {action.name}
                </Button>
              </Link>
            ))}

            <div className="pt-4 border-t">
              <h4 className="text-sm font-medium mb-2">Connection Health</h4>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    Production
                  </span>
                  <span className="text-muted-foreground">Healthy</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-green-500" />
                    Analytics
                  </span>
                  <span className="text-muted-foreground">Healthy</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-yellow-500" />
                    Development
                  </span>
                  <span className="text-muted-foreground">High latency</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
