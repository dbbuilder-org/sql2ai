'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg-primary">
      <div className="text-center space-y-6 p-8 max-w-md">
        <div className="space-y-2">
          <h1 className="text-6xl font-bold text-primary">Oops!</h1>
          <h2 className="text-2xl font-semibold text-text-primary">
            Something went wrong
          </h2>
        </div>
        <p className="text-text-secondary">
          We've been notified about this issue and are working on a fix.
        </p>
        <div className="flex gap-4 justify-center pt-4">
          <button
            onClick={reset}
            className="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            Try Again
          </button>
          <Link
            href="/"
            className="px-6 py-3 border border-border rounded-lg hover:bg-bg-surface transition-colors"
          >
            Go Home
          </Link>
        </div>
        {error.digest && (
          <p className="text-xs text-text-muted">Error ID: {error.digest}</p>
        )}
      </div>
    </div>
  );
}
