"""SQL Migrator - Database-first migrations with code generation."""

from models import (
    Migration,
    MigrationStep,
    MigrationStatus,
    BreakingChange,
    BreakingChangeSeverity,
    GeneratedCode,
    CodeLanguage,
)
from generator import MigrationGenerator
from codegen import (
    CodeGenerator,
    DapperGenerator,
    TypeScriptGenerator,
    ZodSchemaGenerator,
)
from executor import MigrationExecutor

__all__ = [
    # Models
    "Migration",
    "MigrationStep",
    "MigrationStatus",
    "BreakingChange",
    "BreakingChangeSeverity",
    "GeneratedCode",
    "CodeLanguage",
    # Generator
    "MigrationGenerator",
    # Code generators
    "CodeGenerator",
    "DapperGenerator",
    "TypeScriptGenerator",
    "ZodSchemaGenerator",
    # Executor
    "MigrationExecutor",
]
