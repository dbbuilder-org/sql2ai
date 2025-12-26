-- ============================================================================
-- SQL2.AI Sample Database Seed Script
-- Creates sample tables and data for demonstration and testing
-- Compatible with SQL Server and PostgreSQL (with minor adjustments)
-- ============================================================================

-- ============================================================================
-- Create Tables
-- ============================================================================

-- Customers table
CREATE TABLE Customers (
    CustomerId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerName NVARCHAR(100) NOT NULL,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    Address NVARCHAR(500),
    City NVARCHAR(100),
    State NVARCHAR(50),
    PostalCode VARCHAR(20),
    Country NVARCHAR(100) DEFAULT 'USA',
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    UpdatedAt DATETIME2,
    IsActive BIT NOT NULL DEFAULT 1,
    CONSTRAINT CHK_Email CHECK (Email LIKE '%@%.%')
);

-- Create index on frequently queried columns
CREATE INDEX IX_Customers_Email ON Customers(Email);
CREATE INDEX IX_Customers_IsActive ON Customers(IsActive) INCLUDE (CustomerName, Email);

-- Products table
CREATE TABLE Products (
    ProductId INT IDENTITY(1,1) PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    SKU VARCHAR(50) NOT NULL UNIQUE,
    Category VARCHAR(50) NOT NULL,
    Description NVARCHAR(MAX),
    UnitPrice DECIMAL(18,2) NOT NULL,
    StockQuantity INT NOT NULL DEFAULT 0,
    ReorderLevel INT NOT NULL DEFAULT 10,
    IsDiscontinued BIT NOT NULL DEFAULT 0,
    CreatedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT CHK_Price CHECK (UnitPrice >= 0),
    CONSTRAINT CHK_Stock CHECK (StockQuantity >= 0)
);

CREATE INDEX IX_Products_Category ON Products(Category);
CREATE INDEX IX_Products_SKU ON Products(SKU);

-- Orders table
CREATE TABLE Orders (
    OrderId INT IDENTITY(1,1) PRIMARY KEY,
    CustomerId INT NOT NULL,
    OrderDate DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    RequiredDate DATETIME2,
    ShippedDate DATETIME2,
    Status VARCHAR(20) NOT NULL DEFAULT 'Pending',
    ShippingAddress NVARCHAR(500),
    SubTotal DECIMAL(18,2) NOT NULL DEFAULT 0,
    Tax DECIMAL(18,2) NOT NULL DEFAULT 0,
    ShippingCost DECIMAL(18,2) NOT NULL DEFAULT 0,
    TotalAmount AS (SubTotal + Tax + ShippingCost) PERSISTED,
    Notes NVARCHAR(MAX),
    CONSTRAINT FK_Orders_Customer FOREIGN KEY (CustomerId)
        REFERENCES Customers(CustomerId),
    CONSTRAINT CHK_OrderStatus CHECK (Status IN ('Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'))
);

CREATE INDEX IX_Orders_CustomerId ON Orders(CustomerId);
CREATE INDEX IX_Orders_Status ON Orders(Status);
CREATE INDEX IX_Orders_OrderDate ON Orders(OrderDate DESC);

-- Order Details table
CREATE TABLE OrderDetails (
    OrderDetailId INT IDENTITY(1,1) PRIMARY KEY,
    OrderId INT NOT NULL,
    ProductId INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    Discount DECIMAL(5,2) NOT NULL DEFAULT 0,
    LineTotal AS (Quantity * UnitPrice * (1 - Discount)) PERSISTED,
    CONSTRAINT FK_OrderDetails_Order FOREIGN KEY (OrderId)
        REFERENCES Orders(OrderId) ON DELETE CASCADE,
    CONSTRAINT FK_OrderDetails_Product FOREIGN KEY (ProductId)
        REFERENCES Products(ProductId),
    CONSTRAINT CHK_Quantity CHECK (Quantity > 0),
    CONSTRAINT CHK_Discount CHECK (Discount >= 0 AND Discount <= 1)
);

CREATE INDEX IX_OrderDetails_OrderId ON OrderDetails(OrderId);
CREATE INDEX IX_OrderDetails_ProductId ON OrderDetails(ProductId);

-- Employees table (for audit and DBA demos)
CREATE TABLE Employees (
    EmployeeId INT IDENTITY(1,1) PRIMARY KEY,
    FirstName NVARCHAR(50) NOT NULL,
    LastName NVARCHAR(50) NOT NULL,
    Email NVARCHAR(255) NOT NULL UNIQUE,
    Phone VARCHAR(20),
    HireDate DATE NOT NULL,
    Department NVARCHAR(50),
    JobTitle NVARCHAR(100),
    Salary DECIMAL(18,2),  -- Sensitive data for compliance demos
    SSN CHAR(11),          -- PII for compliance demos
    IsActive BIT NOT NULL DEFAULT 1
);

-- Audit Log table
CREATE TABLE AuditLog (
    AuditId BIGINT IDENTITY(1,1) PRIMARY KEY,
    TableName NVARCHAR(128) NOT NULL,
    RecordId INT NOT NULL,
    Action VARCHAR(10) NOT NULL,
    OldValues NVARCHAR(MAX),
    NewValues NVARCHAR(MAX),
    ChangedBy NVARCHAR(128),
    ChangedAt DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    CONSTRAINT CHK_Action CHECK (Action IN ('INSERT', 'UPDATE', 'DELETE'))
);

CREATE INDEX IX_AuditLog_TableName ON AuditLog(TableName, RecordId);
CREATE INDEX IX_AuditLog_ChangedAt ON AuditLog(ChangedAt DESC);


-- ============================================================================
-- Create Views
-- ============================================================================

CREATE VIEW vw_CustomerOrders AS
SELECT
    c.CustomerId,
    c.CustomerName,
    c.Email,
    o.OrderId,
    o.OrderDate,
    o.Status,
    o.TotalAmount,
    COUNT(od.OrderDetailId) AS ItemCount
FROM Customers c
LEFT JOIN Orders o ON c.CustomerId = o.CustomerId
LEFT JOIN OrderDetails od ON o.OrderId = od.OrderId
GROUP BY
    c.CustomerId, c.CustomerName, c.Email,
    o.OrderId, o.OrderDate, o.Status, o.TotalAmount;
GO

CREATE VIEW vw_ProductSales AS
SELECT
    p.ProductId,
    p.ProductName,
    p.Category,
    p.UnitPrice AS CurrentPrice,
    COALESCE(SUM(od.Quantity), 0) AS TotalQuantitySold,
    COALESCE(SUM(od.LineTotal), 0) AS TotalRevenue,
    COUNT(DISTINCT od.OrderId) AS NumberOfOrders
FROM Products p
LEFT JOIN OrderDetails od ON p.ProductId = od.ProductId
GROUP BY p.ProductId, p.ProductName, p.Category, p.UnitPrice;
GO

CREATE VIEW vw_MonthlyRevenue AS
SELECT
    YEAR(OrderDate) AS Year,
    MONTH(OrderDate) AS Month,
    COUNT(*) AS OrderCount,
    SUM(SubTotal) AS SubTotal,
    SUM(Tax) AS TaxCollected,
    SUM(TotalAmount) AS TotalRevenue,
    AVG(TotalAmount) AS AverageOrderValue
FROM Orders
WHERE Status != 'Cancelled'
GROUP BY YEAR(OrderDate), MONTH(OrderDate);
GO


-- ============================================================================
-- Create Stored Procedures
-- ============================================================================

CREATE PROCEDURE sp_GetCustomerOrders
    @CustomerId INT,
    @StartDate DATETIME2 = NULL,
    @EndDate DATETIME2 = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        o.OrderId,
        o.OrderDate,
        o.Status,
        o.TotalAmount,
        od.ProductId,
        p.ProductName,
        od.Quantity,
        od.UnitPrice,
        od.LineTotal
    FROM Orders o
    JOIN OrderDetails od ON o.OrderId = od.OrderId
    JOIN Products p ON od.ProductId = p.ProductId
    WHERE o.CustomerId = @CustomerId
        AND (@StartDate IS NULL OR o.OrderDate >= @StartDate)
        AND (@EndDate IS NULL OR o.OrderDate <= @EndDate)
    ORDER BY o.OrderDate DESC, od.OrderDetailId;
END;
GO

CREATE PROCEDURE sp_CreateOrder
    @CustomerId INT,
    @ShippingAddress NVARCHAR(500) = NULL,
    @OrderId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        -- Validate customer exists and is active
        IF NOT EXISTS (SELECT 1 FROM Customers WHERE CustomerId = @CustomerId AND IsActive = 1)
        BEGIN
            THROW 50001, 'Customer not found or inactive', 1;
        END

        INSERT INTO Orders (CustomerId, ShippingAddress, Status)
        VALUES (@CustomerId, @ShippingAddress, 'Pending');

        SET @OrderId = SCOPE_IDENTITY();

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

CREATE PROCEDURE sp_AddOrderItem
    @OrderId INT,
    @ProductId INT,
    @Quantity INT,
    @Discount DECIMAL(5,2) = 0
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        BEGIN TRANSACTION;

        DECLARE @UnitPrice DECIMAL(18,2);
        DECLARE @StockQuantity INT;

        -- Get product info with lock
        SELECT @UnitPrice = UnitPrice, @StockQuantity = StockQuantity
        FROM Products WITH (UPDLOCK)
        WHERE ProductId = @ProductId;

        IF @UnitPrice IS NULL
        BEGIN
            THROW 50002, 'Product not found', 1;
        END

        IF @StockQuantity < @Quantity
        BEGIN
            THROW 50003, 'Insufficient stock', 1;
        END

        -- Add order detail
        INSERT INTO OrderDetails (OrderId, ProductId, Quantity, UnitPrice, Discount)
        VALUES (@OrderId, @ProductId, @Quantity, @UnitPrice, @Discount);

        -- Update stock
        UPDATE Products
        SET StockQuantity = StockQuantity - @Quantity
        WHERE ProductId = @ProductId;

        -- Update order subtotal
        UPDATE Orders
        SET SubTotal = (
            SELECT SUM(LineTotal) FROM OrderDetails WHERE OrderId = @OrderId
        )
        WHERE OrderId = @OrderId;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        ROLLBACK TRANSACTION;
        THROW;
    END CATCH
END;
GO

CREATE PROCEDURE sp_GetInventoryAlerts
    @ThresholdPercent INT = 20
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        ProductId,
        ProductName,
        SKU,
        Category,
        StockQuantity,
        ReorderLevel,
        (ReorderLevel - StockQuantity) AS ShortageAmount,
        CASE
            WHEN StockQuantity = 0 THEN 'Out of Stock'
            WHEN StockQuantity < ReorderLevel THEN 'Low Stock'
            ELSE 'OK'
        END AS StockStatus
    FROM Products
    WHERE StockQuantity <= ReorderLevel * (100 + @ThresholdPercent) / 100
        AND IsDiscontinued = 0
    ORDER BY StockQuantity ASC;
END;
GO


-- ============================================================================
-- Create Triggers (for audit demo)
-- ============================================================================

CREATE TRIGGER trg_Customers_Audit
ON Customers
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Handle INSERT
    INSERT INTO AuditLog (TableName, RecordId, Action, NewValues, ChangedBy)
    SELECT
        'Customers',
        i.CustomerId,
        'INSERT',
        (SELECT i.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
        SYSTEM_USER
    FROM inserted i
    WHERE NOT EXISTS (SELECT 1 FROM deleted);

    -- Handle UPDATE
    INSERT INTO AuditLog (TableName, RecordId, Action, OldValues, NewValues, ChangedBy)
    SELECT
        'Customers',
        i.CustomerId,
        'UPDATE',
        (SELECT d.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
        (SELECT i.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
        SYSTEM_USER
    FROM inserted i
    JOIN deleted d ON i.CustomerId = d.CustomerId;

    -- Handle DELETE
    INSERT INTO AuditLog (TableName, RecordId, Action, OldValues, ChangedBy)
    SELECT
        'Customers',
        d.CustomerId,
        'DELETE',
        (SELECT d.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER),
        SYSTEM_USER
    FROM deleted d
    WHERE NOT EXISTS (SELECT 1 FROM inserted);
END;
GO


-- ============================================================================
-- Insert Sample Data
-- ============================================================================

-- Insert Customers
INSERT INTO Customers (CustomerName, Email, Phone, Address, City, State, PostalCode)
VALUES
    ('John Smith', 'john.smith@email.com', '555-0101', '123 Main St', 'New York', 'NY', '10001'),
    ('Jane Doe', 'jane.doe@email.com', '555-0102', '456 Oak Ave', 'Los Angeles', 'CA', '90001'),
    ('Bob Johnson', 'bob.j@email.com', '555-0103', '789 Pine Rd', 'Chicago', 'IL', '60601'),
    ('Alice Brown', 'alice.b@email.com', '555-0104', '321 Elm St', 'Houston', 'TX', '77001'),
    ('Charlie Wilson', 'charlie.w@email.com', '555-0105', '654 Maple Dr', 'Phoenix', 'AZ', '85001'),
    ('Diana Martinez', 'diana.m@email.com', '555-0106', '987 Cedar Ln', 'Philadelphia', 'PA', '19101'),
    ('Edward Lee', 'edward.l@email.com', '555-0107', '147 Birch Way', 'San Antonio', 'TX', '78201'),
    ('Fiona Garcia', 'fiona.g@email.com', '555-0108', '258 Spruce Ct', 'San Diego', 'CA', '92101'),
    ('George Taylor', 'george.t@email.com', '555-0109', '369 Walnut Blvd', 'Dallas', 'TX', '75201'),
    ('Hannah Anderson', 'hannah.a@email.com', '555-0110', '741 Cherry Ave', 'San Jose', 'CA', '95101');

-- Insert Products
INSERT INTO Products (ProductName, SKU, Category, Description, UnitPrice, StockQuantity, ReorderLevel)
VALUES
    ('Laptop Pro 15', 'TECH-001', 'Electronics', 'High-performance laptop', 1299.99, 50, 10),
    ('Wireless Mouse', 'TECH-002', 'Electronics', 'Ergonomic wireless mouse', 29.99, 200, 30),
    ('USB-C Hub', 'TECH-003', 'Electronics', '7-port USB-C hub', 49.99, 150, 25),
    ('Office Chair', 'FURN-001', 'Furniture', 'Ergonomic office chair', 299.99, 30, 5),
    ('Standing Desk', 'FURN-002', 'Furniture', 'Adjustable standing desk', 499.99, 20, 5),
    ('Notebook Set', 'OFFC-001', 'Office Supplies', 'Pack of 5 notebooks', 12.99, 500, 100),
    ('Pen Pack', 'OFFC-002', 'Office Supplies', 'Pack of 10 pens', 8.99, 800, 150),
    ('Monitor 27"', 'TECH-004', 'Electronics', '27-inch 4K monitor', 349.99, 75, 15),
    ('Keyboard Mechanical', 'TECH-005', 'Electronics', 'Mechanical keyboard', 89.99, 100, 20),
    ('Webcam HD', 'TECH-006', 'Electronics', '1080p HD webcam', 79.99, 120, 25);

-- Insert Orders and Order Details
DECLARE @OrderId INT;

-- Order 1
EXEC sp_CreateOrder @CustomerId = 1, @ShippingAddress = '123 Main St, New York, NY 10001', @OrderId = @OrderId OUTPUT;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 1, @Quantity = 1;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 2, @Quantity = 2;
UPDATE Orders SET Status = 'Delivered', ShippedDate = DATEADD(DAY, -5, GETUTCDATE()) WHERE OrderId = @OrderId;

-- Order 2
EXEC sp_CreateOrder @CustomerId = 2, @OrderId = @OrderId OUTPUT;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 4, @Quantity = 1;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 5, @Quantity = 1;
UPDATE Orders SET Status = 'Shipped', ShippedDate = DATEADD(DAY, -1, GETUTCDATE()) WHERE OrderId = @OrderId;

-- Order 3
EXEC sp_CreateOrder @CustomerId = 3, @OrderId = @OrderId OUTPUT;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 6, @Quantity = 10;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 7, @Quantity = 5;
UPDATE Orders SET Status = 'Processing' WHERE OrderId = @OrderId;

-- Order 4
EXEC sp_CreateOrder @CustomerId = 1, @OrderId = @OrderId OUTPUT;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 8, @Quantity = 2;
UPDATE Orders SET Status = 'Pending' WHERE OrderId = @OrderId;

-- Order 5
EXEC sp_CreateOrder @CustomerId = 4, @OrderId = @OrderId OUTPUT;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 9, @Quantity = 1;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 10, @Quantity = 1;
EXEC sp_AddOrderItem @OrderId = @OrderId, @ProductId = 3, @Quantity = 2;
UPDATE Orders SET Status = 'Delivered', ShippedDate = DATEADD(DAY, -10, GETUTCDATE()) WHERE OrderId = @OrderId;

-- Insert Employees (with sample PII for compliance testing)
INSERT INTO Employees (FirstName, LastName, Email, Phone, HireDate, Department, JobTitle, Salary, SSN)
VALUES
    ('Michael', 'Scott', 'michael.scott@company.com', '555-0201', '2010-03-15', 'Management', 'Regional Manager', 85000.00, '123-45-6789'),
    ('Jim', 'Halpert', 'jim.halpert@company.com', '555-0202', '2012-06-01', 'Sales', 'Sales Representative', 65000.00, '234-56-7890'),
    ('Pam', 'Beesly', 'pam.beesly@company.com', '555-0203', '2011-09-15', 'Administration', 'Office Administrator', 45000.00, '345-67-8901'),
    ('Dwight', 'Schrute', 'dwight.schrute@company.com', '555-0204', '2008-01-10', 'Sales', 'Assistant Regional Manager', 70000.00, '456-78-9012'),
    ('Angela', 'Martin', 'angela.martin@company.com', '555-0205', '2009-04-20', 'Accounting', 'Senior Accountant', 55000.00, '567-89-0123');

PRINT 'Sample database seeded successfully!';
GO
