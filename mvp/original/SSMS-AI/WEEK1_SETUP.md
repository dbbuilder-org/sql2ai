# SSMS-AI Week 1 Setup Instructions

## Prerequisites
1. Visual Studio 2019 or 2022 with the following workloads:
   - .NET desktop development
   - Visual Studio extension development
2. SQL Server Management Studio 18.x or 19.x
3. .NET Framework 4.8 SDK

## Initial Setup Steps

### 1. Open the Solution
- Open `D:\dev2\SSMS-AI\src\SSMS-AI.sln` in Visual Studio

### 2. Restore NuGet Packages
- Right-click on the solution in Solution Explorer
- Select "Restore NuGet Packages"

### 3. Build the Solution
- Set the build configuration to "Debug"
- Build the entire solution (Ctrl+Shift+B)

### 4. Configure SSMS Debugging
- Right-click on the SSMS-AI.SSMS project
- Select "Properties"
- Go to "Debug" tab
- Set "Start external program" to your SSMS.exe location
  - Typically: `C:\Program Files (x86)\Microsoft SQL Server Management Studio 18\Common7\IDE\Ssms.exe`
- Set "Command line arguments" to: `/log`

### 5. Test the Extension
- Press F5 to start debugging
- SSMS should launch with the extension loaded
- Check the output window for "SSMS-AI Package initialized successfully"

## Project Structure Created

```
D:\dev2\SSMS-AI\
├── REQUIREMENTS.md          # Full project specifications
├── README.md               # Project overview
├── TODO.md                 # MVP-focused development plan
├── FUTURE.md              # Long-term vision
├── build.bat              # Build script
├── src/
│   ├── SSMS-AI.sln       # Visual Studio solution
│   ├── SSMS-AI.Core/      # Core functionality
│   │   ├── AI/           # AI provider interfaces
│   │   ├── Configuration/ # Config management
│   │   ├── Logging/      # Logging setup
│   │   ├── DependencyInjection/ # DI container
│   │   └── SSMS/         # SSMS interfaces
│   ├── SSMS-AI.AI/       # AI implementations
│   │   └── Providers/    # OpenAI provider
│   └── SSMS-AI.SSMS/     # SSMS extension
│       ├── SsmsAiPackage.cs # Main package class
│       └── source.extension.vsixmanifest
```

## Week 1 Completed Tasks
✅ Created Visual Studio solution structure
✅ Set up project references and dependencies
✅ Configured essential NuGet packages
✅ Defined interfaces for AI providers
✅ Created base classes for SSMS integration
✅ Set up basic logging with Serilog
✅ Created VSIX project structure
✅ Implemented package initialization
✅ Set up configuration management with encryption
✅ Created basic OpenAI provider with retry logic

## Next Steps (Week 2)
- Implement IObjectExplorerExtender for context menu
- Create menu commands for stored procedures
- Connect OpenAI provider to menu actions
- Create basic UI for API key configuration
- Test end-to-end flow

## Known Issues
- The SSMS integration requires specific SDK references that may need to be adjusted based on your SSMS version
- The project currently uses hardcoded test responses until the context menu is implemented
