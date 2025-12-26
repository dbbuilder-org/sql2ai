'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowRight, Play, Sparkles, Zap } from 'lucide-react';
import { Button, Badge, GradientText, GlowOrb } from '../ui';

export function Hero(): JSX.Element {
  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 pb-20 overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-bg-base" />

      {/* Animated Grid Pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(59,130,246,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(59,130,246,0.03)_1px,transparent_1px)] bg-[size:60px_60px] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_70%)]" />

      {/* Glow Orbs */}
      <GlowOrb className="top-1/4 left-1/4 -translate-x-1/2" color="primary" size="xl" />
      <GlowOrb className="top-1/3 right-1/4 translate-x-1/2" color="purple" size="lg" />
      <GlowOrb className="bottom-1/4 left-1/3" color="cyan" size="md" />

      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-bg-base/50 to-bg-base" />

      <div className="container-wide relative z-10">
        <div className="max-w-5xl mx-auto text-center">
          {/* Announcement Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="mb-8"
          >
            <Badge variant="glow" pulse className="px-4 py-2">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Now with Claude MCP Integration</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Badge>
          </motion.div>

          {/* Main Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold tracking-tight mb-6"
          >
            <span className="text-text-primary">Database Development</span>
            <br />
            <GradientText variant="purple" className="font-extrabold">
              Powered by AI
            </GradientText>
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg sm:text-xl md:text-2xl text-text-secondary max-w-3xl mx-auto mb-10 leading-relaxed"
          >
            The complete lifecycle platform for{' '}
            <span className="text-sqlserver font-medium">SQL Server</span> and{' '}
            <span className="text-postgresql font-medium">PostgreSQL</span>—from schema analysis to deployment.
            <br className="hidden sm:block" />
            <span className="text-text-muted">AI that understands your database the way you do.</span>
          </motion.p>

          {/* CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mb-16"
          >
            <Button asChild size="xl" variant="gradient">
              <Link href="/signup" className="group">
                <Zap className="w-5 h-5" />
                Start Free Trial
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </Button>
            <Button asChild size="xl" variant="secondary">
              <Link href="/demo" className="group">
                <Play className="w-5 h-5" />
                Watch Demo
              </Link>
            </Button>
          </motion.div>

          {/* Platform Badges */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="flex flex-col items-center gap-6"
          >
            <p className="text-sm text-text-muted">Works seamlessly with your database</p>
            <div className="flex flex-wrap items-center justify-center gap-6">
              <PlatformBadge
                name="PostgreSQL"
                icon={<PostgreSQLIcon />}
                color="postgresql"
              />
              <PlatformBadge
                name="SQL Server"
                icon={<SQLServerIcon />}
                color="sqlserver"
              />
              <PlatformBadge
                name="Azure SQL"
                icon={<AzureIcon />}
                color="primary"
              />
            </div>
          </motion.div>

          {/* Stats Row */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.7 }}
            className="mt-20 grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            <StatItem value="26+" label="AI Modules" />
            <StatItem value="10x" label="Faster Development" />
            <StatItem value="99.9%" label="Uptime SLA" />
            <StatItem value="5min" label="Setup Time" />
          </motion.div>
        </div>
      </div>

      {/* Bottom Gradient Fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-bg-surface to-transparent" />
    </section>
  );
}

function PlatformBadge({
  name,
  icon,
  color
}: {
  name: string;
  icon: React.ReactNode;
  color: 'postgresql' | 'sqlserver' | 'primary';
}) {
  const colorClasses = {
    postgresql: 'border-postgresql/30 bg-postgresql/5 hover:bg-postgresql/10',
    sqlserver: 'border-sqlserver/30 bg-sqlserver/5 hover:bg-sqlserver/10',
    primary: 'border-primary/30 bg-primary/5 hover:bg-primary/10',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -2 }}
      className={`flex items-center gap-3 px-5 py-3 rounded-xl border transition-colors ${colorClasses[color]}`}
    >
      <span className="w-8 h-8">{icon}</span>
      <span className="text-text-primary font-medium">{name}</span>
    </motion.div>
  );
}

function StatItem({ value, label }: { value: string; label: string }) {
  return (
    <div className="text-center">
      <div className="text-3xl md:text-4xl font-bold text-text-primary mb-1">
        <GradientText>{value}</GradientText>
      </div>
      <div className="text-sm text-text-muted">{label}</div>
    </div>
  );
}

function PostgreSQLIcon() {
  return (
    <svg viewBox="0 0 32 32" fill="none" className="w-full h-full">
      <circle cx="16" cy="16" r="14" stroke="#336791" strokeWidth="2" fill="none" />
      <path
        d="M16 8c-4.4 0-8 3.6-8 8s3.6 8 8 8 8-3.6 8-8-3.6-8-8-8zm0 14c-3.3 0-6-2.7-6-6s2.7-6 6-6 6 2.7 6 6-2.7 6-6 6z"
        fill="#336791"
        fillOpacity="0.3"
      />
      <circle cx="16" cy="16" r="3" fill="#336791" />
    </svg>
  );
}

function SQLServerIcon() {
  return (
    <svg viewBox="0 0 32 32" fill="none" className="w-full h-full">
      <path
        d="M16 6L6 11v10l10 5 10-5V11L16 6z"
        stroke="#CC2927"
        strokeWidth="2"
        fill="none"
      />
      <path d="M6 11l10 5 10-5M16 16v10" stroke="#CC2927" strokeWidth="2" />
      <circle cx="16" cy="11" r="2" fill="#CC2927" />
    </svg>
  );
}

function AzureIcon() {
  return (
    <svg viewBox="0 0 32 32" fill="none" className="w-full h-full">
      <path
        d="M10 8l6 16H8l8-12-4-4h8l-4 4 8 12h-8l6-16H10z"
        fill="#3b82f6"
        fillOpacity="0.8"
      />
    </svg>
  );
}
