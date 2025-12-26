using System;
using System.Collections.Generic;

namespace SQL2AI.SSMS.Models
{
    /// <summary>
    /// Response from query optimization API.
    /// </summary>
    public class OptimizationResult
    {
        public string OriginalQuery { get; set; } = string.Empty;
        public string OptimizedQuery { get; set; } = string.Empty;
        public List<OptimizationSuggestion> Suggestions { get; set; } = new();
        public double EstimatedImprovement { get; set; }
        public List<string> Warnings { get; set; } = new();
    }

    public class OptimizationSuggestion
    {
        public string Title { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string Severity { get; set; } = "info";
        public string? FixScript { get; set; }
    }

    /// <summary>
    /// Response from code review API.
    /// </summary>
    public class CodeReviewResult
    {
        public bool Passed { get; set; }
        public List<ReviewIssue> Issues { get; set; } = new();
        public int CriticalCount { get; set; }
        public int HighCount { get; set; }
        public int MediumCount { get; set; }
        public int LowCount { get; set; }
    }

    public class ReviewIssue
    {
        public string RuleId { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public string Severity { get; set; } = string.Empty;
        public string Message { get; set; } = string.Empty;
        public int? LineNumber { get; set; }
        public string? CodeSnippet { get; set; }
        public string? Suggestion { get; set; }
    }

    /// <summary>
    /// Response from query explanation API.
    /// </summary>
    public class QueryExplanation
    {
        public string Query { get; set; } = string.Empty;
        public string Summary { get; set; } = string.Empty;
        public List<string> Steps { get; set; } = new();
        public List<string> TablesInvolved { get; set; } = new();
        public string? PerformanceNotes { get; set; }
    }

    /// <summary>
    /// Response from CRUD generation API.
    /// </summary>
    public class CrudGenerationResult
    {
        public string TableName { get; set; } = string.Empty;
        public List<GeneratedProcedure> Procedures { get; set; } = new();
        public string CombinedScript { get; set; } = string.Empty;
    }

    public class GeneratedProcedure
    {
        public string Name { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string Script { get; set; } = string.Empty;
    }

    /// <summary>
    /// Response from execution plan analysis API.
    /// </summary>
    public class ExecutionPlanAnalysis
    {
        public string QueryHash { get; set; } = string.Empty;
        public string Summary { get; set; } = string.Empty;
        public List<PlanIssue> Issues { get; set; } = new();
        public List<string> Recommendations { get; set; } = new();
        public double EstimatedCost { get; set; }
    }

    public class PlanIssue
    {
        public string Operator { get; set; } = string.Empty;
        public string Issue { get; set; } = string.Empty;
        public string Impact { get; set; } = string.Empty;
        public string? Fix { get; set; }
    }

    /// <summary>
    /// Request for DDL generation.
    /// </summary>
    public class DdlGenerationRequest
    {
        public string Prompt { get; set; } = string.Empty;
        public string ObjectType { get; set; } = "stored_procedure";
        public List<string> ContextTables { get; set; } = new();
        public bool IncludeErrorHandling { get; set; } = true;
        public bool IncludeAuditLogging { get; set; } = false;
    }

    /// <summary>
    /// Response from DDL generation API.
    /// </summary>
    public class DdlGenerationResult
    {
        public string ObjectType { get; set; } = string.Empty;
        public string ObjectName { get; set; } = string.Empty;
        public string SqlScript { get; set; } = string.Empty;
        public string? RollbackScript { get; set; }
        public List<string> Warnings { get; set; } = new();
        public List<string> SecurityNotes { get; set; } = new();
    }

    /// <summary>
    /// Configuration for the extension.
    /// </summary>
    public class ExtensionSettings
    {
        public string ApiBaseUrl { get; set; } = "https://api.sql2.ai";
        public string? ApiKey { get; set; }
        public bool EnableInlineCompletion { get; set; } = true;
        public bool ShowNotifications { get; set; } = true;
        public int RequestTimeoutSeconds { get; set; } = 30;
        public bool UseLocalLlm { get; set; } = false;
        public string? LocalLlmEndpoint { get; set; }
    }
}
