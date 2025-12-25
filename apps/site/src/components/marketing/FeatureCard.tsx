import Link from 'next/link';

interface FeatureCardProps {
  title: string;
  description: string;
  icon: JSX.Element;
  href?: string;
  highlights?: string[];
}

export function FeatureCard({
  title,
  description,
  icon,
  href,
  highlights,
}: FeatureCardProps): JSX.Element {
  const content = (
    <>
      <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center text-primary mb-4">
        {icon}
      </div>
      <h3 className="text-h5 text-text-primary mb-2">{title}</h3>
      <p className="text-small text-text-secondary mb-4">{description}</p>
      {highlights && (
        <ul className="space-y-2">
          {highlights.map((highlight) => (
            <li key={highlight} className="flex items-center gap-2 text-xs text-text-muted">
              <svg className="w-3 h-3 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
              </svg>
              {highlight}
            </li>
          ))}
        </ul>
      )}
      {href && (
        <div className="mt-4 pt-4 border-t border-border-subtle">
          <span className="text-small text-primary font-medium group-hover:underline">
            Learn more →
          </span>
        </div>
      )}
    </>
  );

  if (href) {
    return (
      <Link href={href} className="card p-6 hover:border-primary transition-colors group">
        {content}
      </Link>
    );
  }

  return <div className="card p-6">{content}</div>;
}

export function FeatureGrid({ children }: { children: React.ReactNode }): JSX.Element {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {children}
    </div>
  );
}
