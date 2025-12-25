# SQL2.AI Platform Architecture

## Executive Summary

This document outlines the common platform architecture for SQL2.AI, designed to maximize code reuse across 8 existing MVP projects totaling ~76,000 lines of code. By extracting shared patterns into reusable libraries, we can reduce duplication by 40-60% and accelerate new feature development by 30-50%.

## Existing Codebase Analysis

### Project Inventory

| Project | Stack | Purpose | Lines |
|---------|-------|---------|-------|
| **sql-monitor** | .NET 8, Dapper, SQL Server | Real-time monitoring | ~15,000 |
| **sqlauditor** | .NET 8, EF Core, React | Database auditing | ~12,000 |
| **bcpplus** | .NET 8, EF Core | AI-powered data import | ~18,000 |
| **postgresanalyze** | Python, OpenAI | PostgreSQL log analysis | ~8,000 |
| **SQLMCP** | Next.js, Prisma | MCP integration | ~5,000 |
| **SSMS-AI** | .NET 4.7+, WPF | SSMS plugin | ~4,000 |
| **SQLReleaseNotes2** | .NET, Python, React | Release notes | ~8,000 |
| **sqldepends** | Python | Dependency analysis | ~6,000 |

### Common Patterns Identified

1. **Database Connectivity** - Every project connects to SQL Server/PostgreSQL
2. **AI/LLM Integration** - 5 projects use OpenAI for analysis/generation
3. **Configuration Management** - JSON/YAML configs with environment overrides
4. **File Processing** - CSV, Excel, JSON, log file parsing
5. **Authentication** - JWT, OAuth, database RBAC

---

## Shared Library Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                        SQL2.AI PLATFORM                             │
├────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │
│  │  SQL2.AI    │ │  SQL2.AI    │ │  SQL2.AI    │ │  SQL2.AI    │  │
│  │   Monitor   │ │   Migrate   │ │   Comply    │ │   Import    │  │
│  │   (Next)    │ │   (.NET)    │ │   (Python)  │ │   (.NET)    │  │
│  └──────┬──────┘ └──────┬──────┘ └──────┬──────┘ └──────┬──────┘  │
│         │               │               │               │          │
│         └───────────────┴───────────────┴───────────────┘          │
│                                 │                                   │
│  ┌──────────────────────────────┴──────────────────────────────┐   │
│  │                    SHARED LIBRARIES                          │   │
│  ├──────────────────────────────────────────────────────────────┤   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │ SQL2AI.Core  │  │  SQL2AI.AI   │  │ SQL2AI.Auth  │       │   │
│  │  │              │  │              │  │              │       │   │
│  │  │ • Connection │  │ • OpenAI     │  │ • JWT        │       │   │
│  │  │ • Query Exec │  │ • Claude     │  │ • OAuth      │       │   │
│  │  │ • Pooling    │  │ • Local LLM  │  │ • RBAC       │       │   │
│  │  │ • Metrics    │  │ • Embeddings │  │ • Multi-tenant│      │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │   │
│  │  │SQL2AI.Files  │  │SQL2AI.Config │  │SQL2AI.Monitor│       │   │
│  │  │              │  │              │  │              │       │   │
│  │  │ • CSV        │  │ • JSON/YAML  │  │ • DMV Collect│       │   │
│  │  │ • Excel      │  │ • Env Vars   │  │ • Metrics    │       │   │
│  │  │ • JSON       │  │ • Validation │  │ • Alerting   │       │   │
│  │  │ • Logs       │  │ • Secrets    │  │ • Baselines  │       │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘       │   │
│  │                                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Library Specifications

### 1. SQL2AI.Core (.NET 8.0)

**Purpose:** Database connectivity and query execution abstraction

```
libs/sql2ai-core/
├── src/
│   ├── Connection/
│   │   ├── IDatabaseConnection.cs
│   │   ├── SqlServerConnection.cs
│   │   ├── PostgresConnection.cs
│   │   └── ConnectionFactory.cs
│   ├── Query/
│   │   ├── IQueryExecutor.cs
│   │   ├── QueryMetrics.cs
│   │   └── QueryCache.cs
│   ├── Models/
│   │   ├── DatabaseConnectionInfo.cs
│   │   ├── ServerInfo.cs
│   │   └── DatabaseInfo.cs
│   └── Exceptions/
│       ├── ConnectionException.cs
│       └── QueryException.cs
├── tests/
└── SQL2AI.Core.csproj
```

**Key Interfaces:**

```csharp
public interface IDatabaseConnection : IAsyncDisposable
{
    Task<IEnumerable<T>> QueryAsync<T>(string sql, object? parameters = null);
    Task<T?> QuerySingleAsync<T>(string sql, object? parameters = null);
    Task<int> ExecuteAsync(string sql, object? parameters = null);
    IAsyncEnumerable<T> StreamAsync<T>(string sql, object? parameters = null);
    Task<QueryMetrics> ExecuteWithMetricsAsync(string sql, object? parameters = null);
}

public interface IConnectionFactory
{
    IDatabaseConnection Create(DatabaseConnectionInfo connectionInfo);
    Task<bool> TestConnectionAsync(DatabaseConnectionInfo connectionInfo);
}
```

**Reuse From:**
- bcpplus: `DatabaseConnectionInfo`, `DatabaseService`
- sqlauditor: Multi-database Entity Framework patterns
- sql-monitor: Dapper query patterns

---

### 2. SQL2AI.AI (.NET 8.0)

**Purpose:** AI/LLM provider abstraction with multi-provider support

```
libs/sql2ai-ai/
├── src/
│   ├── Providers/
│   │   ├── IAiProvider.cs
│   │   ├── OpenAiProvider.cs
│   │   ├── ClaudeProvider.cs
│   │   └── LocalLlamaProvider.cs
│   ├── Services/
│   │   ├── PromptTemplateService.cs
│   │   ├── TokenCounterService.cs
│   │   ├── EmbeddingService.cs
│   │   └── ConversationService.cs
│   ├── Models/
│   │   ├── AiOptions.cs
│   │   ├── AiResponse.cs
│   │   ├── ConversationContext.cs
│   │   └── EmbeddingResult.cs
│   └── Utilities/
│       ├── RetryPolicy.cs
│       └── RateLimiter.cs
├── tests/
└── SQL2AI.AI.csproj
```

**Key Interfaces:**

```csharp
public interface IAiProvider
{
    Task<AiResponse> CompleteAsync(string prompt, AiOptions options);
    IAsyncEnumerable<string> StreamAsync(string prompt, AiOptions options);
    Task<float[]> EmbedAsync(string text);
    Task<AiResponse> AnalyzeAsync(string content, AnalysisType type);
}

public class AiOptions
{
    public string Model { get; set; } = "gpt-4-turbo";
    public float Temperature { get; set; } = 0.7f;
    public int MaxTokens { get; set; } = 4096;
    public string? SystemPrompt { get; set; }
    public Dictionary<string, string> Metadata { get; set; } = new();
}
```

**Reuse From:**
- postgresanalyze: AI configuration, system prompts, framework-aware analysis
- bcpplus: `OpenAIFieldMappingService` for semantic similarity
- SSMS-AI: `OpenAiProvider` abstraction

---

### 3. SQL2AI.Files (.NET 8.0)

**Purpose:** File parsing and transformation pipeline

```
libs/sql2ai-files/
├── src/
│   ├── Processors/
│   │   ├── IFileProcessor.cs
│   │   ├── CsvProcessor.cs
│   │   ├── ExcelProcessor.cs
│   │   ├── JsonProcessor.cs
│   │   ├── XmlProcessor.cs
│   │   └── LogProcessor.cs
│   ├── Analysis/
│   │   ├── SchemaDetector.cs
│   │   ├── DataTypeInferrer.cs
│   │   └── EncodingDetector.cs
│   ├── Transform/
│   │   ├── ITransformer.cs
│   │   ├── ColumnMapper.cs
│   │   └── DataCleaner.cs
│   └── Models/
│       ├── FileAnalysisResult.cs
│       ├── ColumnInfo.cs
│       └── TransformRule.cs
├── tests/
└── SQL2AI.Files.csproj
```

**Key Interfaces:**

```csharp
public interface IFileProcessor
{
    Task<FileAnalysisResult> AnalyzeAsync(Stream input, FileOptions? options = null);
    IAsyncEnumerable<Dictionary<string, object>> StreamRowsAsync(Stream input);
    Task<DataTable> ReadAllAsync(Stream input, int? maxRows = null);
}

public class FileAnalysisResult
{
    public string DetectedFormat { get; set; }
    public string DetectedEncoding { get; set; }
    public int EstimatedRowCount { get; set; }
    public List<ColumnInfo> Columns { get; set; }
    public Dictionary<string, object> Metadata { get; set; }
}
```

**Reuse From:**
- bcpplus: `MultiFormatFileService` (CSV, Excel, JSON, XML, PDF)
- postgresanalyze: Log file streaming parser
- sqldepends: Source code parsing patterns

---

### 4. SQL2AI.Config (.NET 8.0)

**Purpose:** Configuration management with validation

```
libs/sql2ai-config/
├── src/
│   ├── Providers/
│   │   ├── IConfigProvider.cs
│   │   ├── JsonConfigProvider.cs
│   │   ├── YamlConfigProvider.cs
│   │   └── EnvironmentConfigProvider.cs
│   ├── Services/
│   │   ├── ConfigurationService.cs
│   │   ├── SecretService.cs
│   │   └── ValidationService.cs
│   ├── Models/
│   │   ├── ConfigSection.cs
│   │   └── ValidationResult.cs
│   └── Attributes/
│       ├── RequiredAttribute.cs
│       └── SecretAttribute.cs
├── tests/
└── SQL2AI.Config.csproj
```

**Key Interfaces:**

```csharp
public interface IConfigProvider
{
    T Load<T>(string path) where T : class, new();
    Task<T> LoadAsync<T>(string path) where T : class, new();
    void Save<T>(T config, string path) where T : class;
    T Merge<T>(T baseConfig, T overrides) where T : class;
}

public interface IConfigurationService
{
    T GetSection<T>(string sectionName) where T : class, new();
    string? GetConnectionString(string name);
    string? GetSecret(string key);
    void Reload();
}
```

**Reuse From:**
- postgresanalyze: Excellent dataclass-based config with validation
- bcpplus: CommandLineOptions patterns
- sql-monitor: Database configuration management

---

### 5. SQL2AI.Auth (.NET 8.0)

**Purpose:** Authentication and authorization

```
libs/sql2ai-auth/
├── src/
│   ├── Providers/
│   │   ├── IAuthProvider.cs
│   │   ├── JwtAuthProvider.cs
│   │   ├── OAuthProvider.cs
│   │   └── ApiKeyAuthProvider.cs
│   ├── Services/
│   │   ├── IAuthorizationService.cs
│   │   ├── RoleBasedAuthorizationService.cs
│   │   └── TenantService.cs
│   ├── Models/
│   │   ├── AuthResult.cs
│   │   ├── User.cs
│   │   ├── Role.cs
│   │   └── Tenant.cs
│   └── Middleware/
│       ├── AuthenticationMiddleware.cs
│       └── TenantMiddleware.cs
├── tests/
└── SQL2AI.Auth.csproj
```

**Reuse From:**
- SQLMCP: NextAuth.js patterns (adapted for .NET)
- bcpplus: `JwtAuthenticationService`
- sql-monitor: RBAC with row-level security

---

### 6. SQL2AI.Monitor (.NET 8.0)

**Purpose:** Database monitoring and metrics collection

```
libs/sql2ai-monitor/
├── src/
│   ├── Collectors/
│   │   ├── IMetricCollector.cs
│   │   ├── DmvCollector.cs
│   │   ├── QueryStoreCollector.cs
│   │   └── ExtendedEventsCollector.cs
│   ├── Analysis/
│   │   ├── BaselineService.cs
│   │   ├── AnomalyDetector.cs
│   │   └── TrendAnalyzer.cs
│   ├── Alerting/
│   │   ├── IAlertProvider.cs
│   │   ├── AlertEngine.cs
│   │   └── ThresholdManager.cs
│   └── Models/
│       ├── Metric.cs
│       ├── Alert.cs
│       └── Baseline.cs
├── tests/
└── SQL2AI.Monitor.csproj
```

**Reuse From:**
- sql-monitor: Complete monitoring schema and procedures
- sql-monitor: Baseline detection algorithms
- sql-monitor: Partitioning strategies

---

## Python Libraries

### sql2ai-core (Python)

```
packages/sql2ai-core-py/
├── sql2ai_core/
│   ├── __init__.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── query_builder.py
│   │   └── connection_pool.py
│   ├── config/
│   │   ├── config_manager.py
│   │   └── validators.py
│   └── logging/
│       └── structured_logger.py
├── tests/
├── pyproject.toml
└── README.md
```

**Reuse From:**
- postgresanalyze: Configuration dataclasses, logging patterns
- sqldepends: Database validation patterns

### sql2ai-ai (Python)

```
packages/sql2ai-ai-py/
├── sql2ai_ai/
│   ├── __init__.py
│   ├── providers/
│   │   ├── base.py
│   │   ├── openai.py
│   │   └── claude.py
│   ├── prompts/
│   │   └── templates.py
│   └── analysis/
│       ├── code_analyzer.py
│       └── log_analyzer.py
├── tests/
├── pyproject.toml
└── README.md
```

**Reuse From:**
- postgresanalyze: AI integration, system prompts, analysis patterns

---

## Directory Structure

```
sql2ai/
├── apps/
│   ├── site/              # Marketing site (Next.js)
│   ├── web/               # Web application (Next.js)
│   └── api/               # API server (FastAPI)
│
├── libs/                  # Shared .NET libraries
│   ├── sql2ai-core/
│   ├── sql2ai-ai/
│   ├── sql2ai-files/
│   ├── sql2ai-config/
│   ├── sql2ai-auth/
│   └── sql2ai-monitor/
│
├── packages/              # NPM/PyPI packages
│   ├── sql2ai-cli/        # CLI tool (TypeScript)
│   ├── sql2ai-mcp/        # MCP server (TypeScript)
│   ├── sql2ai-sdk/        # SDK (TypeScript)
│   ├── sql2ai-core-py/    # Core (Python)
│   └── sql2ai-ai-py/      # AI (Python)
│
├── tools/                 # Standalone tools
│   ├── ssms-plugin/       # SSMS extension (.NET)
│   └── vscode-extension/  # VS Code extension
│
├── docs/
│   ├── modules/           # Module documentation
│   ├── architecture/      # Architecture docs
│   └── content/           # Blog content plan
│
└── mvp/
    └── original/          # Legacy MVP code (reference)
```

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-4)

**Goals:**
- Create SQL2AI.Core with database connectivity
- Create SQL2AI.Config with configuration management
- Set up NuGet/PyPI package infrastructure
- Migrate bcpplus to use shared libraries

**Deliverables:**
- SQL2AI.Core NuGet package
- SQL2AI.Config NuGet package
- sql2ai-core-py PyPI package
- bcpplus refactored to use shared libs

### Phase 2: AI Integration (Weeks 5-8)

**Goals:**
- Create SQL2AI.AI with multi-provider support
- Create sql2ai-ai-py Python package
- Migrate postgresanalyze to shared AI
- Migrate bcpplus AI features

**Deliverables:**
- SQL2AI.AI NuGet package
- sql2ai-ai-py PyPI package
- postgresanalyze using sql2ai-ai-py
- bcpplus using SQL2AI.AI

### Phase 3: File & Auth (Weeks 9-12)

**Goals:**
- Create SQL2AI.Files for file processing
- Create SQL2AI.Auth for authentication
- Migrate file processing from bcpplus
- Implement unified auth across apps

**Deliverables:**
- SQL2AI.Files NuGet package
- SQL2AI.Auth NuGet package
- Unified auth system
- File processing extraction complete

### Phase 4: Monitoring (Weeks 13-16)

**Goals:**
- Create SQL2AI.Monitor library
- Extract sql-monitor patterns
- Build unified monitoring dashboard
- Implement alerting framework

**Deliverables:**
- SQL2AI.Monitor NuGet package
- Monitoring dashboard MVP
- Alerting system
- Baseline detection

### Phase 5: Integration (Weeks 17-20)

**Goals:**
- All tools using shared libraries
- Unified CLI with all commands
- Common web dashboard
- Complete documentation

**Deliverables:**
- sql2ai CLI with all commands
- Unified web application
- API documentation
- User guides

---

## Code Reuse Metrics

| Library | Source Projects | Est. Lines Extracted | New Features Enabled |
|---------|-----------------|---------------------|---------------------|
| SQL2AI.Core | bcpplus, sqlauditor, sql-monitor | 3,000 | Multi-DB support |
| SQL2AI.AI | postgresanalyze, bcpplus, SSMS-AI | 2,500 | Multi-provider AI |
| SQL2AI.Files | bcpplus, postgresanalyze | 4,000 | Unified file processing |
| SQL2AI.Config | postgresanalyze, bcpplus | 1,500 | Consistent config |
| SQL2AI.Auth | SQLMCP, bcpplus | 2,000 | Unified auth |
| SQL2AI.Monitor | sql-monitor | 5,000 | Monitoring-as-library |
| **Total** | | **~18,000** | |

**Expected Benefits:**
- 40% reduction in code duplication
- 50% faster feature development
- Consistent patterns across all tools
- Easier maintenance and testing
- Better documentation

---

## Next Steps

1. **Create libs/ directory structure**
2. **Initialize SQL2AI.Core project**
3. **Extract DatabaseConnectionInfo from bcpplus**
4. **Create unit test framework**
5. **Set up CI/CD for shared libraries**

---

## References

- [Existing Codebase Analysis](./CODEBASE-ANALYSIS.md)
- [Article Content Plan](../content/ARTICLE-PLAN.md)
- [Module Documentation](../modules/)
