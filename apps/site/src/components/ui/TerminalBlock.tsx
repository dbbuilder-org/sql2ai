'use client';

import { useState } from 'react';

interface TerminalCommand {
  prompt?: string;
  command: string;
  output?: string;
}

interface TerminalBlockProps {
  commands: TerminalCommand[];
  title?: string;
}

export function TerminalBlock({ commands, title = 'Terminal' }: TerminalBlockProps): JSX.Element {
  const [copied, setCopied] = useState(false);

  const copyCommands = (): void => {
    const text = commands.map((c) => c.command).join('\n');
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="terminal">
      {/* Terminal header */}
      <div className="terminal-header">
        <div className="flex items-center gap-2">
          <div className="terminal-dot bg-error" />
          <div className="terminal-dot bg-warning" />
          <div className="terminal-dot bg-success" />
        </div>
        <span className="text-xs text-text-muted">{title}</span>
        <button
          onClick={copyCommands}
          className="ml-auto text-xs text-text-muted hover:text-text-primary transition-colors"
        >
          {copied ? 'Copied!' : 'Copy'}
        </button>
      </div>

      {/* Terminal content */}
      <div className="terminal-content">
        {commands.map((cmd, index) => (
          <div key={index} className="mb-3 last:mb-0">
            <div className="flex items-start">
              <span className="text-success mr-2">{cmd.prompt || '$'}</span>
              <span className="text-text-primary">{cmd.command}</span>
            </div>
            {cmd.output && (
              <div className="mt-1 pl-4 text-text-secondary whitespace-pre-wrap">
                {cmd.output}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
