'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MDXContentProps {
  content: string;
}

export function MDXContent({ content }: MDXContentProps) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        h1: ({ children }) => <h1 className="text-h2 mt-12 mb-6 first:mt-0">{children}</h1>,
        h2: ({ children }) => <h2 className="text-h3 mt-10 mb-4">{children}</h2>,
        h3: ({ children }) => <h3 className="text-h4 mt-8 mb-3">{children}</h3>,
        h4: ({ children }) => <h4 className="text-h5 mt-6 mb-2">{children}</h4>,
        p: ({ children }) => <p className="text-text-secondary mb-6 leading-relaxed">{children}</p>,
        ul: ({ children }) => <ul className="list-disc list-inside mb-6 space-y-2">{children}</ul>,
        ol: ({ children }) => (
          <ol className="list-decimal list-inside mb-6 space-y-2">{children}</ol>
        ),
        li: ({ children }) => <li className="text-text-secondary">{children}</li>,
        a: ({ href, children }) => (
          <a
            href={href}
            className="text-primary hover:underline"
            target={href?.startsWith('http') ? '_blank' : undefined}
            rel={href?.startsWith('http') ? 'noopener noreferrer' : undefined}
          >
            {children}
          </a>
        ),
        blockquote: ({ children }) => (
          <blockquote className="border-l-4 border-primary pl-6 my-6 italic text-text-muted">
            {children}
          </blockquote>
        ),
        code: ({ className, children }) => {
          const isInline = !className;
          if (isInline) {
            return (
              <code className="bg-bg-surface px-2 py-1 rounded text-sm font-mono text-primary">
                {children}
              </code>
            );
          }
          return (
            <code className="block bg-bg-surface p-4 rounded-lg overflow-x-auto text-sm font-mono">
              {children}
            </code>
          );
        },
        pre: ({ children }) => (
          <pre className="bg-bg-surface p-4 rounded-lg overflow-x-auto mb-6 text-sm">{children}</pre>
        ),
        table: ({ children }) => (
          <div className="overflow-x-auto mb-6">
            <table className="min-w-full divide-y divide-border">{children}</table>
          </div>
        ),
        thead: ({ children }) => <thead className="bg-bg-surface">{children}</thead>,
        th: ({ children }) => (
          <th className="px-4 py-3 text-left text-sm font-medium text-text-primary">{children}</th>
        ),
        td: ({ children }) => (
          <td className="px-4 py-3 text-sm text-text-secondary border-t border-border">
            {children}
          </td>
        ),
        hr: () => <hr className="border-border my-8" />,
        img: ({ src, alt }) => (
          <figure className="my-8">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={alt || ''} className="rounded-lg w-full" />
            {alt && <figcaption className="text-center text-sm text-text-muted mt-2">{alt}</figcaption>}
          </figure>
        ),
      }}
    >
      {content}
    </ReactMarkdown>
  );
}
