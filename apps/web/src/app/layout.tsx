import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'SQL2.AI - Dashboard',
  description: 'AI-Driven Database Development Platform',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
