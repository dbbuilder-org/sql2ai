import Link from 'next/link';

interface PricingTier {
  name: string;
  price: string;
  period?: string;
  description: string;
  features: string[];
  cta: {
    text: string;
    href: string;
  };
  popular?: boolean;
}

const tiers: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    period: '/mo',
    description: 'For individual developers exploring SQL2.AI',
    features: [
      '1 database connection',
      '100 query optimizations/month',
      '5 schema analyses/month',
      'Basic CLI access',
      'Community support',
    ],
    cta: { text: 'Get Started', href: '/signup' },
  },
  {
    name: 'Professional',
    price: '$29',
    period: '/mo',
    description: 'For professional developers and small teams',
    features: [
      '5 database connections',
      'Unlimited query optimizations',
      'Unlimited schema analyses',
      'Full CLI + MCP access',
      'Migration generation',
      'Telemetry dashboard',
      'Email support',
    ],
    cta: { text: 'Start Free Trial', href: '/signup?plan=pro' },
    popular: true,
  },
  {
    name: 'Team',
    price: '$99',
    period: '/mo',
    description: 'For development teams up to 10 members',
    features: [
      'Everything in Professional',
      'Unlimited connections',
      'Team collaboration',
      'CI/CD integration',
      'SSO authentication',
      'Priority support',
      'Custom training',
    ],
    cta: { text: 'Start Free Trial', href: '/signup?plan=team' },
  },
];

export function PricingTable(): JSX.Element {
  return (
    <section className="section" id="pricing">
      <div className="container-wide">
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-h2 text-text-primary mb-4">Simple, Transparent Pricing</h2>
          <p className="text-lg text-text-secondary">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {tiers.map((tier) => (
            <div
              key={tier.name}
              className={`
                card p-6 flex flex-col
                ${tier.popular ? 'border-primary ring-1 ring-primary' : ''}
              `}
            >
              {tier.popular && (
                <div className="text-center mb-4">
                  <span className="inline-block px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium">
                    Most Popular
                  </span>
                </div>
              )}

              <div className="text-center mb-6">
                <h3 className="text-h4 text-text-primary">{tier.name}</h3>
                <div className="mt-2">
                  <span className="text-4xl font-bold text-text-primary">{tier.price}</span>
                  {tier.period && <span className="text-text-muted">{tier.period}</span>}
                </div>
                <p className="mt-2 text-small text-text-muted">{tier.description}</p>
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2 text-small text-text-secondary">
                    <svg
                      className="w-4 h-4 text-success shrink-0 mt-0.5"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <Link
                href={tier.cta.href}
                className={tier.popular ? 'btn-primary w-full' : 'btn-secondary w-full'}
              >
                {tier.cta.text}
              </Link>
            </div>
          ))}
        </div>

        {/* Enterprise CTA */}
        <div className="mt-12 text-center">
          <p className="text-text-secondary mb-4">
            Need more? We offer custom Enterprise plans with dedicated support.
          </p>
          <Link href="/contact?type=enterprise" className="text-primary hover:underline font-medium">
            Contact Sales →
          </Link>
        </div>
      </div>
    </section>
  );
}

export function PricingPreview(): JSX.Element {
  return (
    <section className="section">
      <div className="container-wide">
        <div className="max-w-3xl mx-auto text-center mb-12">
          <h2 className="text-h3 text-text-primary mb-4">Plans for Every Team</h2>
        </div>

        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <div className="card px-6 py-4 text-center">
            <div className="text-2xl font-bold text-text-primary">$0</div>
            <div className="text-small text-text-muted">Free</div>
          </div>
          <div className="card px-6 py-4 text-center border-primary">
            <div className="text-2xl font-bold text-text-primary">$29</div>
            <div className="text-small text-text-muted">Professional</div>
          </div>
          <div className="card px-6 py-4 text-center">
            <div className="text-2xl font-bold text-text-primary">$99</div>
            <div className="text-small text-text-muted">Team</div>
          </div>
          <div className="card px-6 py-4 text-center">
            <div className="text-2xl font-bold text-text-primary">Custom</div>
            <div className="text-small text-text-muted">Enterprise</div>
          </div>
        </div>

        <div className="text-center">
          <Link href="/pricing" className="text-primary hover:underline font-medium">
            See full pricing details →
          </Link>
        </div>
      </div>
    </section>
  );
}
