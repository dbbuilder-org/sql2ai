export function PlatformBridge(): JSX.Element {
  return (
    <section className="section">
      <div className="container-wide">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-h2 text-text-primary mb-4">
            One Platform. Two Databases.
            <br />
            <span className="gradient-text">Zero Compromises.</span>
          </h2>
          <p className="text-lg text-text-secondary">
            Translate between SQL Server and PostgreSQL with full context preservation—
            transactions, isolation levels, and semantics intact.
          </p>
        </div>

        {/* Bridge visualization */}
        <div className="relative max-w-4xl mx-auto">
          <div className="flex items-center justify-between">
            {/* PostgreSQL side */}
            <div className="flex flex-col items-center">
              <div className="w-20 h-20 rounded-2xl bg-postgresql/10 border border-postgresql/20 flex items-center justify-center mb-4">
                <PostgreSQLLogo className="w-12 h-12" />
              </div>
              <span className="text-lg font-medium text-text-primary">PostgreSQL</span>
              <span className="text-small text-text-muted">Source or Target</span>
            </div>

            {/* Bridge */}
            <div className="flex-1 mx-8 relative">
              {/* Connection lines */}
              <div className="absolute inset-y-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-postgresql via-primary to-sqlserver" />

              {/* Center hub */}
              <div className="relative z-10 flex justify-center">
                <div className="w-16 h-16 rounded-full bg-bg-elevated border-2 border-primary flex items-center justify-center">
                  <svg className="w-8 h-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                  </svg>
                </div>
              </div>

              {/* Arrows */}
              <div className="absolute top-1/2 left-4 -translate-y-1/2">
                <svg className="w-6 h-6 text-postgresql" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </div>
              <div className="absolute top-1/2 right-4 -translate-y-1/2">
                <svg className="w-6 h-6 text-sqlserver" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16l-4-4m0 0l4-4m-4 4h18" />
                </svg>
              </div>
            </div>

            {/* SQL Server side */}
            <div className="flex flex-col items-center">
              <div className="w-20 h-20 rounded-2xl bg-sqlserver/10 border border-sqlserver/20 flex items-center justify-center mb-4">
                <SQLServerLogo className="w-12 h-12" />
              </div>
              <span className="text-lg font-medium text-text-primary">SQL Server</span>
              <span className="text-small text-text-muted">Source or Target</span>
            </div>
          </div>
        </div>

        {/* Translation examples */}
        <div className="mt-16 grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { from: 'IDENTITY(1,1)', to: 'SERIAL', category: 'Data Types' },
            { from: 'TOP 10', to: 'LIMIT 10', category: 'Queries' },
            { from: "'+' concat", to: "'||' concat", category: 'Operators' },
          ].map((example) => (
            <div key={example.category} className="card p-4 text-center">
              <span className="text-xs text-text-muted uppercase tracking-wide">{example.category}</span>
              <div className="mt-2 flex items-center justify-center gap-2">
                <code className="text-small text-sqlserver">{example.from}</code>
                <span className="text-text-muted">→</span>
                <code className="text-small text-postgresql">{example.to}</code>
              </div>
            </div>
          ))}
        </div>

        {/* What we preserve */}
        <div className="mt-12 text-center">
          <h3 className="text-h5 text-text-primary mb-4">What We Preserve</h3>
          <div className="flex flex-wrap justify-center gap-3">
            {['Transaction semantics', 'Isolation levels', 'Lock ordering', 'Constraint behavior', 'Index strategy'].map(
              (item) => (
                <span key={item} className="px-4 py-2 rounded-full bg-bg-surface border border-border text-small text-text-secondary">
                  {item}
                </span>
              )
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

function PostgreSQLLogo({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} viewBox="0 0 48 48" fill="none">
      <circle cx="24" cy="24" r="20" stroke="#336791" strokeWidth="3" fill="none" />
      <path
        d="M24 12c-6.627 0-12 5.373-12 12s5.373 12 12 12 12-5.373 12-12-5.373-12-12-12zm0 3c4.97 0 9 4.03 9 9s-4.03 9-9 9-9-4.03-9-9 4.03-9 9-9z"
        fill="#336791"
      />
      <ellipse cx="24" cy="24" rx="6" ry="9" stroke="#336791" strokeWidth="2" fill="none" />
    </svg>
  );
}

function SQLServerLogo({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} viewBox="0 0 48 48" fill="none">
      <path
        d="M24 8L8 16v16l16 8 16-8V16L24 8z"
        stroke="#CC2927"
        strokeWidth="3"
        fill="none"
      />
      <path d="M8 16l16 8 16-8" stroke="#CC2927" strokeWidth="2" />
      <path d="M24 24v16" stroke="#CC2927" strokeWidth="2" />
    </svg>
  );
}
