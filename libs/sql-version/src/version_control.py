"""Main SQL Version control class."""

from datetime import datetime
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

from models import (
    ObjectType,
    ObjectVersion,
    ObjectHistory,
    VersionDiff,
    BlameResult,
    Branch,
    Tag,
    MergeConflict,
    MergeResult,
    SyncStatus,
    VersionControlConfig,
    ChangeAction,
)
from repository import VersionRepository, InMemoryVersionRepository


# Type for database query function
DBQueryFunc = Callable[[str], Awaitable[list[dict]]]


class SQLVersionControl:
    """Git-like version control for SQL Server database objects."""

    def __init__(
        self,
        repository: Optional[VersionRepository] = None,
        db_query: Optional[DBQueryFunc] = None,
        config: Optional[VersionControlConfig] = None,
    ):
        """Initialize version control.

        Args:
            repository: Version repository for storage
            db_query: Function to execute database queries
            config: Configuration options
        """
        self.repository = repository or InMemoryVersionRepository()
        self.db_query = db_query
        self.config = config or VersionControlConfig(repository_path=".")

    # === Version Management ===

    async def commit(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        definition: str,
        author: str,
        message: Optional[str] = None,
        branch: Optional[str] = None,
    ) -> ObjectVersion:
        """Commit a new version of a database object.

        Args:
            object_name: Name of the object
            schema_name: Schema name
            object_type: Type of database object
            definition: SQL definition
            author: Author name/email
            message: Commit message
            branch: Target branch (default: main)

        Returns:
            Created version
        """
        # Get previous version
        previous = await self.repository.get_latest_version(
            object_name, schema_name, object_type, branch
        )

        # Calculate version number
        version_number = (previous.version_number + 1) if previous else 1

        # Calculate content hash
        content_hash = ObjectVersion.compute_hash(definition)

        # Check if content actually changed
        if previous and previous.content_hash == content_hash:
            return previous  # No changes, return existing version

        # Create new version
        version = ObjectVersion(
            id="",  # Will be set by repository
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            version_number=version_number,
            definition=definition,
            content_hash=content_hash,
            created_at=datetime.utcnow(),
            created_by=author,
            message=message,
            parent_version_id=previous.id if previous else None,
        )

        return await self.repository.save_version(version)

    async def history(
        self,
        object_name: str,
        schema_name: str = "dbo",
        object_type: Optional[ObjectType] = None,
        limit: int = 50,
    ) -> ObjectHistory:
        """Get version history for an object.

        Args:
            object_name: Name of the object
            schema_name: Schema name
            object_type: Type of object (auto-detected if not provided)
            limit: Maximum versions to return

        Returns:
            Object history with versions
        """
        if object_type is None:
            object_type = await self._detect_object_type(object_name, schema_name)

        return await self.repository.get_history(
            object_name, schema_name, object_type, limit
        )

    async def diff(
        self,
        object_name: str,
        schema_name: str = "dbo",
        from_version: Optional[str] = None,
        to_version: Optional[str] = None,
        object_type: Optional[ObjectType] = None,
    ) -> VersionDiff:
        """Get diff between versions.

        Args:
            object_name: Name of the object
            schema_name: Schema name
            from_version: Starting version (or "HEAD~1" syntax)
            to_version: Ending version (default: HEAD)
            object_type: Type of object

        Returns:
            Version diff
        """
        if object_type is None:
            object_type = await self._detect_object_type(object_name, schema_name)

        # Resolve version references
        from_id = await self._resolve_version_ref(
            object_name, schema_name, object_type, from_version
        )
        to_id = await self._resolve_version_ref(
            object_name, schema_name, object_type, to_version or "HEAD"
        )

        if not to_id:
            raise ValueError("Target version not found")

        return await self.repository.diff_versions(from_id, to_id)

    async def blame(
        self,
        object_name: str,
        schema_name: str = "dbo",
        object_type: Optional[ObjectType] = None,
        version: Optional[str] = None,
    ) -> BlameResult:
        """Get blame information showing who changed each line.

        Args:
            object_name: Name of the object
            schema_name: Schema name
            object_type: Type of object
            version: Specific version (default: HEAD)

        Returns:
            Blame result with line attributions
        """
        if object_type is None:
            object_type = await self._detect_object_type(object_name, schema_name)

        version_id = None
        if version:
            version_id = await self._resolve_version_ref(
                object_name, schema_name, object_type, version
            )

        return await self.repository.blame(
            object_name, schema_name, object_type, version_id
        )

    async def restore(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        version: str,
        author: str,
    ) -> ObjectVersion:
        """Restore an object to a previous version.

        Args:
            object_name: Name of the object
            schema_name: Schema name
            object_type: Type of object
            version: Version to restore to
            author: Author of the restore

        Returns:
            New version with restored content
        """
        # Get the version to restore
        version_id = await self._resolve_version_ref(
            object_name, schema_name, object_type, version
        )

        if not version_id:
            raise ValueError(f"Version {version} not found")

        target_version = await self.repository.get_version(version_id)
        if not target_version:
            raise ValueError(f"Version {version} not found")

        # Commit as new version
        return await self.commit(
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            definition=target_version.definition,
            author=author,
            message=f"Restored to version {target_version.version_number}",
        )

    # === Branch Management ===

    async def create_branch(
        self,
        name: str,
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Branch:
        """Create a new branch.

        Args:
            name: Branch name
            description: Optional description
            author: Author of the branch

        Returns:
            Created branch
        """
        branch = Branch(
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            created_by=author,
        )
        return await self.repository.create_branch(branch)

    async def list_branches(self) -> list[Branch]:
        """List all branches."""
        return await self.repository.list_branches()

    async def checkout(
        self,
        branch: str,
        create: bool = False,
        author: Optional[str] = None,
    ) -> Branch:
        """Switch to a branch.

        Args:
            branch: Branch name
            create: Create branch if it doesn't exist
            author: Author for new branch

        Returns:
            Checked out branch
        """
        existing = await self.repository.get_branch(branch)

        if existing:
            return existing
        elif create:
            return await self.create_branch(branch, author=author)
        else:
            raise ValueError(f"Branch {branch} not found")

    async def merge(
        self,
        source_branch: str,
        target_branch: str = "main",
        author: Optional[str] = None,
    ) -> MergeResult:
        """Merge one branch into another.

        Args:
            source_branch: Branch to merge from
            target_branch: Branch to merge into
            author: Author of the merge

        Returns:
            Merge result with any conflicts
        """
        source = await self.repository.get_branch(source_branch)
        target = await self.repository.get_branch(target_branch)

        if not source:
            raise ValueError(f"Source branch {source_branch} not found")
        if not target:
            raise ValueError(f"Target branch {target_branch} not found")

        merged_objects = []
        conflicts = []

        # Find objects that differ between branches
        all_objects = set(source.head_versions.keys()) | set(target.head_versions.keys())

        for full_name in all_objects:
            source_ver_id = source.head_versions.get(full_name)
            target_ver_id = target.head_versions.get(full_name)

            if source_ver_id == target_ver_id:
                continue  # Same version, no merge needed

            if source_ver_id and not target_ver_id:
                # Object only in source - fast forward
                target.head_versions[full_name] = source_ver_id
                merged_objects.append(full_name)

            elif target_ver_id and not source_ver_id:
                # Object only in target - keep as is
                continue

            else:
                # Both branches have different versions - check for conflict
                source_ver = await self.repository.get_version(source_ver_id)
                target_ver = await self.repository.get_version(target_ver_id)

                if source_ver and target_ver:
                    if source_ver.content_hash != target_ver.content_hash:
                        # Actual conflict
                        conflicts.append(MergeConflict(
                            object_name=source_ver.object_name,
                            schema_name=source_ver.schema_name,
                            object_type=source_ver.object_type,
                            source_version_id=source_ver_id,
                            target_version_id=target_ver_id,
                            base_version_id=None,
                            source_content=source_ver.definition,
                            target_content=target_ver.definition,
                            base_content=None,
                        ))
                    else:
                        # Same content, use source
                        target.head_versions[full_name] = source_ver_id
                        merged_objects.append(full_name)

        success = len(conflicts) == 0

        if success:
            # Save updated target branch
            # Note: In real implementation, would save to repository
            pass

        return MergeResult(
            source_branch=source_branch,
            target_branch=target_branch,
            merged_objects=merged_objects,
            conflicts=conflicts,
            success=success,
            message=f"Merged {len(merged_objects)} objects" if success else f"{len(conflicts)} conflicts",
        )

    # === Tag Management ===

    async def create_tag(
        self,
        name: str,
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> Tag:
        """Create a tag at the current state.

        Args:
            name: Tag name
            description: Optional description
            author: Author of the tag

        Returns:
            Created tag
        """
        tag = Tag(
            name=name,
            description=description,
            created_at=datetime.utcnow(),
            created_by=author,
        )
        return await self.repository.create_tag(tag)

    async def list_tags(self) -> list[Tag]:
        """List all tags."""
        return await self.repository.list_tags()

    # === Database Sync ===

    async def status(
        self,
        database_name: str,
        branch: Optional[str] = None,
    ) -> SyncStatus:
        """Get synchronization status between database and version control.

        Args:
            database_name: Database name
            branch: Branch to compare (default: main)

        Returns:
            Sync status
        """
        if not self.db_query:
            raise ValueError("Database query function not configured")

        branch_name = branch or "main"
        branch_obj = await self.repository.get_branch(branch_name)

        # Get current objects from database
        db_objects = await self._get_database_objects()

        modified = []
        untracked = []
        objects_in_sync = 0
        objects_ahead = 0
        objects_behind = 0

        for obj in db_objects:
            full_name = f"{obj['schema_name']}.{obj['object_name']}"
            obj_type = self._parse_object_type(obj["object_type"])

            # Get versioned copy
            latest = await self.repository.get_latest_version(
                obj["object_name"],
                obj["schema_name"],
                obj_type,
                branch_name,
            )

            if not latest:
                untracked.append(full_name)
                objects_behind += 1
            else:
                current_hash = ObjectVersion.compute_hash(obj["definition"])
                if current_hash == latest.content_hash:
                    objects_in_sync += 1
                else:
                    modified.append(full_name)
                    objects_behind += 1

        # Check for objects in VC but not in DB
        if branch_obj:
            for full_name in branch_obj.head_versions:
                schema, name = full_name.split(".", 1)
                if not any(
                    o["schema_name"] == schema and o["object_name"] == name
                    for o in db_objects
                ):
                    objects_ahead += 1

        return SyncStatus(
            database_name=database_name,
            branch=branch_name,
            last_sync=datetime.utcnow(),
            objects_in_sync=objects_in_sync,
            objects_ahead=objects_ahead,
            objects_behind=objects_behind,
            modified_objects=modified,
            untracked_objects=untracked,
        )

    async def pull(
        self,
        database_name: str,
        author: str,
        branch: Optional[str] = None,
    ) -> list[ObjectVersion]:
        """Pull changes from database into version control.

        Args:
            database_name: Database name
            author: Author of the pull
            branch: Target branch

        Returns:
            List of new versions created
        """
        if not self.db_query:
            raise ValueError("Database query function not configured")

        new_versions = []
        db_objects = await self._get_database_objects()

        for obj in db_objects:
            # Skip excluded schemas
            if obj["schema_name"] in self.config.excluded_schemas:
                continue

            obj_type = self._parse_object_type(obj["object_type"])

            version = await self.commit(
                object_name=obj["object_name"],
                schema_name=obj["schema_name"],
                object_type=obj_type,
                definition=obj["definition"],
                author=author,
                message=f"Pulled from {database_name}",
                branch=branch,
            )

            # Check if it's actually a new version
            history = await self.repository.get_history(
                obj["object_name"], obj["schema_name"], obj_type, limit=2
            )
            if len(history.versions) == 1 or (
                len(history.versions) > 1 and
                history.versions[0].id == version.id
            ):
                new_versions.append(version)

        return new_versions

    # === Helper Methods ===

    async def _detect_object_type(
        self,
        object_name: str,
        schema_name: str,
    ) -> ObjectType:
        """Auto-detect object type from database."""
        if not self.db_query:
            return ObjectType.STORED_PROCEDURE  # Default

        query = f"""
        SELECT type_desc
        FROM sys.objects
        WHERE name = '{object_name}'
        AND schema_id = SCHEMA_ID('{schema_name}')
        """

        results = await self.db_query(query)
        if results:
            return self._parse_object_type(results[0]["type_desc"])

        return ObjectType.STORED_PROCEDURE

    def _parse_object_type(self, type_desc: str) -> ObjectType:
        """Parse SQL Server type description to ObjectType."""
        type_map = {
            "USER_TABLE": ObjectType.TABLE,
            "VIEW": ObjectType.VIEW,
            "SQL_STORED_PROCEDURE": ObjectType.STORED_PROCEDURE,
            "SQL_SCALAR_FUNCTION": ObjectType.FUNCTION,
            "SQL_TABLE_VALUED_FUNCTION": ObjectType.FUNCTION,
            "SQL_INLINE_TABLE_VALUED_FUNCTION": ObjectType.FUNCTION,
            "SQL_TRIGGER": ObjectType.TRIGGER,
            "TYPE_TABLE": ObjectType.TYPE,
            "SYNONYM": ObjectType.SYNONYM,
            "SEQUENCE_OBJECT": ObjectType.SEQUENCE,
        }
        return type_map.get(type_desc, ObjectType.STORED_PROCEDURE)

    async def _resolve_version_ref(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        ref: str,
    ) -> Optional[str]:
        """Resolve a version reference (HEAD, HEAD~1, v1, etc) to version ID."""
        if not ref or ref.upper() == "HEAD":
            latest = await self.repository.get_latest_version(
                object_name, schema_name, object_type
            )
            return latest.id if latest else None

        # Handle HEAD~N syntax
        if ref.upper().startswith("HEAD~"):
            try:
                offset = int(ref[5:])
                history = await self.repository.get_history(
                    object_name, schema_name, object_type, limit=offset + 1
                )
                if len(history.versions) > offset:
                    return history.versions[offset].id
            except ValueError:
                pass

        # Handle v1, v2, etc. syntax
        if ref.lower().startswith("v"):
            try:
                version_num = int(ref[1:])
                history = await self.repository.get_history(
                    object_name, schema_name, object_type
                )
                for ver in history.versions:
                    if ver.version_number == version_num:
                        return ver.id
            except ValueError:
                pass

        # Assume it's a version ID
        return ref

    async def _get_database_objects(self) -> list[dict]:
        """Get all versionable objects from database."""
        if not self.db_query:
            return []

        query = """
        SELECT
            s.name AS schema_name,
            o.name AS object_name,
            o.type_desc AS object_type,
            m.definition
        FROM sys.objects o
        JOIN sys.schemas s ON o.schema_id = s.schema_id
        LEFT JOIN sys.sql_modules m ON o.object_id = m.object_id
        WHERE o.type IN ('P', 'V', 'FN', 'IF', 'TF', 'TR')
        AND o.is_ms_shipped = 0
        AND s.name NOT IN ('sys', 'INFORMATION_SCHEMA')
        ORDER BY s.name, o.name
        """

        return await self.db_query(query)
