# SSMS-AI: Intelligent SQL Server Management Studio Add-in

## Overview
SSMS-AI is a powerful add-in for SQL Server Management Studio that leverages AI capabilities from ChatGPT, Gemini, and Claude to enhance SQL development productivity. Right-click any database object or use the query window to get AI-powered explanations, code improvements, error handling, logging, and comprehensive documentation.

## Features
- **AI-Powered Object Analysis**: Right-click any table, view, stored procedure, or function to get detailed explanations
- **Automated Code Enhancement**: Add error handling, logging, and documentation with a single click
- **Intelligent Code Review**: Get AI-driven suggestions for code improvements
- **Batch Processing**: Process entire scripts with AI enhancements
- **Multi-Provider Support**: Choose between ChatGPT, Gemini, or Claude based on your needs
- **SQLAI: Comments**: Convert special comments into fully functional code

## Quick Start

### Prerequisites
- SQL Server Management Studio 18.x or 19.x
- .NET Framework 4.8
- Active API key for at least one AI provider (ChatGPT, Gemini, or Claude)
- Windows 10 or Windows 11

### Installation
1. Download the latest SSMS-AI.vsix file from the releases page
2. Double-click the VSIX file to install
3. Restart SSMS
4. Configure your AI provider settings via Tools > Options > SSMS-AI

### Configuration
1. Open Tools > Options > SSMS-AI
2. Select your preferred AI provider
3. Enter your API key (stored securely in Azure Key Vault)
4. Configure default actions and preferences
5. Test connection to verify setup

## Usage

### Object Context Menu
1. Right-click any database object in Object Explorer
2. Select "SSMS-AI" from the context menu
3. Choose your desired action:
   - **Explain**: Get comprehensive documentation
   - **Add Error Handling**: Wrap in TRY-CATCH blocks
   - **Add Logging**: Insert debug/trace statements
   - **Code Review**: Get improvement suggestions
   - **Add Comment Header**: Generate detailed documentation

### Query Window Features
1. Write SQL with special comments:
   ```sql
   -- SQLAI: Create a stored procedure to get top customers by sales
   ```
2. Right-click in the query window and select "SSMS-AI > Process SQLAI Comments"
3. Watch as your comments transform into complete SQL code

### Batch Processing
1. Select multiple batches in your query window
2. Right-click and choose "SSMS-AI > Process Selected Batches"
3. Choose actions to apply to all batches
## Architecture

### Technology Stack
- **Framework**: .NET Framework 4.8 (SSMS compatibility)
- **Language**: C# 10
- **UI**: WPF with MVVM pattern
- **AI Integration**: REST APIs via HttpClient
- **Logging**: Serilog with Application Insights
- **Resilience**: Polly for retry policies
- **Security**: Azure Key Vault for secrets

### Project Structure
```
SSMS-AI/
├── src/
│   ├── SSMS-AI.Core/           # Core business logic
│   ├── SSMS-AI.AI/             # AI provider interfaces
│   ├── SSMS-AI.SSMS/           # SSMS integration
│   ├── SSMS-AI.UI/             # User interface
│   └── SSMS-AI.Tests/          # Unit tests
├── docs/                        # Documentation
├── samples/                     # Example scripts
└── tools/                       # Build tools

```

## Development

### Building from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/SSMS-AI.git

# Restore NuGet packages
nuget restore SSMS-AI.sln

# Build the solution
msbuild SSMS-AI.sln /p:Configuration=Release
```

### Running Tests
```bash
# Run all tests
dotnet test

# Run with coverage
dotnet test /p:CollectCoverage=true
```

### Debugging
1. Set SSMS as the external program in project properties
2. Set command line arguments: /log
3. F5 to start debugging

## Contributing
Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### Code Style
- Follow C# coding conventions
- Use meaningful variable names
- Add XML documentation to public APIs
- Write unit tests for new features
- Ensure all tests pass before submitting PR

## Support
- **Documentation**: See the [docs](docs/) folder
- **Issues**: Report bugs on [GitHub Issues](https://github.com/yourusername/SSMS-AI/issues)
- **Discussions**: Join our [community forum](https://github.com/yourusername/SSMS-AI/discussions)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- SQL Server Management Studio extensibility team
- OpenAI, Google, and Anthropic for their AI APIs
- All contributors and beta testers