import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Agent - Autonomous AI Database Operations | SQL2.AI',
  description:
    'Agentic AI that autonomously performs DBA, analysis, auditing, and optimization tasks based on context and compliance requirements.',
};

export default function AgentPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[#8B5CF6] to-[#EC4899] flex items-center justify-center text-white">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Agent</h1>
                <p className="text-lg bg-gradient-to-r from-[#8B5CF6] to-[#EC4899] bg-clip-text text-transparent font-medium">
                  Autonomous AI Operations
                </p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              An agentic AI that autonomously performs database operations based on context,
              compliance requirements, and observed patterns. Your AI-powered DBA, analyst,
              auditor, and optimizer working 24/7.
            </p>
          </div>
        </div>
      </section>

      {/* Agent Personas */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Agent Personas</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="card p-6 text-center border-t-4 border-[#3B82F6]">
              <div className="text-4xl mb-4">🔧</div>
              <h3 className="text-h5 text-text-primary mb-2">DBA Agent</h3>
              <p className="text-sm text-text-muted mb-4">Index management, statistics, backups, space management</p>
              <ul className="text-xs text-text-secondary text-left space-y-1">
                <li>• Creates indexes automatically</li>
                <li>• Updates statistics proactively</li>
                <li>• Manages file growth</li>
                <li>• Verifies backup integrity</li>
              </ul>
            </div>

            <div className="card p-6 text-center border-t-4 border-[#10B981]">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-h5 text-text-primary mb-2">Analyst Agent</h3>
              <p className="text-sm text-text-muted mb-4">Anomaly detection, trends, data quality, insights</p>
              <ul className="text-xs text-text-secondary text-left space-y-1">
                <li>• Detects data anomalies</li>
                <li>• Identifies trends</li>
                <li>• Scores data quality</li>
                <li>• Generates insights</li>
              </ul>
            </div>

            <div className="card p-6 text-center border-t-4 border-[#F59E0B]">
              <div className="text-4xl mb-4">🛡️</div>
              <h3 className="text-h5 text-text-primary mb-2">Auditor Agent</h3>
              <p className="text-sm text-text-muted mb-4">Permissions, compliance, access patterns, PII</p>
              <ul className="text-xs text-text-secondary text-left space-y-1">
                <li>• Reviews permissions</li>
                <li>• Monitors compliance</li>
                <li>• Detects suspicious access</li>
                <li>• Classifies PII columns</li>
              </ul>
            </div>

            <div className="card p-6 text-center border-t-4 border-[#EF4444]">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-h5 text-text-primary mb-2">Optimizer Agent</h3>
              <p className="text-sm text-text-muted mb-4">Query tuning, resource optimization, capacity planning</p>
              <ul className="text-xs text-text-secondary text-left space-y-1">
                <li>• Rewrites slow queries</li>
                <li>• Tunes configuration</li>
                <li>• Balances workloads</li>
                <li>• Plans capacity</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Observe → Orient → Decide → Act</h2>

          <div className="max-w-4xl mx-auto">
            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
│  SQL AGENT: Index Optimization Decision                          │
├─────────────────────────────────────────────────────────────────┤
│  OBSERVATION:                                                    │
│  • Query on Orders table taking 12s (threshold: 2s)             │
│  • Missing index hint detected in execution plan                 │
│  • Index would benefit 847 queries/hour                          │
│  • Current time: 2:30 AM (low activity window)                  │
│  • Storage available: 45 GB (index estimate: 2 GB)              │
│                                                                  │
│  CONTEXT:                                                        │
│  • No deployments scheduled in next 4 hours                      │
│  • Similar index created last month improved query by 95%        │
│  • Compliance: No restrictions on index creation                 │
│                                                                  │
│  DECISION: CREATE INDEX                                          │
│  • Confidence: 94%                                               │
│  • Estimated improvement: 11.5s → 0.3s                          │
│  • Risk level: Low                                               │
│                                                                  │
│  ACTION TAKEN:                                                   │
│  CREATE INDEX IX_Orders_CustomerId_OrderDate                     │
│  ON Orders (CustomerId, OrderDate)                               │
│  INCLUDE (Total, Status)                                         │
│  WITH (ONLINE = ON, MAXDOP = 2)                                  │
│                                                                  │
│  RESULT: ✓ Index created in 3 minutes                           │
│          ✓ Query time reduced to 0.28s                          │
│          ✓ Notification sent to DBA team                        │
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Compliance-Aware */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Compliance-Aware Actions</h2>
            <p className="text-text-secondary text-center mb-12">
              The agent understands your compliance requirements and acts within boundaries
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
│  SQL AGENT: Compliance Alert                                     │
├─────────────────────────────────────────────────────────────────┤
│  OBSERVATION:                                                    │
│  • New column 'diagnosis_notes' added to Patients table          │
│  • Column contains free-text medical information                 │
│  • No encryption or masking applied                              │
│  • Table has 145,000 rows                                        │
│                                                                  │
│  CONTEXT:                                                        │
│  • Database is HIPAA-regulated                                   │
│  • Similar columns require encryption (Always Encrypted)         │
│  • Column name suggests PHI content                              │
│                                                                  │
│  DECISION: ALERT + RECOMMENDATION                                │
│  • Severity: HIGH                                                │
│  • Compliance risk: HIPAA §164.312(a)(2)(iv)                    │
│                                                                  │
│  RECOMMENDED ACTIONS:                                            │
│  1. Apply column encryption (Always Encrypted)                   │
│  2. Add to PII inventory                                         │
│  3. Update access controls                                       │
│  4. Review audit logging for this column                         │
│                                                                  │
│  [Apply Encryption] [Create Ticket] [Dismiss with Reason]       │
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Human in the Loop */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Human-in-the-Loop</h2>
            <p className="text-text-secondary text-center mb-12">
              Critical actions require your approval. The agent explains its reasoning and learns from your decisions.
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
│  SQL AGENT: Approval Required                                    │
├─────────────────────────────────────────────────────────────────┤
│  PROPOSED ACTION: Kill blocking session                          │
│                                                                  │
│  Session ID: 547                                                 │
│  User: reporting_service                                         │
│  Blocking duration: 8 minutes                                    │
│  Affected queries: 23                                            │
│  Query: SELECT * FROM LargeTable WITH (NOLOCK)                  │
│                                                                  │
│  AGENT REASONING:                                                │
│  "This session has been blocking 23 production queries for      │
│   8 minutes. The blocking query appears to be a reporting        │
│   query that could be restarted. Killing this session would     │
│   restore normal operations. However, this is a production      │
│   system and I require human approval for session termination." │
│                                                                  │
│  [✓ Approve Kill] [✗ Reject] [⏸ Defer 5 min] [💬 Ask More]     │
│                                                                  │
│  Your decision will help me learn for future situations.        │
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Autonomy Levels */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Configurable Autonomy</h2>

          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="card p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-[#10B981]/10 flex items-center justify-center text-[#10B981] mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">Monitor Only</h3>
              <p className="text-sm text-text-muted">
                Agent observes and recommends but never takes action
              </p>
            </div>

            <div className="card p-6 text-center border-2 border-primary">
              <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">Supervised</h3>
              <p className="text-sm text-text-muted">
                Low-risk actions auto-approved, critical actions require approval
              </p>
              <span className="text-xs text-primary font-medium">Recommended</span>
            </div>

            <div className="card p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-[#F59E0B]/10 flex items-center justify-center text-[#F59E0B] mx-auto mb-4">
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
              <h3 className="text-h5 text-text-primary mb-2">Autonomous</h3>
              <p className="text-sm text-text-muted">
                Full autonomy within guardrails, notifications on all actions
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Learning */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Learns From Your Decisions</h2>
            <p className="text-text-secondary mb-12">
              Every approval or rejection teaches the agent. Confidence improves over time.
            </p>

            <div className="card p-6">
              <div className="grid md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#10B981] mb-1">87%</div>
                  <div className="text-sm text-text-muted">Index Decisions</div>
                  <div className="text-xs text-[#10B981]">↑ 4% this week</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#10B981] mb-1">92%</div>
                  <div className="text-sm text-text-muted">Backup Timing</div>
                  <div className="text-xs text-text-muted">stable</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#F59E0B] mb-1">68%</div>
                  <div className="text-sm text-text-muted">Resource Tuning</div>
                  <div className="text-xs text-[#F59E0B]">learning</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-[#10B981] mb-1">95%</div>
                  <div className="text-sm text-text-muted">Compliance Alerts</div>
                  <div className="text-xs text-text-muted">stable</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Agent Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL AGENT DASHBOARD                            ║
╠══════════════════════════════════════════════════════════════════╣
║ AGENT STATUS: ✓ Active (Supervised Mode)                         ║
╠══════════════════════════════════════════════════════════════════╣
║ LAST 24 HOURS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Actions Taken:        47                                          ║
║ Approvals Requested:  3                                           ║
║ Anomalies Detected:   12                                          ║
║ Issues Prevented:     5                                           ║
╠══════════════════════════════════════════════════════════════════╣
║ PERSONA ACTIVITY                                                  ║
║ ─────────────────────────────────────────────────────────────── ║
║ DBA Agent:       15 actions │ 2 indexes created, 8 stats updated ║
║ Analyst Agent:   8 reports  │ 3 anomalies flagged                ║
║ Auditor Agent:   18 checks  │ 1 compliance issue found           ║
║ Optimizer Agent: 6 tunings  │ 2 queries improved                 ║
╠══════════════════════════════════════════════════════════════════╣
║ AWAITING APPROVAL                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ • Kill session 547 (blocking for 8 min)     [Approve] [Reject]  ║
║ • Drop unused index IX_Legacy_1             [Approve] [Reject]  ║
║ • Increase tempdb files to 8                [Approve] [Reject]  ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Guardrails */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Built-In Guardrails</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Compliance Boundaries', desc: 'Actions respect HIPAA, PCI-DSS, SOC 2 requirements' },
              { title: 'Approval Workflows', desc: 'Critical actions require human confirmation' },
              { title: 'Automatic Rollback', desc: 'Failed actions are automatically reversed' },
              { title: 'Complete Audit Trail', desc: 'Every action and decision is logged' },
            ].map((item) => (
              <div key={item.title} className="card p-6">
                <h3 className="text-h6 text-text-primary mb-2">{item.title}</h3>
                <p className="text-sm text-text-muted">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Let AI Manage Your Database"
        description="Autonomous, context-aware database operations with human oversight when needed."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
