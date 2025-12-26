'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowUpRight, Check, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Badge } from '../ui';
import type { Module } from './modules-data';

interface ModuleCardProps {
  module: Module;
  size?: 'default' | 'large';
  index?: number;
}

export function ModuleCard({ module, size = 'default', index = 0 }: ModuleCardProps): JSX.Element {
  const isLarge = size === 'large';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration: 0.5, delay: index * 0.05 }}
    >
      <Link
        href={module.href}
        className={cn(
          'group relative block h-full rounded-2xl border border-border bg-bg-surface/50 backdrop-blur-sm',
          'transition-all duration-300',
          'hover:border-primary/50 hover:shadow-xl hover:shadow-primary/5 hover:-translate-y-1',
          module.comingSoon && 'opacity-70'
        )}
      >
        {/* Gradient Glow on Hover */}
        <div
          className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          style={{
            background: `radial-gradient(circle at 50% 0%, ${module.color}10 0%, transparent 50%)`,
          }}
        />

        <div className={cn('relative p-6', isLarge && 'p-8')}>
          {/* Coming Soon Badge */}
          {module.comingSoon && (
            <Badge variant="secondary" className="absolute top-4 right-4">
              <Clock className="w-3 h-3" />
              Coming Soon
            </Badge>
          )}

          {/* Icon and Title */}
          <div className="flex items-start gap-4 mb-4">
            <motion.div
              whileHover={{ scale: 1.1, rotate: 5 }}
              className={cn(
                'flex-shrink-0 rounded-xl flex items-center justify-center',
                isLarge ? 'w-14 h-14' : 'w-12 h-12'
              )}
              style={{
                backgroundColor: `${module.color}15`,
                color: module.color,
                boxShadow: `0 0 20px ${module.color}20`,
              }}
              dangerouslySetInnerHTML={{ __html: module.icon }}
            />
            <div className="flex-1 min-w-0">
              <h3 className={cn(
                'font-semibold text-text-primary group-hover:text-primary transition-colors',
                isLarge ? 'text-xl' : 'text-lg'
              )}>
                {module.name}
              </h3>
              <p
                className="text-sm font-medium mt-0.5"
                style={{ color: module.color }}
              >
                {module.tagline}
              </p>
            </div>
          </div>

          {/* Description */}
          <p className="text-sm text-text-secondary mb-4 line-clamp-2">
            {module.description}
          </p>

          {/* Capabilities */}
          <ul className="space-y-2 mb-4">
            {module.capabilities.slice(0, isLarge ? 5 : 3).map((capability, i) => (
              <motion.li
                key={capability}
                initial={{ opacity: 0, x: -10 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.1 + i * 0.05 }}
                className="flex items-start gap-2 text-xs text-text-muted"
              >
                <Check
                  className="w-3.5 h-3.5 shrink-0 mt-0.5"
                  style={{ color: module.color }}
                />
                <span>{capability}</span>
              </motion.li>
            ))}
          </ul>

          {/* Footer */}
          <div className="pt-4 border-t border-border/50 flex items-center justify-between">
            <span
              className="text-sm font-medium flex items-center gap-1 group-hover:gap-2 transition-all"
              style={{ color: module.color }}
            >
              Learn more
              <ArrowUpRight className="w-4 h-4" />
            </span>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export function ModuleGrid({ children, className }: { children: React.ReactNode; className?: string }): JSX.Element {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6', className)}>
      {children}
    </div>
  );
}

