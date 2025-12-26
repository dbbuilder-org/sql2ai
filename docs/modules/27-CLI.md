# SQL CLI

**Module 27** | **Status:** In Development | **Priority:** P1

## Overview

SQL CLI is the command-line interface for the SQL2.AI platform. It provides full access to all SQL2.AI capabilities from the terminal, enabling scripting, automation, and CI/CD integration. Whether you're generating migrations, running compliance checks, or generating AI-powered SQL, the CLI puts all of SQL2.AI at your fingertips.

## Key Use Cases

### Local Development
```bash
# Quick schema inspection
sql2ai schema show customers

# Generate a query from natural language
sql2ai query "Show me all orders from last month with customer details"

# Run migrations locally
sql2ai migrate up --to latest
```

### CI/CD Integration
```bash
# Validate migrations before deployment
sql2ai migrate validate

# Run compliance checks
sql2ai comply check --framework soc2

# Generate types for TypeScript/Dapper
sql2ai codegen --lang typescript --output ./src/types
```

### Automation & Scripting
```bash
# Batch process multiple databases
for db in prod staging dev; do
  sql2ai --connection $db comply check --framework hipaa
done

# Schedule schema snapshots
sql2ai version snapshot --tag "$(date +%Y%m%d)"
```

## Installation

### NPM (Recommended)
```bash
npm install -g @sql2ai/cli

# Or use npx
npx @sql2ai/cli --help
```

### Homebrew (macOS)
```bash
brew tap sql2ai/tap
brew install sql2ai
```

### Direct Download
```bash
# macOS
curl -L https://sql2ai.com/cli/install.sh | sh

# Windows (PowerShell)
iwr https://sql2ai.com/cli/install.ps1 -UseBasicParsing | iex
```

## Configuration

### Initialize Configuration
```bash
sql2ai init
# Creates .sql2ai/config.yaml in current directory
```

### Configuration File Structure
```yaml
# .sql2ai/config.yaml
version: 1

# Default connection
default_connection: dev

# Database connections
connections:
  dev:
    type: sqlserver
    host: localhost
    database: myapp_dev
    username: sa
    # Password from environment: SQL2AI_DEV_PASSWORD

  prod:
    type: postgresql
    host: prod-db.example.com
    database: myapp
    ssl: true
    # Use AWS Secrets Manager
    secret_arn: arn:aws:secretsmanager:us-east-1:123456789:secret:prod-db

# AI settings
ai:
  model: claude-3-5-sonnet
  temperature: 0.2

# Output preferences
output:
  format: pretty  # pretty, json, yaml
  color: auto     # auto, always, never
```

### Environment Variables
```bash
# API authentication
export SQL2AI_API_KEY="sk_live_..."

# Connection passwords (per connection name)
export SQL2AI_DEV_PASSWORD="..."
export SQL2AI_PROD_PASSWORD="..."

# Override default connection
export SQL2AI_CONNECTION="prod"
```

## Command Reference

### Connection Management

```bash
# Add a new connection
sql2ai connection add dev \
  --type sqlserver \
  --host localhost \
  --database myapp \
  --username sa \
  --password-env SQL2AI_DEV_PASSWORD

# List connections
sql2ai connection list

# Test a connection
sql2ai connection test dev

# Remove a connection
sql2ai connection remove dev

# Set default connection
sql2ai connection default prod
```

### Schema Operations

```bash
# Show full schema
sql2ai schema show

# Show specific table
sql2ai schema show customers

# Show columns only
sql2ai schema columns orders

# Show relationships
sql2ai schema relations --from customers

# Export schema as SQL
sql2ai schema export --format sql --output schema.sql

# Export as JSON (for documentation)
sql2ai schema export --format json --output schema.json

# Search schema
sql2ai schema search "customer"
```

### Query Operations

```bash
# Execute a query
sql2ai query "SELECT * FROM customers WHERE active = 1"

# Execute from file
sql2ai query --file report.sql

# Generate query from natural language
sql2ai query "Show customers who haven't ordered in 90 days" --generate

# Explain a query
sql2ai query explain "SELECT * FROM orders o JOIN customers c ON ..."

# Optimize a query
sql2ai query optimize --file slow-query.sql

# Format SQL
sql2ai query format --file messy.sql --output clean.sql
```

### Migration Operations

```bash
# Generate migration from schema diff
sql2ai migrate new "add customer loyalty"

# Generate from pending changes
sql2ai migrate generate

# Apply migrations
sql2ai migrate up
sql2ai migrate up --to 20250115_001

# Rollback
sql2ai migrate down
sql2ai migrate down --to 20250110_001

# Show migration status
sql2ai migrate status

# Validate migrations
sql2ai migrate validate

# Show SQL without executing
sql2ai migrate up --dry-run
```

### Code Generation

```bash
# Generate TypeScript types
sql2ai codegen --lang typescript --output ./src/types/db.ts

# Generate Dapper C# models
sql2ai codegen --lang csharp --output ./Models/Database

# Generate API from stored procedures
sql2ai codegen api --framework fastapi --output ./api

# Generate with specific tables only
sql2ai codegen --lang typescript --tables customers,orders,products

# Watch mode for development
sql2ai codegen --lang typescript --output ./src/types --watch
```

### Compliance Operations

```bash
# Run compliance check
sql2ai comply check --framework soc2

# Multiple frameworks
sql2ai comply check --framework soc2,hipaa,gdpr

# Generate compliance report
sql2ai comply report --framework hipaa --output report.html

# Scan for PII
sql2ai comply scan-pii --table customers --sample 1000

# List findings
sql2ai comply findings

# Export evidence
sql2ai comply evidence --framework soc2 --output ./evidence
```

### Version Control

```bash
# Take a schema snapshot
sql2ai version snapshot --tag "v1.2.0"

# Show version history
sql2ai version history

# Show object history
sql2ai version history dbo.sp_ProcessOrder

# Diff between versions
sql2ai version diff v1.1.0 v1.2.0

# Diff between environments
sql2ai version diff --from dev --to prod

# Blame (who changed what)
sql2ai version blame dbo.Customers
```

### AI Operations

```bash
# Generate SQL from natural language
sql2ai ai generate "Create a report of monthly sales by region"

# Generate stored procedure
sql2ai ai generate "Create a procedure to archive old orders" --type procedure

# Explain existing code
sql2ai ai explain --file complex-procedure.sql

# Review code for issues
sql2ai ai review --file migration.sql

# Optimize with AI suggestions
sql2ai ai optimize --file slow-query.sql
```

### Monitoring Integration

```bash
# Show current database health
sql2ai monitor status

# Show active queries
sql2ai monitor queries

# Show blocking chains
sql2ai monitor blocking

# Show index recommendations
sql2ai monitor indexes --unused
sql2ai monitor indexes --missing

# Export metrics
sql2ai monitor export --format prometheus --output metrics.txt
```

## Output Formats

### Pretty (Default)
```bash
sql2ai schema show customers
# ┌─────────────┬─────────────┬──────────┬─────────┐
# │ Column      │ Type        │ Nullable │ Key     │
# ├─────────────┼─────────────┼──────────┼─────────┤
# │ CustomerID  │ int         │ NO       │ PK      │
# │ Email       │ nvarchar    │ NO       │         │
# │ Name        │ nvarchar    │ YES      │         │
# └─────────────┴─────────────┴──────────┴─────────┘
```

### JSON
```bash
sql2ai schema show customers --format json
# {"table":"customers","columns":[{"name":"CustomerID",...}]}
```

### YAML
```bash
sql2ai schema show customers --format yaml
# table: customers
# columns:
#   - name: CustomerID
#     type: int
```

## CI/CD Examples

### GitHub Actions
```yaml
name: Database CI
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install SQL2AI CLI
        run: npm install -g @sql2ai/cli

      - name: Validate Migrations
        run: sql2ai migrate validate
        env:
          SQL2AI_API_KEY: ${{ secrets.SQL2AI_API_KEY }}

      - name: Run Compliance Check
        run: sql2ai comply check --framework soc2

      - name: Generate Types
        run: |
          sql2ai codegen --lang typescript --output ./src/types
          git diff --exit-code src/types
```

### Azure DevOps
```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: NodeTool@0
    inputs:
      versionSpec: '20.x'

  - script: npm install -g @sql2ai/cli
    displayName: 'Install SQL2AI CLI'

  - script: sql2ai migrate up --dry-run
    displayName: 'Preview Migrations'
    env:
      SQL2AI_API_KEY: $(SQL2AI_API_KEY)
      SQL2AI_PROD_PASSWORD: $(DB_PASSWORD)
```

### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validate SQL files
sql2ai query validate --files "**/*.sql"

# Check for migrations
if git diff --cached --name-only | grep -q "migrations/"; then
  sql2ai migrate validate
fi
```

## Scripting Examples

### Batch Schema Export
```bash
#!/bin/bash
# Export schemas from all environments

for env in dev staging prod; do
  sql2ai --connection $env schema export \
    --format json \
    --output "./schemas/${env}-$(date +%Y%m%d).json"
done
```

### Automated Compliance Reports
```bash
#!/bin/bash
# Weekly compliance report

REPORT_DIR="./compliance-reports/$(date +%Y-%W)"
mkdir -p $REPORT_DIR

for framework in soc2 hipaa gdpr; do
  sql2ai comply report \
    --framework $framework \
    --output "$REPORT_DIR/${framework}.html"
done

# Upload to S3
aws s3 sync $REPORT_DIR s3://my-reports/compliance/
```

### Migration Script
```bash
#!/bin/bash
# Safe migration deployment

set -e

echo "Taking pre-migration snapshot..."
sql2ai version snapshot --tag "pre-migration-$(date +%s)"

echo "Validating migrations..."
sql2ai migrate validate

echo "Showing pending migrations..."
sql2ai migrate status

read -p "Apply migrations? (y/n) " confirm
if [ "$confirm" = "y" ]; then
  sql2ai migrate up
  echo "Migrations applied successfully"
else
  echo "Migration cancelled"
fi
```

## MCP Integration

SQL CLI can also run as an MCP server for Claude Desktop and Claude Code:

```bash
# Start MCP server mode
sql2ai mcp serve

# Configure in Claude Desktop
# ~/.config/claude/claude_desktop_config.json
{
  "mcpServers": {
    "sql2ai": {
      "command": "sql2ai",
      "args": ["mcp", "serve"]
    }
  }
}
```

## Global Options

```bash
--connection, -c    Specify connection to use
--format, -f        Output format (pretty, json, yaml)
--quiet, -q         Suppress non-essential output
--verbose, -v       Enable verbose output
--debug             Enable debug output
--config            Path to config file
--no-color          Disable colored output
--version           Show version
--help, -h          Show help
```

## Implementation Status

- [ ] Core CLI framework (packages/sql2ai-cli)
- [ ] Connection management
- [ ] Configuration system
- [ ] Schema commands
- [ ] Query commands
- [ ] Migration commands
- [ ] Code generation commands
- [ ] Compliance commands
- [ ] Version control commands
- [ ] AI commands
- [ ] Monitoring commands
- [ ] MCP server mode
- [ ] GitHub Actions integration
- [ ] Azure DevOps integration
- [ ] Homebrew formula
- [ ] Windows installer
