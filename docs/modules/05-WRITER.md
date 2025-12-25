# SQL Writer

**Module 5 of 8** | **Status:** Planned | **Priority:** P1

## Overview

SQL Writer is an AI-powered code generation engine that goes beyond simple text-to-SQL. While other tools generate SELECT queries for data analysis, SQL Writer creates complete DDL, stored procedures, views, functions, and triggers with proper error handling, transactions, and security.

## The Key Differentiator

### Other AI SQL Tools
```
Input: "Show me sales by region"
Output: SELECT Region, SUM(Sales) FROM Orders GROUP BY Region
```

### SQL Writer
```
Input: "Create a customer onboarding workflow with welcome email trigger,
        initial loyalty points, and audit logging"

Output: Complete implementation including:
- Stored procedure with TRY/CATCH
- Transaction management
- Audit logging
- Welcome email queue insert
- Loyalty points initialization
- Input validation
- Error handling
- Rollback on failure
```

## Capabilities

### 1. DDL Generation

**Create Tables**
```
Input: "Create a table for tracking customer loyalty points with history"

Output:
CREATE TABLE dbo.LoyaltyPoints (
    LoyaltyID INT IDENTITY(1,1) PRIMARY KEY,
    CustomerID INT NOT NULL,
    Points INT NOT NULL DEFAULT 0,
    Tier AS (CASE
        WHEN Points >= 10000 THEN 'Platinum'
        WHEN Points >= 5000 THEN 'Gold'
        WHEN Points >= 1000 THEN 'Silver'
        ELSE 'Bronze'
    END) PERSISTED,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),

    CONSTRAINT FK_LoyaltyPoints_Customer
        FOREIGN KEY (CustomerID) REFERENCES dbo.Customers(CustomerID),
    CONSTRAINT CK_LoyaltyPoints_Positive
        CHECK (Points >= 0)
);

CREATE TABLE dbo.LoyaltyPointsHistory (
    HistoryID BIGINT IDENTITY(1,1) PRIMARY KEY,
    LoyaltyID INT NOT NULL,
    PointsChange INT NOT NULL,
    Reason NVARCHAR(200) NOT NULL,
    OrderID INT NULL,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CreatedBy NVARCHAR(128) NOT NULL DEFAULT SUSER_SNAME(),

    CONSTRAINT FK_LoyaltyHistory_Loyalty
        FOREIGN KEY (LoyaltyID) REFERENCES dbo.LoyaltyPoints(LoyaltyID)
);

CREATE INDEX IX_LoyaltyPoints_Customer ON dbo.LoyaltyPoints(CustomerID);
CREATE INDEX IX_LoyaltyHistory_Loyalty ON dbo.LoyaltyPointsHistory(LoyaltyID, CreatedAt);
```

### 2. Stored Procedure Generation

**Complex Business Logic**
```
Input: "Create a procedure to transfer funds between accounts with proper
        locking, audit trail, overdraft protection, and notifications"

Output:
CREATE PROCEDURE dbo.sp_TransferFunds
    @FromAccountID INT,
    @ToAccountID INT,
    @Amount DECIMAL(18,2),
    @Description NVARCHAR(200) = NULL,
    @TransferID INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Input validation
    IF @Amount <= 0
    BEGIN
        RAISERROR('Transfer amount must be positive', 16, 1);
        RETURN -1;
    END

    IF @FromAccountID = @ToAccountID
    BEGIN
        RAISERROR('Cannot transfer to same account', 16, 1);
        RETURN -1;
    END

    DECLARE @FromBalance DECIMAL(18,2);
    DECLARE @TransactionID UNIQUEIDENTIFIER = NEWID();

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Lock accounts in consistent order to prevent deadlocks
        IF @FromAccountID < @ToAccountID
        BEGIN
            SELECT @FromBalance = Balance
            FROM dbo.Accounts WITH (UPDLOCK, HOLDLOCK)
            WHERE AccountID = @FromAccountID;

            SELECT 1
            FROM dbo.Accounts WITH (UPDLOCK, HOLDLOCK)
            WHERE AccountID = @ToAccountID;
        END
        ELSE
        BEGIN
            SELECT 1
            FROM dbo.Accounts WITH (UPDLOCK, HOLDLOCK)
            WHERE AccountID = @ToAccountID;

            SELECT @FromBalance = Balance
            FROM dbo.Accounts WITH (UPDLOCK, HOLDLOCK)
            WHERE AccountID = @FromAccountID;
        END

        -- Check sufficient funds
        IF @FromBalance < @Amount
        BEGIN
            RAISERROR('Insufficient funds for transfer', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN -2;
        END

        -- Perform transfer
        UPDATE dbo.Accounts
        SET Balance = Balance - @Amount,
            UpdatedAt = GETUTCDATE()
        WHERE AccountID = @FromAccountID;

        UPDATE dbo.Accounts
        SET Balance = Balance + @Amount,
            UpdatedAt = GETUTCDATE()
        WHERE AccountID = @ToAccountID;

        -- Record transfer
        INSERT INTO dbo.Transfers (
            TransactionID, FromAccountID, ToAccountID,
            Amount, Description, Status, CreatedAt
        )
        VALUES (
            @TransactionID, @FromAccountID, @ToAccountID,
            @Amount, @Description, 'Completed', GETUTCDATE()
        );

        SET @TransferID = SCOPE_IDENTITY();

        -- Audit logging
        INSERT INTO dbo.AuditLog (
            EntityType, EntityID, Action, Details, CreatedAt
        )
        VALUES (
            'Transfer', @TransferID, 'Create',
            CONCAT('Amount: ', @Amount, ' from ', @FromAccountID, ' to ', @ToAccountID),
            GETUTCDATE()
        );

        -- Queue notification
        INSERT INTO dbo.NotificationQueue (
            Type, RecipientID, Subject, Body, Status
        )
        SELECT
            'TransferComplete',
            c.CustomerID,
            'Transfer Completed',
            CONCAT('Your transfer of $', @Amount, ' has been completed.'),
            'Pending'
        FROM dbo.Accounts a
        JOIN dbo.Customers c ON a.CustomerID = c.CustomerID
        WHERE a.AccountID = @FromAccountID;

        COMMIT TRANSACTION;
        RETURN 0;

    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        -- Log error
        INSERT INTO dbo.ErrorLog (
            ProcedureName, ErrorNumber, ErrorMessage,
            ErrorLine, Parameters, CreatedAt
        )
        VALUES (
            'sp_TransferFunds',
            ERROR_NUMBER(),
            ERROR_MESSAGE(),
            ERROR_LINE(),
            CONCAT('@From=', @FromAccountID, ',@To=', @ToAccountID, ',@Amt=', @Amount),
            GETUTCDATE()
        );

        THROW;
    END CATCH
END
```

### 3. View Generation

```
Input: "Create a view for customer order summary with lifetime value calculation"

Output:
CREATE VIEW dbo.vw_CustomerOrderSummary
WITH SCHEMABINDING
AS
SELECT
    c.CustomerID,
    c.Email,
    c.Name,
    COUNT_BIG(o.OrderID) AS TotalOrders,
    ISNULL(SUM(o.TotalAmount), 0) AS LifetimeValue,
    ISNULL(AVG(o.TotalAmount), 0) AS AverageOrderValue,
    MIN(o.OrderDate) AS FirstOrderDate,
    MAX(o.OrderDate) AS LastOrderDate,
    DATEDIFF(DAY, MAX(o.OrderDate), GETDATE()) AS DaysSinceLastOrder,
    CASE
        WHEN COUNT(o.OrderID) >= 20 THEN 'VIP'
        WHEN COUNT(o.OrderID) >= 10 THEN 'Regular'
        WHEN COUNT(o.OrderID) >= 1 THEN 'New'
        ELSE 'Prospect'
    END AS CustomerSegment
FROM dbo.Customers c
LEFT JOIN dbo.Orders o ON c.CustomerID = o.CustomerID
    AND o.Status = 'Completed'
GROUP BY c.CustomerID, c.Email, c.Name;
GO

-- Indexed view for performance
CREATE UNIQUE CLUSTERED INDEX IX_CustomerOrderSummary
ON dbo.vw_CustomerOrderSummary(CustomerID);
```

### 4. Function Generation

```
Input: "Create a function to calculate shipping cost based on weight,
        distance, and shipping method with volume discounts"

Output:
CREATE FUNCTION dbo.fn_CalculateShipping (
    @WeightKg DECIMAL(10,2),
    @DistanceKm INT,
    @Method NVARCHAR(20),
    @IsVolumeCustomer BIT = 0
)
RETURNS DECIMAL(10,2)
WITH SCHEMABINDING
AS
BEGIN
    DECLARE @BaseCost DECIMAL(10,2);
    DECLARE @WeightCost DECIMAL(10,2);
    DECLARE @DistanceCost DECIMAL(10,2);
    DECLARE @Total DECIMAL(10,2);

    -- Base cost by method
    SET @BaseCost = CASE @Method
        WHEN 'Express' THEN 15.00
        WHEN 'Standard' THEN 8.00
        WHEN 'Economy' THEN 4.00
        ELSE 10.00
    END;

    -- Weight cost (per kg over 1kg)
    SET @WeightCost = CASE
        WHEN @WeightKg <= 1 THEN 0
        WHEN @WeightKg <= 5 THEN (@WeightKg - 1) * 2.00
        WHEN @WeightKg <= 20 THEN 8.00 + (@WeightKg - 5) * 1.50
        ELSE 30.50 + (@WeightKg - 20) * 1.00
    END;

    -- Distance cost (per 100km)
    SET @DistanceCost = (@DistanceKm / 100.0) * CASE @Method
        WHEN 'Express' THEN 3.00
        WHEN 'Standard' THEN 1.50
        WHEN 'Economy' THEN 0.75
        ELSE 2.00
    END;

    SET @Total = @BaseCost + @WeightCost + @DistanceCost;

    -- Volume discount
    IF @IsVolumeCustomer = 1
        SET @Total = @Total * 0.85;

    RETURN ROUND(@Total, 2);
END
```

### 5. Trigger Generation

```
Input: "Create a trigger to maintain order history and prevent deletion
        of orders with payments"

Output:
CREATE TRIGGER dbo.tr_Orders_AuditAndProtect
ON dbo.Orders
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Prevent deletion of orders with payments
    IF EXISTS (SELECT 1 FROM deleted) AND NOT EXISTS (SELECT 1 FROM inserted)
    BEGIN
        IF EXISTS (
            SELECT 1
            FROM deleted d
            JOIN dbo.Payments p ON d.OrderID = p.OrderID
            WHERE p.Status = 'Completed'
        )
        BEGIN
            RAISERROR('Cannot delete orders with completed payments', 16, 1);
            ROLLBACK TRANSACTION;
            RETURN;
        END
    END

    -- Record history for all changes
    INSERT INTO dbo.OrderHistory (
        OrderID, Action, OldStatus, NewStatus,
        OldAmount, NewAmount, ChangedAt, ChangedBy
    )
    SELECT
        COALESCE(i.OrderID, d.OrderID),
        CASE
            WHEN d.OrderID IS NULL THEN 'INSERT'
            WHEN i.OrderID IS NULL THEN 'DELETE'
            ELSE 'UPDATE'
        END,
        d.Status,
        i.Status,
        d.TotalAmount,
        i.TotalAmount,
        GETUTCDATE(),
        SUSER_SNAME()
    FROM inserted i
    FULL OUTER JOIN deleted d ON i.OrderID = d.OrderID;
END
```

## AI Context Awareness

SQL Writer understands:

1. **Schema Context** - Knows existing tables, relationships, constraints
2. **Code Patterns** - Learns from existing procedures in your database
3. **Business Rules** - Infers rules from existing implementations
4. **Security Requirements** - Applies appropriate permissions and validation
5. **Performance Patterns** - Uses efficient patterns (set-based, proper indexing)

## API Endpoints

```
POST   /api/writer/generate/table       # Generate table DDL
POST   /api/writer/generate/procedure   # Generate stored procedure
POST   /api/writer/generate/view        # Generate view
POST   /api/writer/generate/function    # Generate function
POST   /api/writer/generate/trigger     # Generate trigger
POST   /api/writer/generate/index       # Generate index recommendations

POST   /api/writer/refactor             # Refactor existing code
POST   /api/writer/explain              # Explain existing code
```

## CLI Commands

```bash
sql2ai write "Create a table for..." --type table
sql2ai write "Create a procedure to..." --type procedure
sql2ai write --file requirements.txt --output ./generated

sql2ai refactor --file old-proc.sql --style modern
sql2ai explain --file complex-query.sql
```

## Implementation Status

- [ ] Core library structure (libs/sql-writer)
- [ ] LLM integration
- [ ] Table DDL generator
- [ ] Stored procedure generator
- [ ] View generator
- [ ] Function generator
- [ ] Trigger generator
- [ ] Schema context provider
- [ ] Code pattern learning
- [ ] Security rules
- [ ] Performance patterns
- [ ] API routers
- [ ] CLI commands
