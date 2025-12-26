'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Check, Sparkles, Zap, Building2, ArrowRight } from 'lucide-react';
import { Button, Badge, GradientText } from '../ui';
import { cn } from '@/lib/utils';

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
  icon: React.ReactNode;
}

const tiers: PricingTier[] = [
  {
    name: 'Free',
    price: '$0',
    period: '/mo',
    description: 'For individual developers exploring SQL2.AI',
    icon: <Zap className="w-5 h-5" />,
    features: [
      '1 database connection',
      '100 query optimizations/month',
      '5 schema analyses/month',
      'Basic CLI access',
      'Community support',
    ],
    cta: { text: 'Get Started Free', href: '/signup' },
  },
  {
    name: 'Professional',
    price: '$29',
    period: '/mo',
    description: 'For professional developers and small teams',
    icon: <Sparkles className="w-5 h-5" />,
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
    icon: <Building2 className="w-5 h-5" />,
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
    <section className="section relative overflow-hidden" id="pricing">
      {/* Background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_rgba(59,130,246,0.1)_0%,_transparent_50%)]" />

      <div className="container-wide relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center mb-16"
        >
          <Badge variant="gradient" className="mb-4">
            <Sparkles className="w-3 h-3" />
            Pricing
          </Badge>
          <h2 className="text-h2 text-text-primary mb-4">
            Simple, <GradientText>Transparent</GradientText> Pricing
          </h2>
          <p className="text-lg text-text-secondary">
            Start free, scale as you grow. No hidden fees, no surprises.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className={cn(
                'relative rounded-2xl border p-8 flex flex-col',
                'bg-bg-surface/50 backdrop-blur-sm',
                'transition-all duration-300',
                tier.popular
                  ? 'border-primary shadow-glow-primary scale-105 z-10'
                  : 'border-border hover:border-primary/50'
              )}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                  <Badge variant="glow" className="shadow-lg">
                    <Sparkles className="w-3 h-3" />
                    Most Popular
                  </Badge>
                </div>
              )}

              <div className="text-center mb-8">
                <div
                  className={cn(
                    'w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4',
                    tier.popular
                      ? 'bg-primary text-white'
                      : 'bg-bg-elevated text-text-secondary'
                  )}
                >
                  {tier.icon}
                </div>
                <h3 className="text-h4 text-text-primary">{tier.name}</h3>
                <div className="mt-4">
                  <span className="text-5xl font-bold text-text-primary">
                    {tier.popular ? <GradientText>{tier.price}</GradientText> : tier.price}
                  </span>
                  {tier.period && <span className="text-text-muted">{tier.period}</span>}
                </div>
                <p className="mt-3 text-sm text-text-muted">{tier.description}</p>
              </div>

              <ul className="space-y-4 mb-8 flex-1">
                {tier.features.map((feature, i) => (
                  <motion.li
                    key={feature}
                    initial={{ opacity: 0, x: -10 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: 0.2 + i * 0.05 }}
                    className="flex items-start gap-3 text-sm text-text-secondary"
                  >
                    <Check className={cn(
                      'w-5 h-5 shrink-0',
                      tier.popular ? 'text-primary' : 'text-success'
                    )} />
                    {feature}
                  </motion.li>
                ))}
              </ul>

              <Button
                asChild
                variant={tier.popular ? 'gradient' : 'secondary'}
                className="w-full"
                size="lg"
              >
                <Link href={tier.cta.href}>
                  {tier.cta.text}
                  <ArrowRight className="w-4 h-4" />
                </Link>
              </Button>
            </motion.div>
          ))}
        </div>

        {/* Enterprise CTA */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 max-w-3xl mx-auto"
        >
          <div className="rounded-2xl border border-border bg-gradient-to-br from-bg-surface to-bg-elevated p-8 text-center">
            <h3 className="text-h4 text-text-primary mb-2">Need Enterprise Features?</h3>
            <p className="text-text-secondary mb-6">
              Custom pricing for large teams with dedicated support, SLA guarantees, and on-premise deployment options.
            </p>
            <Button asChild variant="outline" size="lg">
              <Link href="/contact?type=enterprise">
                Contact Sales
                <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

export function PricingPreview(): JSX.Element {
  return (
    <section className="section bg-bg-surface">
      <div className="container-wide">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto text-center mb-12"
        >
          <h2 className="text-h3 text-text-primary mb-4">
            Plans for <GradientText>Every Team</GradientText>
          </h2>
        </motion.div>

        <div className="flex flex-wrap justify-center gap-4 mb-8">
          {[
            { price: '$0', name: 'Free', popular: false },
            { price: '$29', name: 'Professional', popular: true },
            { price: '$99', name: 'Team', popular: false },
            { price: 'Custom', name: 'Enterprise', popular: false },
          ].map((plan, index) => (
            <motion.div
              key={plan.name}
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className={cn(
                'rounded-xl border px-8 py-6 text-center transition-all',
                plan.popular
                  ? 'border-primary bg-primary/5 shadow-glow-sm'
                  : 'border-border bg-bg-base hover:border-primary/50'
              )}
            >
              <div className="text-3xl font-bold text-text-primary mb-1">
                {plan.popular ? <GradientText>{plan.price}</GradientText> : plan.price}
              </div>
              <div className="text-sm text-text-muted">{plan.name}</div>
            </motion.div>
          ))}
        </div>

        <div className="text-center">
          <Link
            href="/pricing"
            className="inline-flex items-center gap-2 text-primary hover:text-primary-hover font-medium transition-colors group"
          >
            See full pricing details
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>
    </section>
  );
}
