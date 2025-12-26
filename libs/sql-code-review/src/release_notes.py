"""Release notes generator from schema changes."""

from datetime import datetime
from typing import Optional, Callable, Awaitable, Any
from dataclasses import dataclass, field

from models import (
    ReleaseChange,
    ReleaseNotes,
    ChangeType,
)


@dataclass
class SchemaDiff:
    """Represents a schema difference."""
    object_type: str
    object_name: str
    change_type: str  # added, removed, modified
    old_definition: Optional[str] = None
    new_definition: Optional[str] = None
    changes: list[str] = field(default_factory=list)


# Type for AI completion function
AICompletionFunc = Callable[[str, str], Awaitable[str]]


class ReleaseNotesGenerator:
    """Generates release notes from schema changes."""

    def __init__(
        self,
        ai_completion: Optional[AICompletionFunc] = None,
    ):
        """Initialize generator.

        Args:
            ai_completion: Optional AI function for enhanced descriptions
        """
        self.ai_completion = ai_completion

    async def generate(
        self,
        diffs: list[SchemaDiff],
        version: str,
        release_date: Optional[datetime] = None,
    ) -> ReleaseNotes:
        """Generate release notes from schema diffs.

        Args:
            diffs: List of schema differences
            version: Release version string
            release_date: Release date (defaults to now)

        Returns:
            Generated release notes
        """
        if release_date is None:
            release_date = datetime.utcnow()

        changes = []
        breaking_changes = []

        for diff in diffs:
            change = self._diff_to_change(diff)
            changes.append(change)

            if change.change_type == ChangeType.BREAKING:
                breaking_changes.append(change)

        # Generate summary
        summary = self._generate_summary(changes, breaking_changes)

        # Generate migration SQL
        migration_sql = self._generate_migration_sql(diffs)
        rollback_sql = self._generate_rollback_sql(diffs)

        return ReleaseNotes(
            version=version,
            release_date=release_date,
            summary=summary,
            changes=changes,
            breaking_changes=breaking_changes,
            migration_sql=migration_sql,
            rollback_sql=rollback_sql,
        )

    def _diff_to_change(self, diff: SchemaDiff) -> ReleaseChange:
        """Convert a schema diff to a release change."""
        change_type = self._determine_change_type(diff)
        description = self._generate_description(diff)

        breaking_reason = None
        migration_notes = None

        if change_type == ChangeType.BREAKING:
            breaking_reason = self._get_breaking_reason(diff)
            migration_notes = self._get_migration_notes(diff)

        return ReleaseChange(
            change_type=change_type,
            object_name=diff.object_name,
            object_type=diff.object_type,
            description=description,
            breaking_reason=breaking_reason,
            migration_notes=migration_notes,
        )

    def _determine_change_type(self, diff: SchemaDiff) -> ChangeType:
        """Determine the type of change from a diff."""
        # Removed objects are always breaking
        if diff.change_type == "removed":
            return ChangeType.BREAKING

        # Check for breaking modifications
        if diff.change_type == "modified":
            for change in diff.changes:
                change_lower = change.lower()

                # Column removals are breaking
                if "column removed" in change_lower:
                    return ChangeType.BREAKING

                # Data type changes are breaking
                if "type changed" in change_lower:
                    return ChangeType.BREAKING

                # Making columns non-nullable is breaking
                if "nullable" in change_lower and "not null" in change_lower:
                    return ChangeType.BREAKING

                # Removed parameters are breaking
                if "parameter removed" in change_lower:
                    return ChangeType.BREAKING

        # Added objects are features
        if diff.change_type == "added":
            return ChangeType.FEATURE

        # Other modifications are refactoring
        return ChangeType.REFACTOR

    def _generate_description(self, diff: SchemaDiff) -> str:
        """Generate a human-readable description of the change."""
        if diff.change_type == "added":
            return f"Added new {diff.object_type}"

        if diff.change_type == "removed":
            return f"Removed {diff.object_type}"

        if diff.change_type == "modified":
            if diff.changes:
                return "; ".join(diff.changes[:3])  # First 3 changes
            return f"Modified {diff.object_type}"

        return f"Changed {diff.object_type}"

    def _get_breaking_reason(self, diff: SchemaDiff) -> Optional[str]:
        """Get the reason why a change is breaking."""
        if diff.change_type == "removed":
            return f"The {diff.object_type} '{diff.object_name}' has been removed"

        for change in diff.changes:
            change_lower = change.lower()
            if "column removed" in change_lower:
                return "One or more columns have been removed"
            if "type changed" in change_lower:
                return "Column data types have been modified"
            if "parameter removed" in change_lower:
                return "One or more parameters have been removed"

        return None

    def _get_migration_notes(self, diff: SchemaDiff) -> Optional[str]:
        """Get migration notes for a breaking change."""
        if diff.change_type == "removed":
            return f"Update all code that references {diff.object_name}"

        for change in diff.changes:
            change_lower = change.lower()
            if "column removed" in change_lower:
                return "Update queries and code that reference the removed columns"
            if "type changed" in change_lower:
                return "Verify data compatibility and update client code as needed"

        return None

    def _generate_summary(
        self,
        changes: list[ReleaseChange],
        breaking_changes: list[ReleaseChange],
    ) -> str:
        """Generate a summary of changes."""
        parts = []

        if breaking_changes:
            parts.append(f"**{len(breaking_changes)} breaking change(s)**")

        features = sum(1 for c in changes if c.change_type == ChangeType.FEATURE)
        fixes = sum(1 for c in changes if c.change_type == ChangeType.FIX)
        refactors = sum(1 for c in changes if c.change_type == ChangeType.REFACTOR)

        if features:
            parts.append(f"{features} new feature(s)")
        if fixes:
            parts.append(f"{fixes} bug fix(es)")
        if refactors:
            parts.append(f"{refactors} refactoring change(s)")

        if not parts:
            return "No significant changes in this release."

        return "This release includes " + ", ".join(parts) + "."

    def _generate_migration_sql(self, diffs: list[SchemaDiff]) -> Optional[str]:
        """Generate migration SQL from diffs."""
        scripts = []

        for diff in diffs:
            if diff.new_definition:
                scripts.append(f"-- {diff.object_type}: {diff.object_name}")
                scripts.append(diff.new_definition)
                scripts.append("")

        if scripts:
            return "\n".join(scripts)
        return None

    def _generate_rollback_sql(self, diffs: list[SchemaDiff]) -> Optional[str]:
        """Generate rollback SQL from diffs."""
        scripts = []

        for diff in reversed(diffs):
            if diff.change_type == "added" and diff.object_type:
                scripts.append(f"-- Rollback: Remove {diff.object_name}")
                scripts.append(f"DROP {diff.object_type.upper()} IF EXISTS {diff.object_name};")
                scripts.append("")

            elif diff.change_type == "removed" and diff.old_definition:
                scripts.append(f"-- Rollback: Restore {diff.object_name}")
                scripts.append(diff.old_definition)
                scripts.append("")

            elif diff.change_type == "modified" and diff.old_definition:
                scripts.append(f"-- Rollback: Revert {diff.object_name}")
                scripts.append(diff.old_definition)
                scripts.append("")

        if scripts:
            return "\n".join(scripts)
        return None


class GitReleaseNotesGenerator:
    """Generates release notes by comparing Git commits."""

    def __init__(
        self,
        repo_path: str,
        ai_completion: Optional[AICompletionFunc] = None,
    ):
        """Initialize with repository path.

        Args:
            repo_path: Path to Git repository
            ai_completion: Optional AI function for enhanced descriptions
        """
        self.repo_path = repo_path
        self.ai_completion = ai_completion
        self.notes_generator = ReleaseNotesGenerator(ai_completion)

    async def generate_from_tags(
        self,
        from_tag: str,
        to_tag: str,
    ) -> ReleaseNotes:
        """Generate release notes between two Git tags.

        Args:
            from_tag: Starting tag (older)
            to_tag: Ending tag (newer)

        Returns:
            Generated release notes
        """
        # This would typically:
        # 1. Get list of changed SQL files between tags
        # 2. Parse the SQL files to extract schema changes
        # 3. Generate release notes from the diffs

        # Placeholder implementation
        diffs = await self._get_diffs_between_tags(from_tag, to_tag)
        return await self.notes_generator.generate(diffs, to_tag)

    async def _get_diffs_between_tags(
        self,
        from_tag: str,
        to_tag: str,
    ) -> list[SchemaDiff]:
        """Get schema diffs between two tags."""
        # In production, this would:
        # 1. Use GitPython to get changed files
        # 2. Parse SQL files to extract object definitions
        # 3. Compare objects to generate diffs

        # Placeholder
        return []
