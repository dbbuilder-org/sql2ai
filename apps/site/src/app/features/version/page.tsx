import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Version - Git for Your Database | SQL2.AI',
  description:
    'Track every change to every database object. Full history, blame, diff, and rollback for stored procedures, views, and functions.',
};

export default function VersionPage(): JSX.Element {
  return (
    <>
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link href="/features/" className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-warning/10 flex items-center justify-center text-warning">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Version</h1>
                <p className="text-lg text-warning font-medium">Git for Your Database</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Finally, proper version control for database objects. Track every stored procedure,
              view, and function with full history, blame, and diff capabilities.
            </p>
          </div>
        </div>
      </section>

      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Key Capabilities</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Version History</h3>
              <p className="text-text-secondary">Track every version of every object. See who changed what and when.</p>
            </div>
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Diff & Blame</h3>
              <p className="text-text-secondary">Compare any two versions. Line-by-line attribution for every change.</p>
            </div>
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Branch Support</h3>
              <p className="text-text-secondary">Track different versions across dev, staging, and production.</p>
            </div>
          </div>
        </div>
      </section>

      <CTASection
        title="Ready for Database Version Control?"
        description="Never lose track of database changes again."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
