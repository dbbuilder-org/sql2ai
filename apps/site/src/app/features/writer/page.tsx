import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Writer - AI-Powered DDL & Stored Procedure Generation | SQL2.AI',
  description:
    'Generate complete stored procedures, views, and functions with proper error handling, transactions, and security. Beyond text-to-SQL.',
};

export default function WriterPage(): JSX.Element {
  return (
    <>
      {/* Hero */}
      <section className="pt-32 pb-16 md:pt-40 md:pb-20">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <Link
              href="/features/"
              className="inline-flex items-center gap-2 text-small text-text-muted hover:text-text-secondary mb-6"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              All Modules
            </Link>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-2xl bg-secondary/10 flex items-center justify-center text-secondary">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Writer</h1>
                <p className="text-lg text-secondary font-medium">AI DDL & Code Generation</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              Beyond simple text-to-SQL. Generate complete stored procedures, views, and functions
              with proper error handling, transactions, audit trails, and security best practices.
            </p>
          </div>
        </div>
      </section>

      {/* The Difference */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Beyond Text-to-SQL</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            <div className="card p-6 border-error/30">
              <h3 className="text-h5 text-error mb-4">Traditional AI SQL Tools</h3>
              <p className="text-text-secondary mb-4">
                &quot;Show me sales by region&quot;
              </p>
              <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto mb-4">
                <code className="text-text-secondary">{`SELECT region, SUM(amount)
FROM sales
GROUP BY region`}</code>
              </pre>
              <ul className="space-y-2 text-small text-text-muted">
                <li className="flex items-center gap-2">
                  <span className="text-error">✗</span> Only generates SELECT queries
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-error">✗</span> No error handling
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-error">✗</span> No transaction support
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-error">✗</span> No business logic
                </li>
              </ul>
            </div>

            <div className="card p-6 border-success/30">
              <h3 className="text-h5 text-success mb-4">SQL Writer</h3>
              <p className="text-text-secondary mb-4">
                &quot;Create a fund transfer procedure with overdraft protection&quot;
              </p>
              <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto mb-4">
                <code className="text-text-secondary">{`CREATE PROCEDURE TransferFunds
  @FromAccount INT,
  @ToAccount INT,
  @Amount DECIMAL(18,2)
AS
BEGIN
  SET XACT_ABORT ON;
  BEGIN TRY
    BEGIN TRANSACTION;
    -- Validation, locking, audit...
    COMMIT;
  END TRY
  BEGIN CATCH
    ROLLBACK;
    THROW;
  END CATCH
END`}</code>
              </pre>
              <ul className="space-y-2 text-small text-text-muted">
                <li className="flex items-center gap-2">
                  <span className="text-success">✓</span> Complete stored procedures
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-success">✓</span> Proper error handling
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-success">✓</span> Transaction management
                </li>
                <li className="flex items-center gap-2">
                  <span className="text-success">✓</span> Business logic built-in
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* What It Generates */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">What SQL Writer Generates</h2>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">DDL Statements</h3>
              <ul className="space-y-2 text-text-secondary">
                <li>CREATE TABLE with constraints</li>
                <li>Indexes (covering, filtered)</li>
                <li>Foreign key relationships</li>
                <li>Check constraints</li>
                <li>Default values</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Stored Procedures</h3>
              <ul className="space-y-2 text-text-secondary">
                <li>CRUD operations</li>
                <li>Business workflows</li>
                <li>Batch processing</li>
                <li>Error handling</li>
                <li>Audit logging</li>
              </ul>
            </div>

            <div className="card p-6">
              <h3 className="text-h5 text-text-primary mb-3">Views & Functions</h3>
              <ul className="space-y-2 text-text-secondary">
                <li>Indexed views</li>
                <li>Security views</li>
                <li>Scalar functions</li>
                <li>Table-valued functions</li>
                <li>Aggregate functions</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Example */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">Real-World Example</h2>
            <p className="text-text-secondary text-center mb-12">
              From natural language to production-ready code
            </p>

            <div className="space-y-6">
              <div className="card p-6">
                <h3 className="text-h6 text-text-primary mb-3">Your Request</h3>
                <p className="text-text-secondary italic">
                  &quot;Create a stored procedure to transfer funds between accounts with proper locking,
                  audit trail, and overdraft protection. It should validate both accounts exist
                  and the source has sufficient funds.&quot;
                </p>
              </div>

              <div className="card p-6">
                <h3 className="text-h6 text-text-primary mb-3">Generated Output</h3>
                <pre className="bg-bg-surface rounded-lg p-4 text-sm overflow-x-auto">
                  <code className="text-text-secondary">{`CREATE PROCEDURE dbo.TransferFunds
    @SourceAccountId INT,
    @TargetAccountId INT,
    @Amount DECIMAL(18,2),
    @TransferReference NVARCHAR(100) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @SourceBalance DECIMAL(18,2);
    DECLARE @TransferId INT;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Acquire locks in consistent order
        SELECT @SourceBalance = Balance
        FROM dbo.Accounts WITH (UPDLOCK, HOLDLOCK)
        WHERE AccountId = @SourceAccountId;

        IF @SourceBalance IS NULL
            THROW 50001, 'Source account not found', 1;

        IF NOT EXISTS (SELECT 1 FROM dbo.Accounts
                       WHERE AccountId = @TargetAccountId)
            THROW 50002, 'Target account not found', 1;

        IF @SourceBalance < @Amount
            THROW 50003, 'Insufficient funds', 1;

        -- Perform transfer
        UPDATE dbo.Accounts
        SET Balance = Balance - @Amount
        WHERE AccountId = @SourceAccountId;

        UPDATE dbo.Accounts
        SET Balance = Balance + @Amount
        WHERE AccountId = @TargetAccountId;

        -- Audit trail
        INSERT INTO dbo.TransferLog
            (SourceAccountId, TargetAccountId,
             Amount, Reference, TransferDate)
        VALUES
            (@SourceAccountId, @TargetAccountId,
             @Amount, @TransferReference, GETUTCDATE());

        SET @TransferId = SCOPE_IDENTITY();

        COMMIT TRANSACTION;

        SELECT @TransferId AS TransferId,
               'Success' AS Status;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;
    END CATCH
END;`}</code>
                </pre>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="section">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Built-In Best Practices</h2>

          <div className="grid md:grid-cols-4 gap-6 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center text-secondary mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Secure by Default</h3>
              <p className="text-small text-text-muted">Parameterized queries, no SQL injection</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center text-secondary mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Transaction Aware</h3>
              <p className="text-small text-text-muted">Proper BEGIN/COMMIT/ROLLBACK handling</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center text-secondary mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Error Handling</h3>
              <p className="text-small text-text-muted">TRY/CATCH with proper cleanup</p>
            </div>

            <div className="text-center">
              <div className="w-14 h-14 rounded-full bg-secondary/10 flex items-center justify-center text-secondary mx-auto mb-4">
                <svg className="w-7 h-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                  />
                </svg>
              </div>
              <h3 className="text-h6 text-text-primary mb-2">Audit Ready</h3>
              <p className="text-small text-text-muted">Built-in logging and tracking</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Ready to Write SQL the Smart Way?"
        description="Generate production-ready stored procedures, not just SELECT statements."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
