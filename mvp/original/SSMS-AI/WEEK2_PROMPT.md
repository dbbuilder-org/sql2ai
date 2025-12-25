# SSMS-AI Week 2 Development Prompt

Use this prompt to continue development in your next chat session:

---

**Title**: "SSMS-AI Week 2 - Context Menu Integration & Basic Functionality"

**Prompt**:
"I'm continuing development of SSMS-AI, an add-in for SQL Server Management Studio that integrates AI capabilities. Week 1 is complete with the following accomplished:

**Week 1 Completed:**
- Visual Studio solution created at D:\dev2\SSMS-AI\src\
- Three projects: SSMS-AI.Core, SSMS-AI.AI, and SSMS-AI.SSMS (VSIX)
- Basic package initialization with logging (Serilog)
- AI provider interface (IAiProvider) defined
- OpenAI provider implementation with Polly retry logic
- Configuration management with DPAPI encryption
- Basic dependency injection container

**Current Project Structure:**
- All requirements in D:\dev2\SSMS-AI\REQUIREMENTS.md
- MVP plan in TODO.md (Phase 1, Week 2 tasks)
- Core interfaces defined but not yet connected to SSMS

**Week 2 Goals (from TODO.md):**
1. Implement IObjectExplorerExtender to hook into SSMS context menus
2. Create context menu commands for stored procedures only
3. Add "Explain with AI" menu item that appears on right-click
4. Connect the menu action to the OpenAI provider
5. Create a simple WPF configuration dialog for API key entry
6. Test the full flow: right-click stored procedure → explain → show AI response

**Technical Context:**
- Using .NET Framework 4.8 (SSMS requirement)
- VSIX package for SSMS 18.x/19.x
- Must use MEF (Managed Extensibility Framework) for SSMS integration
- Configuration stored in %APPDATA%\SSMS-AI\config.json (encrypted)

Please help me implement the context menu integration. I need:
1. The IObjectExplorerExtender implementation
2. Command registration in the package
3. Menu item visibility logic for stored procedures
4. Connection to the OpenAI provider
5. Simple result display dialog

Focus on getting one feature working end-to-end before adding complexity."

**Additional Files to Reference:**
- D:\dev2\SSMS-AI\src\SSMS-AI.Core\AI\IAiProvider.cs
- D:\dev2\SSMS-AI\src\SSMS-AI.AI\Providers\OpenAiProvider.cs
- D:\dev2\SSMS-AI\src\SSMS-AI.SSMS\SsmsAiPackage.cs
- D:\dev2\SSMS-AI\src\SSMS-AI.Core\Configuration\ConfigurationManager.cs
