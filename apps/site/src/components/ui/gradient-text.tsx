'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';

interface GradientTextProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'purple' | 'cyan' | 'rainbow';
  animate?: boolean;
}

export function GradientText({
  children,
  className,
  variant = 'default',
  animate = false,
}: GradientTextProps) {
  const gradients = {
    default: 'from-primary via-blue-400 to-cyan-400',
    purple: 'from-primary via-purple-500 to-pink-500',
    cyan: 'from-cyan-400 via-blue-500 to-purple-500',
    rainbow: 'from-red-500 via-yellow-500 to-green-500',
  };

  return (
    <span
      className={cn(
        'bg-gradient-to-r bg-clip-text text-transparent',
        gradients[variant],
        animate && 'animate-gradient bg-[length:200%_auto]',
        className
      )}
    >
      {children}
    </span>
  );
}
