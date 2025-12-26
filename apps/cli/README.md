# SQL2.AI CLI

AI-powered database development from the command line.

## Installation

```bash
pip install sql2ai
```

Or with pipx:

```bash
pipx install sql2ai
```

## Quick Start

```bash
# Login with your API key
sql2ai auth login

# Add a database connection
sql2ai connections add

# Optimize a query
sql2ai optimize query "SELECT * FROM users WHERE email = 'test@example.com'"

# Generate SQL from natural language
sql2ai generate sql "Find all customers who ordered in the last 30 days"

# Review SQL code
sql2ai review code --file my_query.sql
```

## Commands

### Authentication

```bash
sql2ai auth login          # Login with API key
sql2ai auth logout         # Remove stored credentials
sql2ai auth status         # Check authentication status
```

### Connections

```bash
sql2ai connections list    # List all connections
sql2ai connections add     # Add a new connection
sql2ai connections test    # Test a connection
sql2ai connections remove  # Remove a connection
```

### Query Optimization

```bash
sql2ai optimize query "SELECT..."    # Optimize a query
sql2ai optimize explain "SELECT..."  # Explain a query
sql2ai optimize plan --file plan.xml # Analyze execution plan
```

### Code Review

```bash
sql2ai review code "SELECT..."       # Review SQL code
sql2ai review code --file query.sql  # Review from file
sql2ai review dir ./migrations       # Review all SQL files
```

### SQL Generation

```bash
sql2ai generate sql "description"    # Generate SQL from prompt
sql2ai generate crud TableName       # Generate CRUD procedures
sql2ai generate table Name "cols"    # Generate CREATE TABLE
sql2ai generate index Table "cols"   # Generate CREATE INDEX
```

### Migrations

```bash
sql2ai migrate list                  # List migrations
sql2ai migrate generate              # Generate from changes
sql2ai migrate apply                 # Apply pending migrations
sql2ai migrate rollback              # Rollback last migration
```

### Schema Management

```bash
sql2ai schema extract                # Extract schema
sql2ai schema compare src target     # Compare schemas
sql2ai schema snapshot               # Create snapshot
sql2ai schema document               # Generate documentation
```

## Configuration

Create a `.sql2ai.toml` file in your project:

```toml
[settings]
api_url = "https://api.sql2.ai"
default_database = "postgresql"
output_format = "rich"
```

Or use environment variables:

```bash
export SQL2AI_API_KEY="your-api-key"
export SQL2AI_API_URL="https://api.sql2.ai"
export SQL2AI_DEFAULT_DATABASE="postgresql"
```

## Piping and Scripting

The CLI supports stdin/stdout for scripting:

```bash
# Pipe SQL through optimizer
cat query.sql | sql2ai optimize query

# Optimize and save
sql2ai optimize query --file query.sql --output optimized.sql

# Review all SQL files
find . -name "*.sql" -exec sql2ai review code --file {} \;
```

## Output Formats

```bash
# Rich console output (default)
sql2ai review code "SELECT..."

# JSON output for scripting
sql2ai review code "SELECT..." --json

# Plain text
SQL2AI_OUTPUT_FORMAT=plain sql2ai review code "SELECT..."
```

## Getting Help

```bash
sql2ai --help              # General help
sql2ai optimize --help     # Command group help
sql2ai optimize query --help  # Specific command help
```

## Requirements

- Python 3.10+
- SQL2.AI account (free tier available)

## Links

- Website: https://sql2.ai
- Documentation: https://sql2.ai/docs/cli
- Issues: https://github.com/dbbuilder-org/sql2ai/issues
