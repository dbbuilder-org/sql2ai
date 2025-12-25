# SQL Test

**AI-Powered Database Testing Framework**

## Overview

SQL Test generates comprehensive behavioral tests using AI analysis combined with audit-based validation. It creates unit tests and integration tests using native testing frameworks for each database platform (tSQLt for SQL Server, pgTAP for PostgreSQL) and application-level testing frameworks.

## The Problem

### Current Database Testing Challenges

| Challenge | Reality | Impact |
|-----------|---------|--------|
| No test coverage | Most DBs have 0% | Regressions go unnoticed |
| Manual test creation | Time-consuming | Tests not written |
| Stored procedure testing | Complex setup | Skipped entirely |
| Data state management | Hard to reset | Flaky tests |
| Cross-procedure flows | Multi-step scenarios | Not tested |
| Performance regression | Not tracked | Gradual degradation |

## SQL Test Solution

### Test Generation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ANALYSIS ENGINE                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Schema    │  │  Procedure  │  │   Audit     │              │
│  │  Analysis   │  │   Logic     │  │    Logs     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    TEST GENERATION                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Behavior Inference  - Understand what code should do   │ │
│  │  2. Edge Case Detection - Identify boundary conditions     │ │
│  │  3. Test Case Creation  - Generate test scenarios          │ │
│  │  4. Fixture Generation  - Create test data                 │ │
│  │  5. Assertion Building  - Define expected outcomes         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: TEST SUITES                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   tSQLt     │  │   pgTAP     │  │   Jest/     │              │
│  │   Tests     │  │   Tests     │  │   PyTest    │              │
│  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## Test Types

### 1. Unit Tests (Stored Procedures)

**AI analyzes procedure and generates tests:**

```sql
-- Original Procedure
CREATE PROCEDURE dbo.Customer_UpdateStatus
    @CustomerId INT,
    @NewStatus VARCHAR(20)
AS
BEGIN
    IF NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerId = @CustomerId)
        THROW 50001, 'Customer not found', 1;

    IF @NewStatus NOT IN ('Active', 'Inactive', 'Suspended')
        THROW 50002, 'Invalid status', 1;

    UPDATE Customers
    SET Status = @NewStatus, ModifiedDate = GETUTCDATE()
    WHERE CustomerId = @CustomerId;
END;
```

**AI-Generated tSQLt Tests:**

```sql
-- Test Class
EXEC tSQLt.NewTestClass 'CustomerTests';

-- Test: Valid status update
CREATE PROCEDURE CustomerTests.[test Customer_UpdateStatus updates status correctly]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    INSERT INTO dbo.Customers (CustomerId, Status, ModifiedDate)
    VALUES (1, 'Active', '2024-01-01');

    -- Act
    EXEC dbo.Customer_UpdateStatus @CustomerId = 1, @NewStatus = 'Inactive';

    -- Assert
    DECLARE @ActualStatus VARCHAR(20);
    SELECT @ActualStatus = Status FROM dbo.Customers WHERE CustomerId = 1;

    EXEC tSQLt.AssertEquals 'Inactive', @ActualStatus;
END;

-- Test: Customer not found
CREATE PROCEDURE CustomerTests.[test Customer_UpdateStatus throws for missing customer]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    -- No customer inserted

    -- Act & Assert
    EXEC tSQLt.ExpectException @ExpectedMessage = 'Customer not found';
    EXEC dbo.Customer_UpdateStatus @CustomerId = 999, @NewStatus = 'Active';
END;

-- Test: Invalid status
CREATE PROCEDURE CustomerTests.[test Customer_UpdateStatus throws for invalid status]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    INSERT INTO dbo.Customers (CustomerId, Status) VALUES (1, 'Active');

    -- Act & Assert
    EXEC tSQLt.ExpectException @ExpectedMessage = 'Invalid status';
    EXEC dbo.Customer_UpdateStatus @CustomerId = 1, @NewStatus = 'InvalidValue';
END;

-- Test: ModifiedDate is updated
CREATE PROCEDURE CustomerTests.[test Customer_UpdateStatus updates ModifiedDate]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    INSERT INTO dbo.Customers (CustomerId, Status, ModifiedDate)
    VALUES (1, 'Active', '2024-01-01');

    -- Act
    EXEC dbo.Customer_UpdateStatus @CustomerId = 1, @NewStatus = 'Inactive';

    -- Assert
    DECLARE @ModifiedDate DATETIME2;
    SELECT @ModifiedDate = ModifiedDate FROM dbo.Customers WHERE CustomerId = 1;

    EXEC tSQLt.AssertEquals CAST(GETUTCDATE() AS DATE), CAST(@ModifiedDate AS DATE);
END;
```

### 2. PostgreSQL Tests (pgTAP)

```sql
-- AI-Generated pgTAP Tests
BEGIN;
SELECT plan(4);

-- Test: Valid status update
SELECT lives_ok(
    $$SELECT customer_update_status(1, 'Inactive')$$,
    'Should update status successfully'
);

-- Test: Customer not found
SELECT throws_ok(
    $$SELECT customer_update_status(999, 'Active')$$,
    'P0001',
    'Customer not found',
    'Should throw for missing customer'
);

-- Test: Invalid status
SELECT throws_ok(
    $$SELECT customer_update_status(1, 'InvalidValue')$$,
    'P0001',
    'Invalid status',
    'Should throw for invalid status'
);

-- Test: Return value
SELECT is(
    (SELECT customer_update_status(1, 'Active')),
    true,
    'Should return true on success'
);

SELECT * FROM finish();
ROLLBACK;
```

### 3. Integration Tests (Multi-Step Flows)

**AI detects procedure call chains and generates integration tests:**

```sql
-- Detected Flow: Order Processing
-- 1. Order_Create
-- 2. Order_AddItem (multiple)
-- 3. Order_CalculateTotal
-- 4. Order_Submit
-- 5. Inventory_Reserve

CREATE PROCEDURE IntegrationTests.[test Complete order flow reserves inventory]
AS
BEGIN
    -- Arrange: Set up test data
    EXEC tSQLt.FakeTable 'dbo.Orders';
    EXEC tSQLt.FakeTable 'dbo.OrderItems';
    EXEC tSQLt.FakeTable 'dbo.Products';
    EXEC tSQLt.FakeTable 'dbo.Inventory';

    INSERT INTO dbo.Products (ProductId, Name, Price) VALUES (1, 'Widget', 29.99);
    INSERT INTO dbo.Inventory (ProductId, Quantity) VALUES (1, 100);

    -- Act: Execute full flow
    DECLARE @OrderId INT;
    EXEC dbo.Order_Create @CustomerId = 1, @OrderId = @OrderId OUTPUT;
    EXEC dbo.Order_AddItem @OrderId = @OrderId, @ProductId = 1, @Quantity = 5;
    EXEC dbo.Order_CalculateTotal @OrderId = @OrderId;
    EXEC dbo.Order_Submit @OrderId = @OrderId;

    -- Assert: Inventory was reserved
    DECLARE @RemainingInventory INT;
    SELECT @RemainingInventory = Quantity FROM dbo.Inventory WHERE ProductId = 1;

    EXEC tSQLt.AssertEquals 95, @RemainingInventory;
END;
```

### 4. Constraint Tests

```sql
-- AI-Generated constraint tests
CREATE PROCEDURE ConstraintTests.[test Customers Email must be unique]
AS
BEGIN
    EXEC tSQLt.FakeTable 'dbo.Customers';
    EXEC tSQLt.ApplyConstraint 'dbo.Customers', 'UQ_Customers_Email';

    INSERT INTO dbo.Customers (Email) VALUES ('test@example.com');

    EXEC tSQLt.ExpectException;
    INSERT INTO dbo.Customers (Email) VALUES ('test@example.com');
END;

CREATE PROCEDURE ConstraintTests.[test Orders Total must be positive]
AS
BEGIN
    EXEC tSQLt.FakeTable 'dbo.Orders';
    EXEC tSQLt.ApplyConstraint 'dbo.Orders', 'CK_Orders_Total_Positive';

    EXEC tSQLt.ExpectException;
    INSERT INTO dbo.Orders (Total) VALUES (-100);
END;
```

### 5. Trigger Tests

```sql
-- AI-Generated trigger tests
CREATE PROCEDURE TriggerTests.[test Customer audit trigger logs changes]
AS
BEGIN
    -- Arrange
    EXEC tSQLt.FakeTable 'dbo.Customers';
    EXEC tSQLt.FakeTable 'dbo.CustomerAudit';
    EXEC tSQLt.ApplyTrigger 'dbo.Customers', 'TR_Customers_Audit';

    -- Act
    INSERT INTO dbo.Customers (CustomerId, Name) VALUES (1, 'Original');
    UPDATE dbo.Customers SET Name = 'Updated' WHERE CustomerId = 1;

    -- Assert
    DECLARE @AuditCount INT;
    SELECT @AuditCount = COUNT(*) FROM dbo.CustomerAudit;
    EXEC tSQLt.AssertEquals 2, @AuditCount;  -- INSERT + UPDATE
END;
```

### 6. Performance Tests

```sql
-- AI-Generated performance tests
CREATE PROCEDURE PerformanceTests.[test GetCustomerOrders completes in under 100ms]
AS
BEGIN
    -- Arrange: Create realistic data volume
    EXEC TestHelpers.CreateCustomers @Count = 10000;
    EXEC TestHelpers.CreateOrders @Count = 100000;

    -- Act & Measure
    DECLARE @StartTime DATETIME2 = SYSDATETIME();
    EXEC dbo.Customer_GetOrders @CustomerId = 5000;
    DECLARE @Duration INT = DATEDIFF(MILLISECOND, @StartTime, SYSDATETIME());

    -- Assert
    IF @Duration > 100
        EXEC tSQLt.Fail 'Procedure took ', @Duration, 'ms (max: 100ms)';
END;
```

## Audit-Based Test Generation

SQL Test analyzes query patterns from audit logs to generate realistic tests:

```
Audit Analysis:
  Procedure: dbo.Customer_GetOrders
  Calls (last 30 days): 1,247,893

  Parameter Distribution:
    @CustomerId: Range 1-50000, 80% between 1000-40000
    @StartDate: 95% within last 90 days
    @Status: 'Active'=72%, 'All'=25%, 'Inactive'=3%

  Generated Test Cases:
    1. Typical customer (ID in common range)
    2. Edge customer (ID at boundaries)
    3. Recent date range (common)
    4. Historical date range (edge case)
    5. Each status value
    6. NULL parameters where allowed
```

## Test Data Management

```yaml
# sql2ai-test.yaml
fixtures:
  baseline:
    source: sql2ai simulate  # Use synthetic data
    tables:
      - Customers: 1000
      - Products: 500
      - Orders: 5000

  reset_strategy: transaction  # Rollback after each test

  snapshots:
    enabled: true
    location: ./test_snapshots/
```

## CI/CD Integration

```yaml
# GitHub Actions
- name: Run SQL Tests
  run: |
    sql2ai test run --format junit --output test-results.xml

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results.xml
```

## Test Coverage Report

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL TEST COVERAGE REPORT                            ║
╠══════════════════════════════════════════════════════════════════╣
║ OVERALL COVERAGE: 78%                                            ║
╠══════════════════════════════════════════════════════════════════╣
║ BY OBJECT TYPE                                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ Stored Procedures:    85% (68/80 tested)                         ║
║ Functions:            92% (23/25 tested)                         ║
║ Triggers:             75% (6/8 tested)                           ║
║ Constraints:          70% (42/60 tested)                         ║
╠══════════════════════════════════════════════════════════════════╣
║ UNTESTED PROCEDURES (Critical)                                   ║
║ ─────────────────────────────────────────────────────────────── ║
║ ⚠ dbo.Payment_Process         - High complexity, no tests       ║
║ ⚠ dbo.Report_GenerateMonthly  - No tests                        ║
║ ⚠ dbo.User_ResetPassword      - Security-critical, no tests     ║
╠══════════════════════════════════════════════════════════════════╣
║ TEST RESULTS (Last Run)                                          ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Tests:    247                                              ║
║ Passed:         243                                              ║
║ Failed:         3                                                ║
║ Skipped:        1                                                ║
║ Duration:       45.2 seconds                                     ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Generate tests for all procedures
sql2ai test generate --all

# Generate tests for specific procedure
sql2ai test generate --procedure dbo.Customer_UpdateStatus

# Run all tests
sql2ai test run

# Run with coverage
sql2ai test run --coverage

# Run specific test class
sql2ai test run --class CustomerTests

# Generate from audit logs
sql2ai test generate --from-audit --days 30
```

## Integration Points

- **SQL Code**: Review test coverage in code reviews
- **SQL Simulate**: Generate test fixtures
- **SQL Orchestrator**: Schedule regular test runs
- **SQL Version**: Track test changes with code changes
