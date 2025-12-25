import type { Metadata } from 'next';
import { Header } from '../components/layout/Header';
import { Footer } from '../components/layout/Footer';
import { DatabaseDialectProvider } from '../contexts/DatabaseDialectContext';
import './globals.css';

export const metadata: Metadata = {
  title: {
    default: 'SQL2.AI - AI-Driven Database Development',
    template: '%s | SQL2.AI',
  },
  description:
    'Transform your database development with AI. The complete lifecycle platform for SQL Server and PostgreSQL—from schema analysis to deployment.',
  keywords: [
    'SQL',
    'AI',
    'database',
    'PostgreSQL',
    'SQL Server',
    'schema analysis',
    'query optimization',
    'database migrations',
    'MCP',
    'Claude',
  ],
  authors: [{ name: 'SQL2.AI' }],
  creator: 'SQL2.AI',
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://sql2.ai',
    siteName: 'SQL2.AI',
    title: 'SQL2.AI - AI-Driven Database Development',
    description: 'The complete lifecycle platform for SQL Server and PostgreSQL',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: 'SQL2.AI',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SQL2.AI - AI-Driven Database Development',
    description: 'The complete lifecycle platform for SQL Server and PostgreSQL',
    images: ['/og-image.png'],
    creator: '@sql2ai',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-bg-base text-text-primary antialiased">
        <DatabaseDialectProvider>
          <Header />
          <main>{children}</main>
          <Footer />
        </DatabaseDialectProvider>
      </body>
    </html>
  );
}
