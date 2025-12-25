import { Metadata } from 'next';
import Link from 'next/link';
import { CTASection } from '../../../components/marketing';

export const metadata: Metadata = {
  title: 'SQL Test - AI-Powered Database Testing | SQL2.AI',
  description:
    'Generate and run database tests using tSQLt and pgTAP. AI-powered test generation, behavioral verification, and CI/CD integration.',
};

export default function TestPage(): JSX.Element {
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
              <div className="w-16 h-16 rounded-2xl bg-[#EF4444]/10 flex items-center justify-center text-[#EF4444]">
                <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <h1 className="text-h1 text-text-primary">SQL Test</h1>
                <p className="text-lg text-[#EF4444] font-medium">Database Testing</p>
              </div>
            </div>

            <p className="text-xl text-text-secondary mb-8">
              AI-powered test generation for SQL Server (tSQLt) and PostgreSQL (pgTAP).
              Unit tests, integration tests, and behavioral verification with full CI/CD integration.
            </p>
          </div>
        </div>
      </section>

      {/* Framework Support */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Native Testing Frameworks</h2>

          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🔷</div>
                <h3 className="text-h4 text-text-primary">tSQLt (SQL Server)</h3>
              </div>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• Unit tests for stored procedures</li>
                <li>• Table mocking and isolation</li>
                <li>• Constraint verification</li>
                <li>• Transaction rollback per test</li>
                <li>• XML/JUnit output for CI/CD</li>
              </ul>
            </div>

            <div className="card p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="text-3xl">🐘</div>
                <h3 className="text-h4 text-text-primary">pgTAP (PostgreSQL)</h3>
              </div>
              <ul className="space-y-2 text-text-secondary text-sm">
                <li>• TAP-compliant test output</li>
                <li>• Function and trigger testing</li>
                <li>• Schema verification</li>
                <li>• Role and permission tests</li>
                <li>• Parallel test execution</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* AI Test Generation */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">AI-Generated Tests</h2>
            <p className="text-text-secondary text-center mb-12">
              Automatically generate tests based on procedure logic and audit patterns
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`-- Input: GetCustomerOrders procedure

-- AI Generated tSQLt Tests:

EXEC tSQLt.NewTestClass 'GetCustomerOrdersTests';
GO

CREATE PROCEDURE GetCustomerOrdersTests.[test returns orders for valid customer]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    EXEC tSQLt.FakeTable 'dbo.Orders';

    INSERT INTO dbo.Customers (CustomerId, Name) VALUES (1, 'Test Customer');
    INSERT INTO dbo.Orders (OrderId, CustomerId, Total) VALUES (100, 1, 99.99);

    -- Act
    CREATE TABLE #Results (OrderId INT, Total MONEY);
    INSERT INTO #Results EXEC dbo.GetCustomerOrders @CustomerId = 1;

    -- Assert
    EXEC tSQLt.AssertEquals 1, (SELECT COUNT(*) FROM #Results);
    EXEC tSQLt.AssertEquals 99.99, (SELECT Total FROM #Results);
END;
GO

CREATE PROCEDURE GetCustomerOrdersTests.[test returns empty for invalid customer]
AS
BEGIN
    EXEC tSQLt.FakeTable 'dbo.Customers';
    EXEC tSQLt.FakeTable 'dbo.Orders';

    CREATE TABLE #Results (OrderId INT, Total MONEY);
    INSERT INTO #Results EXEC dbo.GetCustomerOrders @CustomerId = 999;

    EXEC tSQLt.AssertEquals 0, (SELECT COUNT(*) FROM #Results);
END;
GO`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Test Types */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <h2 className="text-h2 text-text-primary mb-12 text-center">Test Categories</h2>

          <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
            {[
              { title: 'Unit Tests', items: ['Procedure logic', 'Function returns', 'Trigger behavior', 'Constraint validation'] },
              { title: 'Integration Tests', items: ['Multi-step workflows', 'Transaction integrity', 'Cascade effects', 'Cross-schema operations'] },
              { title: 'Behavioral Tests', items: ['Audit trail verification', 'Permission enforcement', 'Error handling', 'Edge cases'] },
            ].map((category) => (
              <div key={category.title} className="card p-6">
                <h3 className="text-h5 text-text-primary mb-4">{category.title}</h3>
                <ul className="space-y-2 text-text-secondary text-sm">
                  {category.items.map((item) => (
                    <li key={item} className="flex items-center gap-2">
                      <svg className="w-4 h-4 text-[#EF4444] shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CI/CD Integration */}
      <section className="section">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-h2 text-text-primary mb-4 text-center">CI/CD Integration</h2>
            <p className="text-text-secondary text-center mb-12">
              Run tests in your pipeline with standard output formats
            </p>

            <div className="card p-6">
              <pre className="bg-bg-primary rounded-lg p-4 text-sm overflow-x-auto">
                <code className="text-text-secondary">{`# GitHub Actions workflow
name: Database Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Start SQL Server
        run: docker-compose up -d sqlserver

      - name: Run SQL Test
        run: |
          sql2ai test run \\
            --connection "\${{ secrets.DB_CONNECTION }}" \\
            --output junit \\
            --coverage

      - name: Publish Results
        uses: dorny/test-reporter@v1
        with:
          name: Database Tests
          path: test-results.xml
          reporter: java-junit

# Test Output:
# ✓ GetCustomerOrdersTests - 4 tests passed
# ✓ UpdateInventoryTests - 6 tests passed
# ✓ ProcessPaymentTests - 8 tests passed
# ────────────────────────────────────
# Total: 18 passed, 0 failed
# Coverage: 87% of procedures tested`}</code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Coverage Report */}
      <section className="section bg-bg-surface">
        <div className="container-wide">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-h2 text-text-primary mb-4">Test Coverage Analysis</h2>
            <p className="text-text-secondary mb-12">
              Track which procedures and code paths are tested
            </p>

            <div className="card p-6">
              <div className="grid md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#10B981]">87%</div>
                  <div className="text-sm text-text-muted">Procedures</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#10B981]">92%</div>
                  <div className="text-sm text-text-muted">Functions</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#F59E0B]">76%</div>
                  <div className="text-sm text-text-muted">Triggers</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-[#EF4444]">45%</div>
                  <div className="text-sm text-text-muted">Error Paths</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <CTASection
        title="Test Your Database Code"
        description="AI-generated tests for SQL Server and PostgreSQL with full CI/CD integration."
        primaryCTA={{ text: 'Start Free Trial', href: '/signup' }}
        secondaryCTA={{ text: 'View All Features', href: '/features/' }}
      />
    </>
  );
}
