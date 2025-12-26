# SQL2.AI VS Code Extension

AI-powered database development assistant for SQL Server and PostgreSQL.

## Features

- **Query Optimization** (`Ctrl+Alt+O`) - Get AI-powered suggestions to improve query performance
- **Query Explanation** (`Ctrl+Alt+E`) - Understand what your SQL does in plain English
- **Code Review** (`Ctrl+Alt+R`) - Detect security issues, performance problems, and style violations
- **Generate SQL** (`Ctrl+Alt+G`) - Generate SQL from natural language prompts
- **CRUD Generation** - Auto-generate Create, Read, Update, Delete procedures
- **Execution Plan Analysis** - AI insights on query execution plans
- **SQL Formatting** - Format SQL code consistently

## Installation

1. Install from VS Code Marketplace (search "SQL2.AI")
2. Or install the `.vsix` file manually

## Configuration

Open VS Code Settings (`Ctrl+,`) and search for "SQL2.AI":

| Setting | Description | Default |
|---------|-------------|---------|
| `sql2ai.apiUrl` | SQL2.AI API URL | `https://api.sql2.ai` |
| `sql2ai.apiKey` | Your SQL2.AI API key | (empty) |
| `sql2ai.defaultDatabase` | Default database type | `postgresql` |
| `sql2ai.autoFormat` | Format SQL on save | `false` |
| `sql2ai.showInlineHints` | Show optimization hints | `true` |

## Getting an API Key

1. Sign up at [app.sql2.ai](https://app.sql2.ai)
2. Go to Settings → API Keys
3. Generate a new API key
4. Copy the key to VS Code settings

## Usage

### Context Menu

Right-click in any SQL file to access SQL2.AI commands.

### Keyboard Shortcuts

| Shortcut | Command |
|----------|---------|
| `Ctrl+Alt+O` | Optimize Query |
| `Ctrl+Alt+E` | Explain Query |
| `Ctrl+Alt+R` | Review Code |
| `Ctrl+Alt+G` | Generate SQL |

### Command Palette

Open the Command Palette (`Ctrl+Shift+P`) and type "SQL2.AI" to see all available commands.

## Activity Bar

Click the SQL2.AI icon in the Activity Bar to view:
- **Connections** - Your database connections
- **History** - Recent AI operations
- **Snippets** - Saved AI-generated code

## Requirements

- VS Code 1.85.0 or later
- SQL2.AI account (free tier available)
- Internet connection

## Support

- Documentation: [sql2.ai/docs](https://sql2.ai/docs)
- Issues: [GitHub Issues](https://github.com/dbbuilder-org/sql2ai/issues)
- Email: support@sql2.ai

## License

MIT
