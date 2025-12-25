import Link from 'next/link';

interface CTASectionProps {
  title?: string;
  description?: string;
  primaryCTA?: {
    text: string;
    href: string;
  };
  secondaryCTA?: {
    text: string;
    href: string;
  };
}

export function CTASection({
  title = 'Ready to Master Your Database?',
  description = 'Start optimizing your SQL Server and PostgreSQL databases with AI-powered insights.',
  primaryCTA = { text: 'Start Free Trial', href: '/signup' },
  secondaryCTA,
}: CTASectionProps): JSX.Element {
  return (
    <section className="section">
      <div className="container-narrow">
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-primary/20 via-bg-elevated to-bg-surface border border-border p-8 md:p-12 text-center">
          {/* Background glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-96 bg-primary/20 rounded-full blur-3xl" />

          <div className="relative">
            <h2 className="text-h2 text-text-primary mb-4">{title}</h2>
            <p className="text-lg text-text-secondary max-w-xl mx-auto mb-8">{description}</p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href={primaryCTA.href} className="btn-primary text-base px-8 py-4">
                {primaryCTA.text}
              </Link>
              {secondaryCTA && (
                <Link href={secondaryCTA.href} className="btn-secondary text-base px-8 py-4">
                  {secondaryCTA.text}
                </Link>
              )}
            </div>

            <p className="mt-6 text-small text-text-muted">
              No credit card required • Free for individual developers
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
