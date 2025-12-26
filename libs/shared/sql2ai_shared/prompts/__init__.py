"""Versionable prompts system for SQL2.AI.

This module provides:
- Version-tracked prompts with content hashing
- Prompt harnesses for consistent context and guardrails
- Execution tracking for metrics and A/B testing
- Integration with AI services

Usage:
    from sql2ai_shared.prompts import (
        QueryGenerationPrompt,
        PromptExecutor,
        prompt_registry,
    )

    # Create and execute a prompt
    prompt = QueryGenerationPrompt(
        request="Get active customers",
        dialect=DatabaseDialect.SQLSERVER,
        schema_context="...",
    )

    executor = PromptExecutor(ai_service)
    result = await executor.execute(prompt)

    print(result.content)  # Generated SQL
    print(result.prompt_hash)  # For tracking
"""

from sql2ai_shared.prompts.base import (
    Prompt,
    PromptVersion,
    PromptMetadata,
    PromptRegistry,
    PromptExecution,
    prompt_registry,
)
from sql2ai_shared.prompts.harness import (
    PromptHarness,
    HarnessContext,
    SQLExpertHarness,
    DBAHarness,
    ComplianceHarness,
    PerformanceHarness,
    MigrationHarness,
)
from sql2ai_shared.prompts.templates import (
    QueryGenerationPrompt,
    QueryFromExamplePrompt,
    QueryOptimizationPrompt,
    QueryExplanationPrompt,
    SchemaAnalysisPrompt,
    CodeReviewPrompt,
    ComplianceCheckPrompt,
    MigrationPrompt,
    ErrorAnalysisPrompt,
    StoredProcedurePrompt,
)
from sql2ai_shared.prompts.executor import (
    PromptExecutor,
    ExecutionConfig,
    ExecutionResult,
    PromptExecutionLogger,
    ABTestManager,
    ABExperiment,
)

__all__ = [
    # Base
    "Prompt",
    "PromptVersion",
    "PromptMetadata",
    "PromptRegistry",
    "PromptExecution",
    "prompt_registry",
    # Harnesses
    "PromptHarness",
    "HarnessContext",
    "SQLExpertHarness",
    "DBAHarness",
    "ComplianceHarness",
    "PerformanceHarness",
    "MigrationHarness",
    # Templates
    "QueryGenerationPrompt",
    "QueryFromExamplePrompt",
    "QueryOptimizationPrompt",
    "QueryExplanationPrompt",
    "SchemaAnalysisPrompt",
    "CodeReviewPrompt",
    "ComplianceCheckPrompt",
    "MigrationPrompt",
    "ErrorAnalysisPrompt",
    "StoredProcedurePrompt",
    # Executor
    "PromptExecutor",
    "ExecutionConfig",
    "ExecutionResult",
    "PromptExecutionLogger",
    "ABTestManager",
    "ABExperiment",
]
