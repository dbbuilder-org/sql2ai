import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Send - Database Messaging Platform | SQL2.AI',
  description:
    'Send emails and SMS from SQL Server and PostgreSQL via SendGrid, Resend, and Twilio. Transactional outbox pattern for guaranteed delivery.',
};

export default function SendPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#3B82F6]/10 flex items-center justify-center text-[#3B82F6]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Send</h1>
                <p className="text-lg text-[#3B82F6] font-medium">Database Messaging</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Send emails and SMS directly from SQL Server and PostgreSQL via SendGrid, Resend, and Twilio.
              Transactional outbox pattern ensures guaranteed delivery with no lost messages.
            </p>
          </div>
        </div>
      </section>

      {/* Providers */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Supported Providers</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {[
              { name: 'SendGrid', type: 'Email', icon: '📧' },
              { name: 'Resend', type: 'Email', icon: '✉️' },
              { name: 'Twilio', type: 'SMS', icon: '📱' },
              { name: 'Custom SMTP', type: 'Email', icon: '🔧' },
            ].map((provider) => (
              <div key={provider.name} className="card p-6 text-center">
                <div className="text-3xl mb-3">{provider.icon}</div>
                <h3 className="text-h5 text-text-primary mb-1">{provider.name}</h3>
                <p className="text-sm text-text-muted">{provider.type}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Outbox Pattern */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Transactional Outbox Pattern</h2>
            <p className="text-text-secondary text-center mb-12">
              Messages are written to an outbox table in the same transaction as your data changes.
              No messages are ever lost, even during failures.
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`┌─────────────────────────────────────────────────────────────────┐
│  1. Application Transaction                                      │
│  ─────────────────────────────────────────────────────────────  │
│  BEGIN TRANSACTION                                               │
│    INSERT INTO Orders (CustomerId, Total) VALUES (1, 99.99);    │
│    INSERT INTO sql2ai.Outbox (Type, Payload) VALUES             │
│      ('order_confirmation', '{"orderId": 123, "email": "..."}');│
│  COMMIT                                                          │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. SQL Send Agent (polls Outbox)                                │
│  ─────────────────────────────────────────────────────────────  │
│  • Reads pending messages                                        │
│  • Sends via configured provider                                 │
│  • Marks as sent (or retries on failure)                        │
│  • Moves to archive after success                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. Provider Delivery                                            │
│  ─────────────────────────────────────────────────────────────  │
│  SendGrid / Resend / Twilio → Customer                          │
└─────────────────────────────────────────────────────────────────┘`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* SQL Interface */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Simple SQL Interface</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Send an email
EXEC sql2ai.SendEmail
    @To = 'customer@example.com',
    @Subject = 'Order Confirmation',
    @Body = '<h1>Thank you for your order!</h1>',
    @Provider = 'sendgrid';  -- or 'resend'

-- Send an SMS
EXEC sql2ai.SendSMS
    @To = '+1234567890',
    @Message = 'Your order has shipped!',
    @Provider = 'twilio';

-- Send with template
EXEC sql2ai.SendEmail
    @To = 'customer@example.com',
    @Template = 'order_confirmation',
    @TemplateData = '{"orderId": 12345, "total": 99.99}';

-- Bulk send (queued efficiently)
EXEC sql2ai.SendBulkEmail
    @Recipients = '[
        {"email": "a@x.com", "data": {"name": "Alice"}},
        {"email": "b@x.com", "data": {"name": "Bob"}}
    ]',
    @Template = 'newsletter';`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Features</h2>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Guaranteed Delivery', desc: 'Outbox pattern ensures no messages are ever lost' },
              { title: 'Retry Logic', desc: 'Automatic retries with exponential backoff' },
              { title: 'Template Engine', desc: 'Handlebars templates with data binding' },
              { title: 'Tracking', desc: 'Delivery status, opens, clicks tracked' },
              { title: 'Rate Limiting', desc: 'Respect provider rate limits automatically' },
              { title: 'Audit Trail', desc: 'Complete history of all sent messages' },
            ].map((feature) => (
              <div key={feature.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-2">{feature.title}</h3>
                <p className="text-sm text-text-muted">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Dashboard */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-8 text-center">Delivery Dashboard</h2>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`╔══════════════════════════════════════════════════════════════════╗
║                    SQL SEND DASHBOARD                             ║
╠══════════════════════════════════════════════════════════════════╣
║ LAST 24 HOURS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Emails Sent:      12,847                                          ║
║ SMS Sent:         1,234                                           ║
║ Delivery Rate:    99.7%                                           ║
║ Open Rate:        34.2%                                           ║
╠══════════════════════════════════════════════════════════════════╣
║ OUTBOX STATUS                                                     ║
║ ─────────────────────────────────────────────────────────────── ║
║ Pending:          23                                              ║
║ Processing:       5                                               ║
║ Retry Queue:      2 (next retry in 5 min)                        ║
║ Failed (24h):     4                                               ║
╠══════════════════════════════════════════════════════════════════╣
║ BY PROVIDER                                                       ║
║ ─────────────────────────────────────────────────────────────── ║
║ SendGrid:         10,234 emails | 99.8% delivered                ║
║ Resend:           2,613 emails  | 99.5% delivered                ║
║ Twilio:           1,234 SMS     | 99.9% delivered                ║
╚══════════════════════════════════════════════════════════════════╝`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Send Messages Reliably"
        description="Email and SMS from your database with guaranteed delivery and full tracking."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
