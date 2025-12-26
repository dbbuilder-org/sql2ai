import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Performance Monitoring - lower sample rate for marketing site
  tracesSampleRate: 0.05,

  // Environment
  environment: process.env.NODE_ENV,

  // Release tracking
  release: process.env.NEXT_PUBLIC_RENDER_GIT_COMMIT || 'development',

  // Only enable in production
  enabled: process.env.NODE_ENV === 'production',

  // Ignore common non-actionable errors
  ignoreErrors: [
    'Network request failed',
    'Failed to fetch',
    'Load failed',
    'ResizeObserver loop',
    'AbortError',
  ],
});
