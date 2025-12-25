# SSMS Plugin

**Module 6 of 8** | **Status:** Planned | **Priority:** P2

## Overview

The SSMS Plugin brings SQL2.AI capabilities directly into SQL Server Management Studio. Get AI-powered query assistance, inline suggestions, execution plan analysis, and code generation without leaving your familiar IDE.

## Problems Solved

| Problem | Current State | SSMS Plugin Solution |
|---------|---------------|----------------------|
| Context switching | Alt-tab to AI chat | AI inline in editor |
| Copy/paste workflow | Copy SQL, paste in AI | Right-click integration |
| No inline suggestions | Manual typing | Copilot-style completions |
| Plan analysis | Manual interpretation | AI-explained plans |
| SP generation | Write from scratch | Generate from table |

## Features

### 1. Inline Query Completions

As you type, AI suggests completions:

```sql
SELECT c.CustomerID, c.Name, |
                             ↓
┌──────────────────────────────────────────────────┐
│ c.Email, c.Phone                                 │ (based on table)
│ COUNT(*) AS OrderCount                           │ (aggregation)
│ o.OrderDate, o.TotalAmount                       │ (with JOIN)
└──────────────────────────────────────────────────┘
```

### 2. Right-Click Context Menu

Select any SQL code and right-click:

```
┌─────────────────────────────────┐
│ Cut                             │
│ Copy                            │
│ Paste                           │
├─────────────────────────────────┤
│ SQL2.AI                      ▸  │
│   ├─ Explain Query              │
│   ├─ Optimize Query             │
│   ├─ Review for Issues          │
│   ├─ Generate Test Data         │
│   └─ Add Error Handling         │
├─────────────────────────────────┤
│ Execute                         │
└─────────────────────────────────┘
```

### 3. Execution Plan Analysis

After running a query with "Include Actual Execution Plan":

```
┌─────────────────────────────────────────────────────────────┐
│ SQL2.AI Execution Plan Analysis                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ⚠ PERFORMANCE ISSUES DETECTED                              │
│                                                             │
│ 1. Table Scan on Orders (Cost: 67%)                        │
│    Problem: No suitable index for WHERE clause             │
│    Fix: CREATE INDEX IX_Orders_Status ON Orders(Status)    │
│    [Apply Fix] [Copy Script]                               │
│                                                             │
│ 2. Key Lookup (Cost: 23%)                                  │
│    Problem: Index doesn't include all selected columns     │
│    Fix: Add INCLUDE columns or create covering index       │
│    [Show Details] [Apply Fix]                              │
│                                                             │
│ 3. Implicit Conversion                                     │
│    Problem: VARCHAR compared to NVARCHAR                   │
│    Fix: Cast parameter to match column type                │
│    [Show Location]                                         │
│                                                             │
│ Estimated Improvement: 85% faster execution                │
│                                                             │
│ [Apply All Fixes] [Generate Report] [Dismiss]              │
└─────────────────────────────────────────────────────────────┘
```

### 4. Object Explorer Integration

Right-click on tables in Object Explorer:

```
┌─────────────────────────────────┐
│ Tables                          │
│   └─ dbo.Customers              │
│        Right-click:             │
│        ├─ Select Top 1000       │
│        ├─ Edit Top 200          │
│        ├─ Script Table as ▸     │
│        ├─ ─────────────────     │
│        ├─ SQL2.AI            ▸  │
│        │   ├─ Generate CRUD SPs │
│        │   ├─ Generate API Model│
│        │   ├─ Document Table    │
│        │   ├─ Suggest Indexes   │
│        │   └─ Find Dependencies │
│        └─ ─────────────────     │
└─────────────────────────────────┘
```

### 5. Query Editor Toolbar

New toolbar buttons in query editor:

```
[📝 Explain] [⚡ Optimize] [🔍 Review] [📊 Analyze Plan] [💡 Suggest]
```

### 6. AI Chat Panel

Dockable panel for conversational AI:

```
┌─────────────────────────────────────────────────────────────┐
│ SQL2.AI Assistant                               [_] [□] [X] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ You: How can I improve this query's performance?            │
│                                                             │
│ SQL2.AI: I analyzed your query and found:                   │
│                                                             │
│ 1. The Orders table scan can be eliminated by adding        │
│    an index on (CustomerID, OrderDate).                     │
│                                                             │
│ 2. The subquery in the SELECT list is being executed        │
│    for each row. Consider using a JOIN instead.             │
│                                                             │
│ Here's the optimized version:                               │
│ ```sql                                                      │
│ SELECT c.Name, o.OrderDate, ot.TotalItems                   │
│ FROM Customers c                                            │
│ JOIN Orders o ON c.CustomerID = o.CustomerID                │
│ JOIN (SELECT OrderID, COUNT(*) as TotalItems               │
│       FROM OrderItems GROUP BY OrderID) ot                  │
│   ON o.OrderID = ot.OrderID                                 │
│ ```                                                         │
│ [Apply to Editor] [Copy] [Explain More]                     │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Type a message...                              [Send] [📎]  │
└─────────────────────────────────────────────────────────────┘
```

## Architecture

### Technical Stack
- C# / .NET Framework (SSMS uses .NET)
- Visual Studio SDK for SSMS extensibility
- MEF (Managed Extensibility Framework)
- WPF for UI components

### Deployment Options

**1. Cloud-Connected (Default)**
- Connects to SQL2.AI API
- Full AI capabilities
- Requires internet access

**2. Local LLM (Air-Gapped)**
- Uses local LLM (Ollama, LM Studio)
- Works without internet
- Limited to available local models

```
┌─────────────────────────────────────────────────────────────┐
│ SQL2.AI Settings                                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ AI Provider:                                                │
│ ○ SQL2.AI Cloud (Recommended)                               │
│   API Key: [••••••••••••••••••••••] [Verify]                │
│                                                             │
│ ○ Local LLM                                                 │
│   Endpoint: [http://localhost:11434/api] [Test]             │
│   Model: [codellama:13b ▼]                                  │
│                                                             │
│ Features:                                                   │
│ ☑ Inline completions                                        │
│ ☑ Execution plan analysis                                   │
│ ☑ Right-click menu integration                              │
│ ☐ Auto-suggest on idle (3 seconds)                          │
│                                                             │
│ [Save] [Cancel]                                             │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Requirements
- SQL Server Management Studio 18.x or 19.x
- .NET Framework 4.7.2+
- Windows 10/11 or Windows Server 2016+

### Installation Steps
```
1. Download SQL2AI.SSMS.vsix from sql2.ai/downloads
2. Close SSMS
3. Double-click the .vsix file
4. Follow installation wizard
5. Restart SSMS
6. Configure API key in Tools → SQL2.AI Settings
```

## Commands Reference

| Command | Shortcut | Description |
|---------|----------|-------------|
| Explain Query | Ctrl+Shift+E | Explain selected SQL |
| Optimize Query | Ctrl+Shift+O | Get optimization suggestions |
| Review Code | Ctrl+Shift+R | Check for issues |
| Analyze Plan | Ctrl+Shift+P | Analyze execution plan |
| Generate SP | Ctrl+Shift+G | Generate procedure from table |
| AI Chat | Ctrl+Shift+A | Open AI chat panel |

## Privacy & Security

- Queries are sent to SQL2.AI API (or local LLM)
- Connection strings are NOT transmitted
- Query results are NOT transmitted
- All communication is encrypted (TLS 1.3)
- Option to anonymize identifiers before sending
- Full audit log of AI interactions

## Implementation Status

- [ ] SSMS extension framework
- [ ] Query editor integration
- [ ] Inline completions
- [ ] Right-click menu
- [ ] Execution plan analyzer
- [ ] Object Explorer integration
- [ ] AI chat panel
- [ ] Settings UI
- [ ] Cloud API integration
- [ ] Local LLM support
- [ ] Installation package
