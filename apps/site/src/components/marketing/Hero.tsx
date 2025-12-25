import Link from 'next/link';

export function Hero(): JSX.Element {
  return (
    <section className="relative pt-32 pb-20 md:pt-40 md:pb-32 overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 bg-grid-pattern opacity-30" />
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-bg-base/50 to-bg-base" />

      {/* Glow effect */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-primary/10 rounded-full blur-3xl" />

      <div className="container-wide relative">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-bg-surface border border-border mb-8 animate-fade-in">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
            <span className="text-small text-text-secondary">
              Now with Claude MCP integration
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-semibold text-text-primary mb-6 text-balance animate-slide-up">
            Database Development,
            <br />
            <span className="gradient-text">Powered by AI</span>
          </h1>

          {/* Subheadline */}
          <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            The complete lifecycle platform for SQL Server and PostgreSQL—from schema analysis to deployment.
            AI that understands your database the way you do.
          </p>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Link href="/signup" className="btn-primary text-base px-8 py-4">
              Start Free Trial
            </Link>
            <Link href="/demo" className="btn-secondary text-base px-8 py-4">
              Watch Demo
            </Link>
          </div>

          {/* Trust indicators */}
          <div className="mt-12 pt-8 border-t border-border-subtle animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <p className="text-small text-text-muted mb-4">Works with your database</p>
            <div className="flex items-center justify-center gap-8">
              <div className="flex items-center gap-2">
                <PostgreSQLIcon className="w-8 h-8" />
                <span className="text-text-secondary font-medium">PostgreSQL</span>
              </div>
              <div className="flex items-center gap-2">
                <SQLServerIcon className="w-8 h-8" />
                <span className="text-text-secondary font-medium">SQL Server</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function PostgreSQLIcon({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none">
      <path
        d="M23.56 14.58c-.48.04-.85.08-1.11.18-.66.25-1.08.8-1.08 1.42 0 .44.21.84.58 1.1.45.31 1.1.43 2.06.36.8-.06 1.44-.27 1.87-.62.44-.35.66-.84.66-1.42 0-.52-.2-.94-.59-1.23-.39-.29-.97-.44-1.76-.44-.24 0-.44.01-.63.05v.6zm-4.25-3.8c-.73 0-1.33.1-1.79.32-.46.22-.82.52-1.08.9-.26.38-.44.82-.54 1.32-.1.5-.15 1.03-.15 1.6 0 .8.08 1.48.24 2.04.16.56.4 1.02.72 1.38.32.36.73.63 1.23.8.5.18 1.08.27 1.75.27.48 0 .94-.04 1.38-.13v-8.36c-.54-.1-1.12-.14-1.76-.14z"
        fill="#336791"
      />
      <ellipse cx="16" cy="16" rx="14" ry="14" stroke="#336791" strokeWidth="2" fill="none" />
    </svg>
  );
}

function SQLServerIcon({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} viewBox="0 0 32 32" fill="none">
      <path
        d="M16 6L6 11v10l10 5 10-5V11L16 6z"
        stroke="#CC2927"
        strokeWidth="2"
        fill="none"
      />
      <path d="M6 11l10 5 10-5M16 16v10" stroke="#CC2927" strokeWidth="2" />
    </svg>
  );
}
