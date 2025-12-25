export function PhilosophySection(): JSX.Element {
  return (
    <section className="section bg-bg-surface">
      <div className="container-wide">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-h2 text-text-primary mb-4">
            Most AI tools help you escape your database.
            <br />
            <span className="text-text-muted">We help you master it.</span>
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          {/* Traditional Approach */}
          <div className="card-elevated p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-error/10 flex items-center justify-center">
                <svg className="w-5 h-5 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary">ORM-First Approach</h3>
            </div>
            <ul className="space-y-3">
              {[
                'Generate migrations from code',
                'Abstract away SQL',
                'Treat procedures as legacy',
                'Single database focus',
                'Chat-based interface',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2 text-small text-text-muted">
                  <span className="text-error mt-1">✗</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>

          {/* SQL2.AI Approach */}
          <div className="card p-6 border-primary">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                <svg className="w-5 h-5 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary">SQL2.AI Approach</h3>
            </div>
            <ul className="space-y-3">
              {[
                'Generate database-native DDL',
                'Optimize and enhance SQL',
                'Procedures as first-class citizens',
                'SQL Server ↔ PostgreSQL bridging',
                'Workflow integration (CLI, MCP, IDE)',
              ].map((item) => (
                <li key={item} className="flex items-start gap-2 text-small text-text-secondary">
                  <span className="text-success mt-1">✓</span>
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Core thesis */}
        <div className="mt-16 text-center">
          <blockquote className="text-xl md:text-2xl text-text-primary italic max-w-2xl mx-auto">
            &ldquo;Data models drive application objects, not the reverse.&rdquo;
          </blockquote>
          <p className="mt-4 text-small text-text-muted">— The SQL2.AI Philosophy</p>
        </div>
      </div>
    </section>
  );
}
