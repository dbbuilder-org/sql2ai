import { Metadata } from 'next';
import Link from 'next/link';
import { PricingTable, CTASection } from '../../components/marketing';

export const metadata: Metadata = {
  title: 'Pricing',
  description:
    'Simple, transparent pricing for SQL2.AI. Free for individual developers, with powerful plans for teams and enterprises.',
};

interface FAQItem {
  question: string;
  answer: string;
}

const faqs: FAQItem[] = [
  {
    question: 'What counts as a database connection?',
    answer:
      'A database connection is a unique combination of server, database name, and credentials. You can connect to the same database from multiple tools (CLI, MCP, SDK) without using additional connections.',
  },
  {
    question: 'Can I switch plans at any time?',
    answer:
      'Yes! You can upgrade or downgrade your plan at any time. When upgrading, you\'ll be charged a prorated amount for the remainder of your billing cycle. When downgrading, the change takes effect at the start of your next billing cycle.',
  },
  {
    question: 'What databases are supported?',
    answer:
      'SQL2.AI currently supports PostgreSQL (9.6+) and SQL Server (2016+). We\'re actively working on support for MySQL and Oracle, coming in early 2025.',
  },
  {
    question: 'How does the Claude MCP integration work?',
    answer:
      'SQL2.AI provides a Model Context Protocol (MCP) server that integrates directly with Claude. Once configured, Claude can access your database context, run analyses, and help with SQL tasks—all through natural conversation.',
  },
  {
    question: 'Is my database data secure?',
    answer:
      'Absolutely. SQL2.AI operates locally by default—your data never leaves your machine. For cloud features, all data is encrypted in transit and at rest, and we never store your actual database content, only metadata and analysis results.',
  },
  {
    question: 'What\'s included in the free plan?',
    answer:
      'The free plan includes full access to the CLI tool with 1 database connection, 100 query optimizations per month, and 5 schema analyses. It\'s perfect for individual developers working on personal projects.',
  },
  {
    question: 'Do you offer discounts for open source projects?',
    answer:
      'Yes! Open source maintainers can apply for a free Professional plan. Contact us with a link to your project and we\'ll set you up.',
  },
  {
    question: 'What support is included?',
    answer:
      'Free users get community support via GitHub Discussions. Professional users get email support with 48-hour response time. Team and Enterprise users get priority support with dedicated Slack channels and faster response times.',
  },
];

const comparisonFeatures = [
  { name: 'Database connections', free: '1', pro: '5', team: 'Unlimited', enterprise: 'Unlimited' },
  { name: 'Query optimizations', free: '100/mo', pro: 'Unlimited', team: 'Unlimited', enterprise: 'Unlimited' },
  { name: 'Schema analyses', free: '5/mo', pro: 'Unlimited', team: 'Unlimited', enterprise: 'Unlimited' },
  { name: 'CLI access', free: 'Basic', pro: 'Full', team: 'Full', enterprise: 'Full' },
  { name: 'MCP integration', free: '-', pro: 'Yes', team: 'Yes', enterprise: 'Yes' },
  { name: 'Migration generation', free: '-', pro: 'Yes', team: 'Yes', enterprise: 'Yes' },
  { name: 'Telemetry dashboard', free: '-', pro: 'Yes', team: 'Yes', enterprise: 'Yes' },
  { name: 'Team collaboration', free: '-', pro: '-', team: 'Yes', enterprise: 'Yes' },
  { name: 'CI/CD integration', free: '-', pro: '-', team: 'Yes', enterprise: 'Yes' },
  { name: 'SSO/SAML', free: '-', pro: '-', team: 'Yes', enterprise: 'Yes' },
  { name: 'Custom training', free: '-', pro: '-', team: 'Yes', enterprise: 'Yes' },
  { name: 'Dedicated support', free: '-', pro: '-', team: '-', enterprise: 'Yes' },
  { name: 'On-premise deployment', free: '-', pro: '-', team: '-', enterprise: 'Yes' },
  { name: 'SLA guarantee', free: '-', pro: '-', team: '-', enterprise: '99.9%' },
];

export default function PricingPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-8 md:pt-40 md:pb-12">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center">
            <h1 className="text-h1 text-text-primary mb-6">
              Simple, Transparent
              <br />
              <span className="gradient-text">Pricing</span>
            </h1>
            <p className="text-lg text-text-secondary">
              Start free, scale as you grow. No hidden fees, no surprises.
              <br />
              All plans include a 14-day free trial.
            </p>
          </div>
        </div>
      </section>

      {/* Pricing Table */}
      <PricingTable />

      {/* Feature Comparison Table */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Compare All Features</h2>
            <p className="text-text-secondary">
              A detailed breakdown of what&apos;s included in each plan.
            </p>
          </div>

          <div className="max-w-5xl mx-auto overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-4 px-4 text-small font-medium text-text-muted">Feature</th>
                  <th className="text-center py-4 px-4 text-small font-medium text-text-muted">Free</th>
                  <th className="text-center py-4 px-4 text-small font-medium text-text-primary bg-primary/5">Professional</th>
                  <th className="text-center py-4 px-4 text-small font-medium text-text-muted">Team</th>
                  <th className="text-center py-4 px-4 text-small font-medium text-text-muted">Enterprise</th>
                </tr>
              </thead>
              <tbody>
                {comparisonFeatures.map((feature, index) => (
                  <tr key={feature.name} className={`border-b border-border-subtle ${index % 2 === 0 ? 'bg-bg-surface/50' : ''}`}>
                    <td className="py-3 px-4 text-small text-text-secondary">{feature.name}</td>
                    <td className="text-center py-3 px-4 text-small text-text-muted">
                      {feature.free === '-' ? (
                        <span className="text-text-disabled">—</span>
                      ) : feature.free === 'Yes' ? (
                        <svg className="w-5 h-5 text-success mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        feature.free
                      )}
                    </td>
                    <td className="text-center py-3 px-4 text-small text-text-secondary bg-primary/5">
                      {feature.pro === '-' ? (
                        <span className="text-text-disabled">—</span>
                      ) : feature.pro === 'Yes' ? (
                        <svg className="w-5 h-5 text-success mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        feature.pro
                      )}
                    </td>
                    <td className="text-center py-3 px-4 text-small text-text-muted">
                      {feature.team === '-' ? (
                        <span className="text-text-disabled">—</span>
                      ) : feature.team === 'Yes' ? (
                        <svg className="w-5 h-5 text-success mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        feature.team
                      )}
                    </td>
                    <td className="text-center py-3 px-4 text-small text-text-muted">
                      {feature.enterprise === '-' ? (
                        <span className="text-text-disabled">—</span>
                      ) : feature.enterprise === 'Yes' ? (
                        <svg className="w-5 h-5 text-success mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      ) : (
                        feature.enterprise
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <h2 className="text-h3 text-text-primary mb-4">Frequently Asked Questions</h2>
            <p className="text-text-secondary">
              Have a question? We&apos;ve got answers.
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <div className="grid gap-4">
              {faqs.map((faq) => (
                <div key={faq.question} className="card p-6">
                  <h3 className="text-h5 text-text-primary mb-2">{faq.question}</h3>
                  <p className="text-small text-text-secondary">{faq.answer}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-12 text-center">
            <p className="text-text-secondary mb-4">
              Still have questions?
            </p>
            <Link href="/contact" className="text-primary hover:underline font-medium">
              Contact our sales team →
            </Link>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Get Started?"
        description="Start with our free plan and upgrade when you're ready. No credit card required."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'Contact Sales', href: '/contact' }}
      />
    </>
  );
}
