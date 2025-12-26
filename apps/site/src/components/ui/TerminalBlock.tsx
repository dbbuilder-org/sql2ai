'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface TerminalCommand {
  prompt?: string;
  command: string;
  output?: string;
}

interface TerminalBlockProps {
  commands: TerminalCommand[];
  title?: string;
  className?: string;
}

export function TerminalBlock({ commands, title = 'Terminal', className }: TerminalBlockProps): JSX.Element {
  const [copied, setCopied] = useState(false);

  const copyCommands = (): void => {
    const text = commands.map((c) => c.command).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      className={cn(
        'rounded-2xl border border-border bg-bg-base/80 backdrop-blur-sm overflow-hidden shadow-2xl shadow-black/20',
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
    >
      {/* Terminal header */}
      <div className="flex items-center justify-between px-4 py-3 bg-bg-surface/50 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-error/80" />
          <div className="w-3 h-3 rounded-full bg-warning/80" />
          <div className="w-3 h-3 rounded-full bg-success/80" />
        </div>
        <span className="text-xs text-text-muted font-mono">{title}</span>
        <button
          onClick={copyCommands}
          className="text-xs text-text-muted hover:text-text-primary transition-colors px-2 py-1 rounded hover:bg-bg-elevated"
        >
          {copied ? (
            <span className="text-success">Copied!</span>
          ) : (
            'Copy'
          )}
        </button>
      </div>

      {/* Terminal content */}
      <div className="p-4 font-mono text-sm">
        {commands.map((cmd, index) => (
          <motion.div
            key={index}
            className="mb-3 last:mb-0"
            initial={{ opacity: 0, x: -10 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <div className="flex items-start">
              <span className="text-success mr-2 select-none">{cmd.prompt || '$'}</span>
              <span className="text-text-primary">{cmd.command}</span>
            </div>
            {cmd.output && (
              <div className="mt-1 pl-4 text-text-secondary whitespace-pre-wrap">
                {cmd.output}
              </div>
            )}
          </motion.div>
        ))}
        <motion.span
          className="inline-block w-2 h-4 bg-primary ml-4"
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        />
      </div>
    </motion.div>
  );
}
