import {
  Hero,
  PhilosophySection,
  LifecycleIndicator,
  PlatformBridge,
  IntegrationShowcase,
  PricingPreview,
  CTASection,
} from '../components/marketing';

export default function HomePage(): JSX.Element {
  return (
    <>
      {/* Hero Section */}
      <Hero />

      {/* Philosophy - Why we're different */}
      <PhilosophySection />

      {/* Lifecycle Section */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-16">
            <h2 className="text-h2 text-text-primary mb-4">
              The Complete Database Development Lifecycle
            </h2>
            <p className="text-lg text-text-secondary">
              From initial analysis to production deployment—SQL2.AI covers every stage
              of database development with AI-powered insights.
            </p>
          </div>

          <LifecycleIndicator />
        </div>
      </section>

      {/* Platform Bridge */}
      <PlatformBridge />

      {/* Integration Showcase */}
      <IntegrationShowcase />

      {/* Pricing Preview */}
      <PricingPreview />

      {/* Final CTA */}
      <CTASection
        title="Ready to Master Your Database?"
        description="Start optimizing your SQL Server and PostgreSQL databases with AI-powered insights. Free for individual developers."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'Watch Demo', href: '/demo' }}
      />
    </>
  );
}
