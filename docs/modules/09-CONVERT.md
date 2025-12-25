# SQL Convert

**AI-Powered Database Migration Platform**

## Overview

SQL Convert provides intelligent, automated migration between SQL Server variants (On-Prem, Managed Instance, Azure SQL) and PostgreSQL in both directions. Unlike simple schema converters, SQL Convert uses an AI-driven plan-execute-test-integrate agent suite to handle complex conversions including SQL Agent jobs, cross-database queries, CLR procedures, and more.

## The Problem

### Current Migration Challenges

| Challenge | Traditional Approach | Pain Point |
|-----------|---------------------|------------|
| SQL Agent Jobs | Manual rewrite | No equivalent in Azure SQL/PG |
| Cross-DB Queries | 3-part names | Broken references |
| xp_cmdshell | CLR procedures | Security/compatibility |
| Linked Servers | Distributed queries | Architecture change |
| SQL Syntax | Find/replace | Subtle differences break queries |
| Data Types | Manual mapping | Precision/behavior changes |
| Stored Procedures | Line-by-line | Logic differences |
| Triggers | Event handling | Different paradigms |

## SQL Convert Solution

### Supported Migration Paths

```
SQL Server On-Prem ──────────────────────► Azure SQL Database
       │                                         │
       │                                         │
       ▼                                         ▼
SQL Server MI ◄──────────────────────────► PostgreSQL
       │                                         │
       └─────────────────────────────────────────┘
              (Bidirectional with AI assistance)
```

## Key Capabilities

### 1. SQL Agent Job Conversion

**Problem:** Azure SQL Database and PostgreSQL have no native job scheduler.

**Solution:** AI-generated Azure Functions or pg_cron equivalents.

```typescript
// Original SQL Agent Job
// Job: DailyCustomerSync
// Schedule: Every day at 2:00 AM
// Step 1: EXEC dbo.SyncCustomers
// Step 2: EXEC dbo.SendSyncReport @Email='admin@company.com'

// AI-Generated Azure Function
import { AzureFunction, Context, Timer } from "@azure/functions";
import { Connection, Request } from "tedious";

const timerTrigger: AzureFunction = async function (
  context: Context,
  myTimer: Timer
): Promise<void> {
  const connection = await createConnection();

  try {
    // Step 1: Execute SyncCustomers
    await executeStoredProcedure(connection, "dbo.SyncCustomers");

    // Step 2: Execute SendSyncReport
    await executeStoredProcedure(connection, "dbo.SendSyncReport", {
      Email: "admin@company.com"
    });

    context.log("DailyCustomerSync completed successfully");
  } catch (error) {
    context.log.error("DailyCustomerSync failed:", error);
    // Alert logic preserved from original job
    await sendAlert("DailyCustomerSync Failed", error.message);
    throw error;
  } finally {
    connection.close();
  }
};

export default timerTrigger;
```

### 2. Cross-Database Query Resolution

**Problem:** 3-part naming (`Database.Schema.Table`) doesn't work in Azure SQL/PG.

**Solution:** Database intermediary patterns with external tables, synonyms, or API calls.

```sql
-- Original Query (SQL Server On-Prem)
SELECT c.CustomerName, o.OrderTotal
FROM Customers.dbo.Customer c
JOIN Orders.dbo.Order o ON c.CustomerId = o.CustomerId
WHERE o.OrderDate > GETDATE() - 30;

-- AI-Generated Solution for Azure SQL
-- Option 1: External Tables
CREATE EXTERNAL DATA SOURCE CustomersDB
WITH (TYPE = RDBMS, ...);

CREATE EXTERNAL TABLE dbo.Customer_External (...)
WITH (DATA_SOURCE = CustomersDB, SCHEMA_NAME = 'dbo', OBJECT_NAME = 'Customer');

-- Option 2: Synonym + Elastic Query
CREATE SYNONYM dbo.Customer FOR CustomersDB.dbo.Customer;

-- Option 3: API Integration (for complex cases)
-- AI generates Azure Function to fetch cross-database data
```

### 3. xp_cmdshell & CLR Replacement

**Problem:** xp_cmdshell and custom CLR assemblies don't work in Azure SQL.

**Solution:** AI-coded Azure Functions with secure execution.

```sql
-- Original: File system access via xp_cmdshell
EXEC xp_cmdshell 'copy \\server\share\file.csv C:\import\';
BULK INSERT dbo.ImportTable FROM 'C:\import\file.csv';

-- AI-Generated: Azure Function + Blob Storage
-- 1. Azure Function monitors blob container
-- 2. On file arrival, triggers import
-- 3. Calls stored procedure with data
```

### 4. Syntax Translation Engine

**SQL Server to PostgreSQL:**

| SQL Server | PostgreSQL | Notes |
|------------|------------|-------|
| `GETDATE()` | `NOW()` | Timestamp functions |
| `ISNULL(a, b)` | `COALESCE(a, b)` | Null handling |
| `TOP 10` | `LIMIT 10` | Row limiting |
| `IDENTITY(1,1)` | `SERIAL` or `GENERATED` | Auto-increment |
| `NVARCHAR(MAX)` | `TEXT` | Large strings |
| `BIT` | `BOOLEAN` | Boolean type |
| `DATETIME2` | `TIMESTAMP` | Date/time |
| `OUTPUT INSERTED.*` | `RETURNING *` | Return modified rows |
| `@@IDENTITY` | `LASTVAL()` | Last identity |
| `WITH (NOLOCK)` | (removed) | Locking hints |

**PostgreSQL to SQL Server:**

| PostgreSQL | SQL Server | Notes |
|------------|------------|-------|
| `SERIAL` | `IDENTITY(1,1)` | Auto-increment |
| `ARRAY[]` | (JSON or table type) | Arrays |
| `JSONB` | `NVARCHAR(MAX)` + JSON functions | JSON storage |
| `::type` | `CAST(... AS type)` | Type casting |
| `||` (concat) | `+` or `CONCAT()` | String concat |
| `ILIKE` | `LIKE` (case config) | Case-insensitive |

### 5. Stored Procedure Conversion

```sql
-- Original SQL Server Procedure
CREATE PROCEDURE dbo.GetCustomerOrders
    @CustomerId INT,
    @StartDate DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;

    SELECT o.OrderId, o.OrderDate, o.Total
    FROM dbo.Orders o WITH (NOLOCK)
    WHERE o.CustomerId = @CustomerId
      AND o.OrderDate >= ISNULL(@StartDate, DATEADD(YEAR, -1, GETDATE()))
    ORDER BY o.OrderDate DESC;
END;

-- AI-Converted PostgreSQL Function
CREATE OR REPLACE FUNCTION get_customer_orders(
    p_customer_id INTEGER,
    p_start_date TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
    order_id INTEGER,
    order_date TIMESTAMP,
    total NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT o.order_id, o.order_date, o.total
    FROM orders o
    WHERE o.customer_id = p_customer_id
      AND o.order_date >= COALESCE(p_start_date, NOW() - INTERVAL '1 year')
    ORDER BY o.order_date DESC;
END;
$$;
```

## AI Agent Suite

### Plan-Execute-Test-Integrate Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                         PLAN PHASE                               │
├─────────────────────────────────────────────────────────────────┤
│  1. Schema Analysis     - Catalog all objects                    │
│  2. Dependency Mapping  - Build object graph                     │
│  3. Compatibility Check - Identify unsupported features          │
│  4. Migration Strategy  - Generate conversion plan               │
│  5. Risk Assessment     - Flag high-risk conversions             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        EXECUTE PHASE                             │
├─────────────────────────────────────────────────────────────────┤
│  1. Schema Conversion   - Tables, indexes, constraints           │
│  2. Code Translation    - SPs, functions, triggers               │
│  3. Job Migration       - Agent jobs → Azure Functions           │
│  4. Data Migration      - Bulk copy with validation              │
│  5. Reference Updates   - Fix cross-database references          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         TEST PHASE                               │
├─────────────────────────────────────────────────────────────────┤
│  1. Schema Validation   - Compare source/target structures       │
│  2. Data Verification   - Row counts, checksums                  │
│  3. Procedure Testing   - Execute all SPs with test data         │
│  4. Performance Check   - Compare execution plans                │
│  5. Regression Suite    - Run application test suite             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       INTEGRATE PHASE                            │
├─────────────────────────────────────────────────────────────────┤
│  1. Connection Updates  - Generate new connection strings        │
│  2. Application Changes - Update data access code                │
│  3. CI/CD Pipeline      - Add migration to deployment            │
│  4. Monitoring Setup    - Configure alerts and dashboards        │
│  5. Rollback Plan       - Document reversion procedure           │
└─────────────────────────────────────────────────────────────────┘
```

## Migration Report

SQL Convert generates comprehensive migration reports:

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL CONVERT MIGRATION REPORT                        ║
║              Source: SQL Server 2019 On-Prem                     ║
║              Target: Azure SQL Database                          ║
╠══════════════════════════════════════════════════════════════════╣
║ SUMMARY                                                          ║
║ ─────────────────────────────────────────────────────────────── ║
║ Total Objects:        1,247                                      ║
║ Auto-Converted:       1,189 (95.3%)                              ║
║ AI-Assisted:             47 (3.8%)                               ║
║ Manual Review:           11 (0.9%)                               ║
╠══════════════════════════════════════════════════════════════════╣
║ OBJECT BREAKDOWN                                                 ║
║ ─────────────────────────────────────────────────────────────── ║
║ Tables:               234   ✓ All converted                      ║
║ Stored Procedures:    412   ✓ 408 auto, 4 review                 ║
║ Functions:             89   ✓ All converted                      ║
║ Views:                156   ✓ All converted                      ║
║ Triggers:              34   ✓ 31 auto, 3 AI-assisted             ║
║ SQL Agent Jobs:        18   → Azure Functions generated          ║
║ Linked Servers:         4   → External tables created            ║
╠══════════════════════════════════════════════════════════════════╣
║ ITEMS REQUIRING REVIEW                                           ║
║ ─────────────────────────────────────────────────────────────── ║
║ 1. dbo.ExportToFile      - Uses xp_cmdshell (→ Azure Function)   ║
║ 2. dbo.SendEmailAlert    - Uses sp_send_dbmail (→ Logic App)     ║
║ 3. dbo.CustomCLRFunction - CLR assembly (→ Azure Function)       ║
║ ...                                                              ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Analyze source database
sql2ai convert analyze --source "Server=...;Database=..."

# Generate migration plan
sql2ai convert plan --source "..." --target azure-sql

# Execute migration
sql2ai convert execute --plan migration-plan.json

# Run validation tests
sql2ai convert test --source "..." --target "..."

# Generate integration changes
sql2ai convert integrate --output ./migration-artifacts
```

## Integration Points

- **SQL Version**: Track conversion history and changes
- **SQL Test**: Validate converted procedures
- **SQL Optimize**: Tune queries for target platform
- **SQL Code**: Review converted code for issues
