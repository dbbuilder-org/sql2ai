export default function DashboardPage(): JSX.Element {
  return (
    <main className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">SQL2.AI Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400">
          AI-Driven Database Development Platform
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <DashboardCard
          title="Schema Analyzer"
          description="Analyze and compare database schemas across platforms"
          href="/schemas"
        />
        <DashboardCard
          title="Query Optimizer"
          description="AI-powered query optimization suggestions"
          href="/queries"
        />
        <DashboardCard
          title="Migration Engine"
          description="Generate and manage database migrations"
          href="/migrations"
        />
        <DashboardCard
          title="Telemetry"
          description="Monitor query performance and patterns"
          href="/telemetry"
        />
        <DashboardCard
          title="Connections"
          description="Manage database connections"
          href="/connections"
        />
        <DashboardCard
          title="Settings"
          description="Configure your SQL2.AI workspace"
          href="/settings"
        />
      </section>
    </main>
  );
}

interface DashboardCardProps {
  title: string;
  description: string;
  href: string;
}

function DashboardCard({ title, description, href }: DashboardCardProps): JSX.Element {
  return (
    <a
      href={href}
      className="block p-6 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
    >
      <h2 className="text-xl font-semibold mb-2">{title}</h2>
      <p className="text-gray-600 dark:text-gray-400">{description}</p>
    </a>
  );
}
