# SQL2.AI SSMS Extension

AI-powered SQL Server Management Studio extension for query optimization, code review, and DDL generation.

## Features

### Query Optimization
- **Optimize Query** (Ctrl+Alt+O): Analyze selected SQL for performance issues and get optimization suggestions
- **Analyze Execution Plan**: Get AI-powered analysis of execution plan XML with actionable recommendations

### Code Review
- **Review Code** (Ctrl+Alt+R): Check SQL code for security vulnerabilities, performance anti-patterns, and best practice violations
- Security analysis (SQL injection, xp_cmdshell, hardcoded credentials)
- Performance analysis (SELECT *, cursors, NOLOCK, leading wildcards)
- Style and best practice checks

### Code Generation
- **Generate CRUD Procedures**: Auto-generate Create, Read, Update, Delete, List, Search stored procedures for any table
- **Generate from Prompt** (Ctrl+Alt+G): Generate stored procedures, views, functions, triggers, or tables from natural language descriptions

### Query Understanding
- **Explain Query** (Ctrl+Alt+E): Get a natural language explanation of what a SQL query does

## Installation

1. Download the latest `.vsix` file from releases
2. Double-click to install, or use Extensions > Manage Extensions in Visual Studio
3. Restart SSMS/Visual Studio
4. Configure your API key: Tools > SQL2.AI > Settings

## Configuration

### API Key
Get your API key at https://sql2.ai and configure it in Settings.

### Local LLM (Air-gapped environments)
For environments without internet access, configure a local LLM endpoint:
1. Set up Ollama or compatible local LLM server
2. Enable "Use local LLM" in Settings
3. Enter your local endpoint (default: http://localhost:11434)

## Keyboard Shortcuts

| Command | Shortcut |
|---------|----------|
| Optimize Query | Ctrl+Alt+O |
| Review Code | Ctrl+Alt+R |
| Explain Query | Ctrl+Alt+E |
| Generate from Prompt | Ctrl+Alt+G |

## Context Menu

Right-click on selected SQL code to access:
- SQL2.AI: Optimize
- SQL2.AI: Review
- SQL2.AI: Explain

## Requirements

- SQL Server Management Studio 18+ or Visual Studio 2022+
- .NET Framework 4.8
- Internet connection (or local LLM for offline use)
- SQL2.AI API key

## Building from Source

```bash
# Open solution in Visual Studio 2022
cd apps/ssms-addin
start SQL2AI.SSMS.sln

# Build solution
msbuild /p:Configuration=Release

# Output: bin/Release/SQL2AI.SSMS.vsix
```

## Project Structure

```
src/
├── SQL2AIPackage.cs          # Main extension package
├── SQL2AIPackage.vsct        # Command table (menus, buttons)
├── Commands/
│   ├── BaseCommand.cs        # Base class for all commands
│   ├── OptimizeQueryCommand.cs
│   ├── ReviewCodeCommand.cs
│   ├── ExplainQueryCommand.cs
│   ├── GenerateCrudCommand.cs
│   ├── GenerateFromPromptCommand.cs
│   ├── AnalyzeExecutionPlanCommand.cs
│   └── SettingsCommand.cs
├── Services/
│   ├── Sql2AiApiClient.cs    # HTTP client for SQL2.AI API
│   └── SettingsService.cs    # Settings persistence
├── UI/
│   ├── SettingsDialog.cs     # Settings configuration dialog
│   └── PromptDialog.cs       # Natural language prompt dialog
└── Models/
    └── ApiModels.cs          # API request/response models
```

## Support

- Documentation: https://sql2.ai/docs
- Issues: https://github.com/sql2ai/ssms-extension/issues
- Email: support@sql2.ai

## License

Copyright 2024 SQL2.AI. All rights reserved.
