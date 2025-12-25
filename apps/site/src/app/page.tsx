import Link from 'next/link';
import {
  Hero,
  PhilosophySection,
  LifecycleIndicator,
  PlatformBridge,
  IntegrationShowcase,
  PricingPreview,
  CTASection,
  modules,
} from '../components/marketing';

export default function HomePage(): JSX.Element {
  return (
    <>
      {/* Hero Section */}
      <Hero />

      {/* Philosophy - Why we're different */}
      <PhilosophySection />

      {/* Modules Overview */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-3xl mx-auto text-center mb-12">
            <span className="inline-block px-4 py-2 rounded-full bg-primary/10 text-primary text-small font-medium mb-4">
              8 Integrated Modules
            </span>
            <h2 className="text-h2 text-text-primary mb-4">
              One Platform, Complete Coverage
            </h2>
            <p className="text-lg text-text-secondary">
              SQL2.AI brings AI-powered sophistication to every stage of database development.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mb-8">
            {modules.map((module) => (
              <Link
                key={module.id}
                href={module.href}
                className="card p-5 hover:border-primary/50 transition-colors group"
              >
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center mb-3"
                  style={{ backgroundColor: `${module.color}15`, color: module.color }}
                  dangerouslySetInnerHTML={{ __html: module.icon }}
                />
                <h3 className="text-h6 text-text-primary mb-1 group-hover:text-primary transition-colors">
                  {module.name}
                </h3>
                <p className="text-small text-text-muted">{module.tagline}</p>
              </Link>
            ))}
          </div>

          <div className="text-center">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-primary hover:text-primary/80 font-medium"
            >
              Explore all features
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

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
