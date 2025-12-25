# SQL Import

**Intelligent Data Ingestion Platform**

## Overview

SQL Import provides smart data import capabilities from CSV, Excel, JSON, Parquet, and external databases. It features automatic schema detection, data validation, transformation rules, and error handling to streamline data ingestion workflows.

## The Problem

### Current Import Challenges

| Challenge | Traditional Approach | Risk |
|-----------|---------------------|------|
| Manual schema mapping | Hand-code column types | Errors, mismatches |
| All-or-nothing imports | Fail on first error | Lost progress |
| No validation | Hope data is clean | Data quality issues |
| One-time scripts | Custom code each time | Maintenance burden |
| Limited formats | CSV only | Format conversion needed |

## SQL Import Solution

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    SQL IMPORT PIPELINE                           │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  SOURCE  │ →  │  DETECT  │ →  │ VALIDATE │ →  │  IMPORT  │  │
│  │   DATA   │    │  SCHEMA  │    │ TRANSFORM│    │  TO DB   │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │              │                │               │         │
│       │              │                │               │         │
│       ▼              ▼                ▼               ▼         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ • CSV    │    │ • Types  │    │ • Rules  │    │ • Bulk   │  │
│  │ • Excel  │    │ • Nulls  │    │ • FK     │    │ • Stream │  │
│  │ • JSON   │    │ • Keys   │    │ • Dedup  │    │ • Delta  │  │
│  │ • Parquet│    │ • FKs    │    │ • Clean  │    │ • Upsert │  │
│  │ • DB     │    │          │    │          │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    ERROR HANDLING                            ││
│  │  • Quarantine invalid rows  • Retry logic  • Full audit log ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Supported Sources

### File Formats

```yaml
file_formats:
  csv:
    extensions: [.csv, .tsv, .txt]
    options:
      - delimiter: auto-detect or specify
      - encoding: UTF-8, UTF-16, ASCII, etc.
      - header_row: true/false
      - skip_rows: number
      - quote_char: " or '

  excel:
    extensions: [.xlsx, .xls, .xlsm]
    options:
      - sheet_name: specific or all
      - header_row: row number
      - data_range: A1:Z1000

  json:
    extensions: [.json, .jsonl]
    options:
      - format: array, object, jsonl
      - flatten_nested: true/false
      - path: JSONPath to data

  parquet:
    extensions: [.parquet]
    options:
      - columns: select specific
      - row_groups: specify range

  xml:
    extensions: [.xml]
    options:
      - xpath: path to records
      - namespaces: namespace mappings
```

### Database Sources

```yaml
database_sources:
  sql_server:
    connection: "Server=...;Database=...;User=...;Password=..."
    query: "SELECT * FROM SourceTable"
    # or
    table: "SourceTable"

  postgresql:
    connection: "postgresql://user:pass@host/database"
    query: "SELECT * FROM source_table"

  mysql:
    connection: "mysql://user:pass@host/database"
    query: "SELECT * FROM source_table"

  mongodb:
    connection: "mongodb://host:27017/database"
    collection: "source_collection"
    filter: { status: "active" }
```

## Schema Detection

### Auto-Detection Example

```
┌─────────────────────────────────────────────────────────────────┐
│  SCHEMA DETECTION: customers.csv                                 │
├─────────────────────────────────────────────────────────────────┤
│  Analyzed: 15,000 rows                                           │
│  Confidence: 98%                                                 │
│                                                                  │
│  ┌─────────────┬──────────────┬──────────┬───────────────────┐  │
│  │ Column      │ Detected Type│ Nullable │ Sample Values     │  │
│  ├─────────────┼──────────────┼──────────┼───────────────────┤  │
│  │ id          │ INT          │ No       │ 1001, 1002, 1003  │  │
│  │ email       │ VARCHAR(255) │ No       │ john@acme.com     │  │
│  │ name        │ NVARCHAR(100)│ No       │ John Smith        │  │
│  │ created_at  │ DATETIME     │ No       │ 2024-01-15        │  │
│  │ tier        │ VARCHAR(20)  │ Yes (2%) │ premium, basic    │  │
│  │ revenue     │ DECIMAL(10,2)│ Yes (5%) │ 1234.56           │  │
│  │ is_active   │ BIT          │ No       │ true, false       │  │
│  └─────────────┴──────────────┴──────────┴───────────────────┘  │
│                                                                  │
│  Suggested Primary Key: id                                       │
│  Detected Date Format: YYYY-MM-DD                               │
│  Encoding: UTF-8                                                 │
│                                                                  │
│  [Accept Schema] [Edit Mappings] [View Sample Data]             │
└─────────────────────────────────────────────────────────────────┘
```

## Validation Rules

### Built-in Validators

```yaml
validation_rules:
  type_checks:
    - integer: must be valid integer
    - decimal: must be valid decimal
    - date: must match date format
    - email: must match email pattern
    - phone: must match phone pattern

  constraint_checks:
    - not_null: column cannot be null
    - unique: no duplicate values
    - foreign_key: value must exist in reference table
    - check: custom SQL expression

  data_quality:
    - min_length: minimum string length
    - max_length: maximum string length
    - range: numeric range check
    - pattern: regex pattern match
    - enum: value must be in list
```

### Custom Validation

```yaml
# import-config.yaml
source: customers.csv
target: Customers

validation:
  columns:
    email:
      rules:
        - type: pattern
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
          message: "Invalid email format"

    age:
      rules:
        - type: range
          min: 0
          max: 150
          message: "Age must be between 0 and 150"

    country_code:
      rules:
        - type: foreign_key
          table: Countries
          column: code
          message: "Country code not found"

  row_level:
    - rule: "end_date > start_date"
      message: "End date must be after start date"
```

## Transformation Rules

```yaml
transformations:
  columns:
    name:
      - trim: true
      - case: title  # capitalize each word

    email:
      - trim: true
      - case: lower

    phone:
      - regex_replace:
          pattern: "[^0-9]"
          replacement: ""

    created_at:
      - parse_date:
          formats: ["YYYY-MM-DD", "MM/DD/YYYY", "DD-MMM-YYYY"]

    status:
      - map_values:
          "A": "Active"
          "I": "Inactive"
          "P": "Pending"
          default: "Unknown"

    amount:
      - parse_decimal:
          decimal_separator: ","
          thousands_separator: "."

  computed_columns:
    full_address:
      expression: "CONCAT(street, ', ', city, ', ', state, ' ', zip)"

    import_timestamp:
      expression: "GETDATE()"
```

## Import Modes

### Bulk Import

```yaml
import_mode: bulk
options:
  batch_size: 10000
  parallel_threads: 4
  disable_indexes: true    # Rebuild after import
  disable_triggers: false
  lock_table: true
```

### Streaming Import

```yaml
import_mode: stream
options:
  batch_size: 1000
  commit_interval: 5000
  on_error: continue       # or fail
```

### Incremental Import

```yaml
import_mode: incremental
options:
  tracking_column: modified_at
  last_value: "2024-01-15 00:00:00"
  # Automatically stored for next run
```

### Upsert (Merge)

```yaml
import_mode: upsert
options:
  match_columns: [customer_id]
  update_columns: [name, email, updated_at]
  insert_missing: true
  on_conflict: update      # or skip, fail
```

## Error Handling

### Quarantine System

```
┌─────────────────────────────────────────────────────────────────┐
│  IMPORT RESULTS: orders.csv                                      │
├─────────────────────────────────────────────────────────────────┤
│  Total Rows:      50,000                                         │
│  Imported:        49,847 ✓                                       │
│  Quarantined:     153 ⚠️                                         │
│                                                                  │
│  QUARANTINE SUMMARY                                              │
│  ─────────────────────────────────────────────────────────────  │
│  • Invalid date format:           87 rows                        │
│  • FK violation (product_id):     45 rows                        │
│  • Duplicate order_id:            21 rows                        │
│                                                                  │
│  Quarantine Table: _import_quarantine_orders_20240115            │
│                                                                  │
│  [View Quarantine] [Export Errors] [Retry After Fix]            │
└─────────────────────────────────────────────────────────────────┘
```

### Retry Failed Rows

```bash
# View quarantined rows
sql2ai import quarantine list --job orders_20240115

# Export for fixing
sql2ai import quarantine export --job orders_20240115 --output errors.csv

# After fixing, re-import
sql2ai import run errors_fixed.csv --table Orders --append
```

## CLI Commands

```bash
# Detect schema from file
sql2ai import detect customers.csv --output schema.yaml

# Preview import
sql2ai import preview customers.csv --table Customers --rows 100

# Run import
sql2ai import run customers.csv --table Customers

# Import with options
sql2ai import run orders.xlsx \
  --table Orders \
  --sheet "Q1 Orders" \
  --mode upsert \
  --match-columns order_id \
  --validate-fk \
  --quarantine-errors

# Import from database
sql2ai import database \
  --source "postgresql://legacy/customers" \
  --target "sqlserver://new/Customers" \
  --mode incremental \
  --tracking-column updated_at

# Schedule recurring import
sql2ai import schedule \
  --source "s3://bucket/daily/*.csv" \
  --table DailyImport \
  --cron "0 2 * * *" \
  --notify-on-error

# View import history
sql2ai import history --table Customers

# Rollback import
sql2ai import rollback --job import_20240115_customers
```

## Configuration File

```yaml
# sql2ai-import.yaml
defaults:
  batch_size: 10000
  parallel_threads: 4
  quarantine_errors: true
  audit_logging: true

sources:
  daily_orders:
    type: sftp
    host: sftp.partner.com
    path: /exports/orders_*.csv
    credentials: ${SFTP_CREDS}

  customer_api:
    type: rest_api
    url: https://api.crm.com/customers
    auth: bearer ${API_TOKEN}
    pagination: cursor

jobs:
  import_daily_orders:
    source: daily_orders
    target: Orders
    mode: upsert
    match_columns: [order_id]
    schedule: "0 6 * * *"

  sync_customers:
    source: customer_api
    target: Customers
    mode: incremental
    tracking: last_modified
    schedule: "*/15 * * * *"
```

## Integration Points

- **SQL Receive**: Secure file ingestion before import
- **SQL Standardize**: Apply naming standards during import
- **SQL Anonymize**: Mask PII during import
- **SQL Monitor**: Track import job performance
- **SQL Audit**: Log all import operations
