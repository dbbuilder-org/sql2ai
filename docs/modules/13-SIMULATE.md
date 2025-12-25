# SQL Simulate

**Synthetic Data Generation Platform**

## Overview

SQL Simulate creates realistic synthetic data from metadata and data dictionaries without requiring access to source data. Unlike anonymization which transforms real data, simulation generates entirely new data that statistically mirrors production patterns while being completely fictional.

## The Problem

### When Anonymization Isn't Enough

| Scenario | Anonymize | Simulate |
|----------|-----------|----------|
| No production access | ❌ | ✓ |
| New system development | ❌ | ✓ |
| Load testing (10x data) | ❌ | ✓ |
| Demo environments | Limited | ✓ |
| Training data for ML | Re-id risk | ✓ |
| Greenfield projects | ❌ | ✓ |

## SQL Simulate Solution

### Generation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    INPUT SOURCES                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Schema    │  │    Data     │  │  Business   │              │
│  │  Metadata   │  │ Dictionary  │  │   Rules     │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼─────────────────────┘
          │                │                │
          ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SQL SIMULATE ENGINE                           │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. Analyze Schema    - Column types, constraints, FKs     │ │
│  │  2. Infer Patterns    - AI understands data semantics      │ │
│  │  3. Build Generators  - Create data generators per column  │ │
│  │  4. Establish Relations - Maintain FK integrity            │ │
│  │  5. Generate Data     - Produce synthetic records          │ │
│  │  6. Validate Output   - Ensure realistic distributions     │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    OUTPUT: SYNTHETIC DATABASE                    │
│                                                                  │
│    ✓ Realistic data      ✓ FK integrity    ✓ Correct types     │
│    ✓ Proper distributions  ✓ Edge cases    ✓ Scalable volume   │
└─────────────────────────────────────────────────────────────────┘
```

## AI-Powered Column Understanding

### Semantic Analysis

SQL Simulate uses AI to understand column meaning from names and context:

```yaml
# Auto-detected from schema
table: Customers
columns:
  CustomerId:
    detected_type: primary_key
    generator: sequential

  FirstName:
    detected_type: person_first_name
    generator: faker.first_name
    locale: en_US

  Email:
    detected_type: email
    generator: email
    pattern: "{first_name}.{last_name}@{domain}"

  PhoneNumber:
    detected_type: phone
    generator: phone
    format: "(###) ###-####"

  CreditLimit:
    detected_type: currency
    generator: decimal
    range: [1000, 50000]
    distribution: normal
    mean: 15000
    std_dev: 8000

  CreatedDate:
    detected_type: creation_timestamp
    generator: datetime
    range: [2020-01-01, now]
    distribution: uniform

  Status:
    detected_type: enum
    generator: choice
    values: [Active, Inactive, Pending, Suspended]
    weights: [0.75, 0.15, 0.08, 0.02]
```

### Pattern Recognition

```
Column: ProductSKU
Pattern Detected: [A-Z]{3}-[0-9]{4}-[A-Z]{2}
Examples Generated:
  ABC-1234-XY
  DEF-5678-PQ
  GHI-9012-RS

Column: SSN
Pattern Detected: Social Security Number
Action: Generate valid format with invalid checksum
Examples:
  123-45-6789 (format valid, not real)
  987-65-4321 (format valid, not real)
```

## Data Distribution Modeling

### From Statistics (if available)

```yaml
# Can import production statistics
distributions:
  Orders.Total:
    type: log_normal
    mean: 4.5  # log scale
    std_dev: 1.2
    min: 10
    max: 50000

  Orders.ItemCount:
    type: poisson
    lambda: 3.2

  Customers.Age:
    type: custom_histogram
    buckets:
      18-24: 0.15
      25-34: 0.28
      35-44: 0.25
      45-54: 0.18
      55-64: 0.10
      65+: 0.04
```

### From Data Dictionary

```yaml
# SQL Code data dictionary provides context
data_dictionary:
  Customers.LoyaltyTier:
    description: "Customer loyalty level based on annual spend"
    values:
      Bronze: "< $500 annual spend"
      Silver: "$500 - $2000 annual spend"
      Gold: "$2000 - $5000 annual spend"
      Platinum: "> $5000 annual spend"

# SQL Simulate generates:
# - Correlated spend amounts per tier
# - Realistic tier distribution (more Bronze than Platinum)
```

## Referential Integrity

### Foreign Key Generation

```yaml
relationships:
  Orders:
    CustomerId:
      references: Customers.CustomerId
      distribution: pareto  # Some customers have many orders
      alpha: 1.5  # 20% of customers = 80% of orders

  OrderItems:
    OrderId:
      references: Orders.OrderId
      count_distribution: poisson
      lambda: 2.5  # Average 2.5 items per order

    ProductId:
      references: Products.ProductId
      distribution: weighted
      weight_column: Products.Popularity
```

### Cascading Generation

```
Generation Order (auto-calculated):
  1. Categories (0 dependencies)
  2. Products (depends on Categories)
  3. Customers (0 dependencies)
  4. Orders (depends on Customers)
  5. OrderItems (depends on Orders, Products)

Progress:
  Categories:   100/100   ████████████████████ 100%
  Products:     1000/1000 ████████████████████ 100%
  Customers:    50000/50000 ██████████████████ 100%
  Orders:       150000/150000 ████████████████ 100%
  OrderItems:   375000/375000 ████████████████ 100%
```

## Business Rule Enforcement

```yaml
rules:
  # Temporal consistency
  - name: order_after_customer
    condition: "Orders.OrderDate >= Customers.CreatedDate"

  # Logical constraints
  - name: valid_discount
    condition: "OrderItems.Discount <= OrderItems.UnitPrice * 0.5"

  # Cross-field dependencies
  - name: status_date_consistency
    when: "Orders.Status = 'Shipped'"
    then: "Orders.ShippedDate IS NOT NULL"

  # Correlated values
  - name: premium_customer_higher_limit
    when: "Customers.LoyaltyTier = 'Platinum'"
    then: "Customers.CreditLimit >= 25000"
```

## Edge Case Generation

```yaml
edge_cases:
  enabled: true
  percentage: 5  # 5% of data includes edge cases

  scenarios:
    - name: null_optional_fields
      frequency: 0.1
      columns: [MiddleName, Phone2, Notes]

    - name: maximum_length_strings
      frequency: 0.01
      columns: [Description, Address]

    - name: boundary_dates
      frequency: 0.02
      values: [1900-01-01, 2099-12-31, null]

    - name: unicode_characters
      frequency: 0.05
      columns: [CustomerName, ProductName]
      values: ["José García", "北京", "Ümlauts"]

    - name: extreme_values
      frequency: 0.01
      columns: [OrderTotal]
      values: [0.01, 999999.99]
```

## Scale Configuration

```yaml
scale:
  mode: multiplier
  factor: 10  # 10x production size

  # OR
  mode: absolute
  targets:
    Customers: 1000000
    Orders: 5000000
    OrderItems: 12500000

  performance:
    batch_size: 10000
    parallel_workers: 8
    disable_indexes: true  # Rebuild after generation
```

## Output Formats

```yaml
output:
  # Direct database load
  database:
    connection: "postgresql://dev/TestDB"
    mode: truncate_insert

  # File export
  files:
    format: csv  # or parquet, json
    path: ./synthetic_data/
    compression: gzip

  # SQL scripts
  scripts:
    path: ./insert_scripts/
    batch_size: 1000
    include_schema: true
```

## Validation Report

```
╔══════════════════════════════════════════════════════════════════╗
║              SQL SIMULATE VALIDATION REPORT                      ║
╠══════════════════════════════════════════════════════════════════╣
║ DATA QUALITY CHECKS                                              ║
║ ─────────────────────────────────────────────────────────────── ║
║ ✓ All FK constraints satisfied                                   ║
║ ✓ No NULL violations in required columns                         ║
║ ✓ All check constraints passed                                   ║
║ ✓ Unique constraints maintained                                  ║
╠══════════════════════════════════════════════════════════════════╣
║ DISTRIBUTION ANALYSIS                                            ║
║ ─────────────────────────────────────────────────────────────── ║
║ Customers.Age:       Mean=38.2, Std=12.4 (Target: 38, 12)       ║
║ Orders.Total:        Median=$127 (Target: $125)                  ║
║ Orders per Customer: P80=12 orders (Target: P80=10-15)          ║
╠══════════════════════════════════════════════════════════════════╣
║ EDGE CASE COVERAGE                                               ║
║ ─────────────────────────────────────────────────────────────── ║
║ NULL values:         4.8% (Target: 5%)                           ║
║ Boundary values:     1.2% (Target: 1%)                           ║
║ Unicode names:       5.1% (Target: 5%)                           ║
╚══════════════════════════════════════════════════════════════════╝
```

## CLI Commands

```bash
# Analyze schema and generate config
sql2ai simulate init --schema "postgresql://prod/DB" --output sim.yaml

# Generate synthetic data
sql2ai simulate run --config sim.yaml --scale 10x

# Validate generated data
sql2ai simulate validate

# Generate from data dictionary
sql2ai simulate from-dictionary --input data-dict.yaml

# Quick demo data
sql2ai simulate demo --tables Customers,Orders --rows 1000
```

## Integration Points

- **SQL Code**: Use data dictionary for semantic understanding
- **SQL Test**: Generate test fixtures
- **SQL Anonymize**: Supplement anonymized data
- **SQL API**: Create demo data for API testing
