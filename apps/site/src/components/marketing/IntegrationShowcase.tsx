import { TerminalBlock } from '../ui/TerminalBlock';

export function IntegrationShowcase(): JSX.Element {
  return (
    <section className="section bg-bg-surface">
      <div className="container-wide">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-h2 text-text-primary mb-4">Works Where You Work</h2>
          <p className="text-lg text-text-secondary">
            Integrate SQL2.AI into your existing workflow—CLI, MCP for Claude, IDE extensions, and CI/CD pipelines.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* CLI Demo */}
          <div>
            <h3 className="text-h5 text-text-primary mb-4 flex items-center gap-2">
              <TerminalIcon className="w-5 h-5 text-primary" />
              Command Line
            </h3>
            <TerminalBlock
              title="sql2ai"
              commands={[
                {
                  command: 'sql2ai analyze --connection postgres://localhost/mydb',
                  output: `✓ Analyzing schema...
✓ Found 24 tables, 156 columns
✓ Detected 3 anti-patterns
✓ 2 missing index opportunities

Report saved to ./analysis-report.json`,
                },
                {
                  command: 'sql2ai optimize --file slow-query.sql',
                  output: `Original: 3.2s average execution
Optimized: 0.08s average execution
Improvement: 97.5% faster

Suggestions:
  1. Added covering index
  2. Converted cursor to set-based
  3. Removed implicit conversion`,
                },
              ]}
            />
          </div>

          {/* MCP Demo */}
          <div>
            <h3 className="text-h5 text-text-primary mb-4 flex items-center gap-2">
              <BrainIcon className="w-5 h-5 text-primary" />
              Claude MCP Integration
            </h3>
            <div className="card p-4">
              <div className="space-y-4">
                {/* User message */}
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-bg-elevated flex items-center justify-center shrink-0">
                    <span className="text-xs text-text-muted">You</span>
                  </div>
                  <div className="flex-1 bg-bg-elevated rounded-lg p-3">
                    <p className="text-small text-text-primary">
                      Analyze the Orders table and suggest indexes for our slow queries
                    </p>
                  </div>
                </div>

                {/* Claude response */}
                <div className="flex gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center shrink-0">
                    <span className="text-xs text-primary">AI</span>
                  </div>
                  <div className="flex-1 bg-bg-surface border border-border rounded-lg p-3">
                    <p className="text-small text-text-secondary mb-2">
                      I&apos;ve analyzed the Orders table using SQL2.AI. Here are my findings:
                    </p>
                    <ul className="text-small text-text-secondary space-y-1">
                      <li className="flex items-start gap-2">
                        <span className="text-success">1.</span>
                        <span>Add covering index on <code className="text-primary">(CustomerId, OrderDate) INCLUDE (Total)</code></span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-warning">2.</span>
                        <span>Remove duplicate index <code className="text-primary">IX_Orders_Date</code></span>
                      </li>
                      <li className="flex items-start gap-2">
                        <span className="text-success">3.</span>
                        <span>Consider filtered index for <code className="text-primary">Status = &apos;Pending&apos;</code></span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Integration logos */}
        <div className="mt-16 text-center">
          <p className="text-small text-text-muted mb-6">Also integrates with</p>
          <div className="flex flex-wrap justify-center gap-8">
            {[
              { name: 'VS Code', icon: <VSCodeIcon /> },
              { name: 'GitHub Actions', icon: <GitHubIcon /> },
              { name: 'Azure DevOps', icon: <AzureIcon /> },
              { name: 'SSMS', icon: <SSMSIcon /> },
            ].map((integration) => (
              <div key={integration.name} className="flex items-center gap-2 text-text-muted">
                <div className="w-6 h-6">{integration.icon}</div>
                <span className="text-small">{integration.name}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}

function TerminalIcon({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 9l3 3-3 3m5 0h3M5 20h14a2 2 0 002-2V6a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
    </svg>
  );
}

function BrainIcon({ className }: { className?: string }): JSX.Element {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );
}

function VSCodeIcon(): JSX.Element {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M17.583 2L8.236 11.358 3.893 7.849.5 9.632v4.736l3.393 1.783 4.343-3.509 9.347 9.358 5.917-2.958V4.958L17.583 2zm-1.5 13.625l-5.667-4.583 5.667-4.583v9.166z" />
    </svg>
  );
}

function GitHubIcon(): JSX.Element {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
    </svg>
  );
}

function AzureIcon(): JSX.Element {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M5.483 21.3H24L14.025 4.013l-3.038 8.347 5.836 6.938L5.483 21.3zM13.23 2.7L6.105 8.677 0 19.253h5.505l7.725-16.553z" />
    </svg>
  );
}

function SSMSIcon(): JSX.Element {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor">
      <path d="M4 4h16v16H4V4zm2 2v12h12V6H6zm2 2h8v2H8V8zm0 4h8v2H8v-2z" />
    </svg>
  );
}
