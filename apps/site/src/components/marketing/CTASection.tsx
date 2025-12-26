'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Play, Sparkles, Zap } from 'lucide-react';
import { Button, GradientText } from '../ui';

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
  variant?: 'default' | 'gradient' | 'minimal';
}

export function CTASection({
  title = 'Ready to Master Your Database?',
  description = 'Start optimizing your SQL Server and PostgreSQL databases with AI-powered insights.',
  primaryCTA = { text: 'Start Free Trial', href: '/signup' },
  secondaryCTA,
  variant = 'default',
}: CTASectionProps): JSX.Element {
  if (variant === 'minimal') {
    return (
      <section className="section">
        <div className="container-wide">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <h2 className="text-h3 text-text-primary mb-4">{title}</h2>
            <p className="text-lg text-text-secondary max-w-xl mx-auto mb-8">{description}</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Button asChild variant="gradient" size="lg">
                <Link href={primaryCTA.href}>
                  <Zap className="w-4 h-4" />
                  {primaryCTA.text}
                </Link>
              </Button>
              {secondaryCTA && (
                <Button asChild variant="secondary" size="lg">
                  <Link href={secondaryCTA.href}>
                    <Play className="w-4 h-4" />
                    {secondaryCTA.text}
                  </Link>
                </Button>
              )}
            </div>
          </motion.div>
        </div>
      </section>
    );
  }

  return (
    <section className="section relative overflow-hidden">
      <div className="container-narrow relative">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl border border-primary/20"
        >
          {/* Background */}
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 via-bg-elevated to-purple-500/10" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(59,130,246,0.2)_0%,_transparent_70%)]" />

          {/* Glow Effects */}
          <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-primary/20 rounded-full blur-[100px]" />
          <div className="absolute -bottom-20 right-1/4 w-[300px] h-[300px] bg-purple-500/20 rounded-full blur-[80px]" />

          {/* Grid Pattern */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.05)_1px,transparent_1px)] bg-[size:40px_40px] opacity-50" />

          {/* Content */}
          <div className="relative p-10 md:p-16 text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 border border-primary/20 mb-6"
            >
              <Sparkles className="w-4 h-4 text-primary" />
              <span className="text-sm text-primary font-medium">Free for individual developers</span>
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.2 }}
              className="text-3xl md:text-4xl lg:text-5xl font-bold text-text-primary mb-4"
            >
              {title.includes('?') ? (
                <>
                  {title.split('?')[0]}
                  <GradientText>?</GradientText>
                </>
              ) : (
                title
              )}
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
              className="text-lg text-text-secondary max-w-2xl mx-auto mb-10"
            >
              {description}
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
              <Button asChild size="xl" variant="glow">
                <Link href={primaryCTA.href} className="group">
                  <Zap className="w-5 h-5" />
                  {primaryCTA.text}
                  <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
                </Link>
              </Button>
              {secondaryCTA && (
                <Button asChild size="xl" variant="secondary">
                  <Link href={secondaryCTA.href}>
                    <Play className="w-5 h-5" />
                    {secondaryCTA.text}
                  </Link>
                </Button>
              )}
            </motion.div>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ delay: 0.5 }}
              className="mt-8 text-sm text-text-muted"
            >
              No credit card required • Setup in under 5 minutes • Cancel anytime
            </motion.p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
