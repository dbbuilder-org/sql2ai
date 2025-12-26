"""Version repository for storing and managing object versions."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass, field
import json
import os
from ulid import ULID

from models import (
    ObjectType,
    ObjectVersion,
    ObjectHistory,
    VersionDiff,
    BlameLine,
    BlameResult,
    Branch,
    Tag,
    ChangeAction,
)


class VersionRepository(ABC):
    """Abstract base class for version repositories."""

    @abstractmethod
    async def save_version(self, version: ObjectVersion) -> ObjectVersion:
        """Save a new version."""
        pass

    @abstractmethod
    async def get_version(self, version_id: str) -> Optional[ObjectVersion]:
        """Get a version by ID."""
        pass

    @abstractmethod
    async def get_history(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        limit: int = 100,
    ) -> ObjectHistory:
        """Get version history for an object."""
        pass

    @abstractmethod
    async def get_latest_version(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        branch: Optional[str] = None,
    ) -> Optional[ObjectVersion]:
        """Get the latest version of an object."""
        pass

    @abstractmethod
    async def diff_versions(
        self,
        from_version_id: Optional[str],
        to_version_id: str,
    ) -> VersionDiff:
        """Get diff between two versions."""
        pass

    @abstractmethod
    async def blame(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        version_id: Optional[str] = None,
    ) -> BlameResult:
        """Get blame information for an object."""
        pass

    @abstractmethod
    async def create_branch(self, branch: Branch) -> Branch:
        """Create a new branch."""
        pass

    @abstractmethod
    async def get_branch(self, name: str) -> Optional[Branch]:
        """Get a branch by name."""
        pass

    @abstractmethod
    async def list_branches(self) -> list[Branch]:
        """List all branches."""
        pass

    @abstractmethod
    async def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag."""
        pass

    @abstractmethod
    async def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        pass

    @abstractmethod
    async def list_tags(self) -> list[Tag]:
        """List all tags."""
        pass


class InMemoryVersionRepository(VersionRepository):
    """In-memory implementation for testing."""

    def __init__(self):
        self.versions: dict[str, ObjectVersion] = {}
        self.branches: dict[str, Branch] = {}
        self.tags: dict[str, Tag] = {}

        # Create default branch
        self.branches["main"] = Branch(
            name="main",
            is_default=True,
            created_at=datetime.utcnow(),
        )

    async def save_version(self, version: ObjectVersion) -> ObjectVersion:
        """Save a new version."""
        if not version.id:
            version.id = str(ULID())
        self.versions[version.id] = version

        # Update branch head
        full_name = version.full_name
        if "main" in self.branches:
            self.branches["main"].head_versions[full_name] = version.id

        return version

    async def get_version(self, version_id: str) -> Optional[ObjectVersion]:
        """Get a version by ID."""
        return self.versions.get(version_id)

    async def get_history(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        limit: int = 100,
    ) -> ObjectHistory:
        """Get version history for an object."""
        full_name = f"{schema_name}.{object_name}"

        # Find all versions for this object
        versions = [
            v for v in self.versions.values()
            if v.object_name == object_name
            and v.schema_name == schema_name
            and v.object_type == object_type
        ]

        # Sort by version number descending
        versions.sort(key=lambda v: v.version_number, reverse=True)
        versions = versions[:limit]

        # Get current version ID
        current_id = None
        if "main" in self.branches:
            current_id = self.branches["main"].head_versions.get(full_name)

        return ObjectHistory(
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            versions=versions,
            current_version_id=current_id,
        )

    async def get_latest_version(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        branch: Optional[str] = None,
    ) -> Optional[ObjectVersion]:
        """Get the latest version of an object."""
        branch_name = branch or "main"
        branch_obj = self.branches.get(branch_name)

        if not branch_obj:
            return None

        full_name = f"{schema_name}.{object_name}"
        version_id = branch_obj.head_versions.get(full_name)

        if version_id:
            return self.versions.get(version_id)

        return None

    async def diff_versions(
        self,
        from_version_id: Optional[str],
        to_version_id: str,
    ) -> VersionDiff:
        """Get diff between two versions."""
        to_version = await self.get_version(to_version_id)
        if not to_version:
            raise ValueError(f"Version {to_version_id} not found")

        from_version = None
        if from_version_id:
            from_version = await self.get_version(from_version_id)

        # Determine action
        if not from_version:
            action = ChangeAction.CREATE
        elif not to_version.definition:
            action = ChangeAction.DROP
        else:
            action = ChangeAction.ALTER

        # Simple line-by-line diff
        from_lines = (from_version.definition.split("\n") if from_version else [])
        to_lines = to_version.definition.split("\n")

        from_set = set(from_lines)
        to_set = set(to_lines)

        added = [line for line in to_lines if line not in from_set]
        removed = [line for line in from_lines if line not in to_set]

        return VersionDiff(
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            object_name=to_version.object_name,
            schema_name=to_version.schema_name,
            object_type=to_version.object_type,
            action=action,
            added_lines=added,
            removed_lines=removed,
        )

    async def blame(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        version_id: Optional[str] = None,
    ) -> BlameResult:
        """Get blame information for an object."""
        # Get target version
        if version_id:
            target = await self.get_version(version_id)
        else:
            target = await self.get_latest_version(object_name, schema_name, object_type)

        if not target:
            return BlameResult(
                object_name=object_name,
                schema_name=schema_name,
                object_type=object_type,
            )

        # Get history
        history = await self.get_history(object_name, schema_name, object_type)

        # Simple blame: attribute each line to the version that last changed it
        current_lines = target.definition.split("\n")
        blame_lines = []

        for i, line in enumerate(current_lines, 1):
            # Find which version introduced this line
            introducing_version = target
            for version in history.versions:
                if version.version_number <= target.version_number:
                    if line in version.definition:
                        introducing_version = version
                        break

            blame_lines.append(BlameLine(
                line_number=i,
                content=line,
                version_id=introducing_version.id,
                version_number=introducing_version.version_number,
                author=introducing_version.created_by,
                timestamp=introducing_version.created_at,
                commit_message=introducing_version.message,
            ))

        return BlameResult(
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            lines=blame_lines,
        )

    async def create_branch(self, branch: Branch) -> Branch:
        """Create a new branch."""
        if branch.name in self.branches:
            raise ValueError(f"Branch {branch.name} already exists")

        # Copy head versions from default branch
        if "main" in self.branches:
            branch.head_versions = dict(self.branches["main"].head_versions)

        self.branches[branch.name] = branch
        return branch

    async def get_branch(self, name: str) -> Optional[Branch]:
        """Get a branch by name."""
        return self.branches.get(name)

    async def list_branches(self) -> list[Branch]:
        """List all branches."""
        return list(self.branches.values())

    async def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag."""
        if tag.name in self.tags:
            raise ValueError(f"Tag {tag.name} already exists")

        # Snapshot current versions
        if "main" in self.branches:
            tag.version_snapshot = dict(self.branches["main"].head_versions)

        self.tags[tag.name] = tag
        return tag

    async def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        return self.tags.get(name)

    async def list_tags(self) -> list[Tag]:
        """List all tags."""
        return list(self.tags.values())


class FileSystemVersionRepository(VersionRepository):
    """File-system based repository using JSON files."""

    def __init__(self, base_path: str):
        """Initialize with base path for storage."""
        self.base_path = base_path
        self.versions_path = os.path.join(base_path, "versions")
        self.branches_path = os.path.join(base_path, "branches")
        self.tags_path = os.path.join(base_path, "tags")

        # Create directories
        os.makedirs(self.versions_path, exist_ok=True)
        os.makedirs(self.branches_path, exist_ok=True)
        os.makedirs(self.tags_path, exist_ok=True)

        # Initialize default branch
        self._init_default_branch()

    def _init_default_branch(self):
        """Initialize default branch if not exists."""
        main_path = os.path.join(self.branches_path, "main.json")
        if not os.path.exists(main_path):
            branch = Branch(
                name="main",
                is_default=True,
                created_at=datetime.utcnow(),
            )
            self._save_branch_sync(branch)

    def _save_branch_sync(self, branch: Branch):
        """Synchronously save branch."""
        path = os.path.join(self.branches_path, f"{branch.name}.json")
        data = {
            "name": branch.name,
            "description": branch.description,
            "created_at": branch.created_at.isoformat(),
            "created_by": branch.created_by,
            "is_default": branch.is_default,
            "head_versions": branch.head_versions,
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _version_to_dict(self, version: ObjectVersion) -> dict:
        """Convert version to dictionary."""
        return {
            "id": version.id,
            "object_name": version.object_name,
            "schema_name": version.schema_name,
            "object_type": version.object_type.value,
            "version_number": version.version_number,
            "definition": version.definition,
            "content_hash": version.content_hash,
            "created_at": version.created_at.isoformat(),
            "created_by": version.created_by,
            "message": version.message,
            "parent_version_id": version.parent_version_id,
            "tags": version.tags,
            "metadata": version.metadata,
        }

    def _dict_to_version(self, data: dict) -> ObjectVersion:
        """Convert dictionary to version."""
        return ObjectVersion(
            id=data["id"],
            object_name=data["object_name"],
            schema_name=data["schema_name"],
            object_type=ObjectType(data["object_type"]),
            version_number=data["version_number"],
            definition=data["definition"],
            content_hash=data["content_hash"],
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data["created_by"],
            message=data.get("message"),
            parent_version_id=data.get("parent_version_id"),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    async def save_version(self, version: ObjectVersion) -> ObjectVersion:
        """Save a new version."""
        if not version.id:
            version.id = str(ULID())

        # Save version file
        object_dir = os.path.join(
            self.versions_path,
            version.schema_name,
            version.object_type.value,
        )
        os.makedirs(object_dir, exist_ok=True)

        version_file = os.path.join(object_dir, f"{version.object_name}_{version.id}.json")
        with open(version_file, "w") as f:
            json.dump(self._version_to_dict(version), f, indent=2)

        # Update branch head
        main_branch = await self.get_branch("main")
        if main_branch:
            main_branch.head_versions[version.full_name] = version.id
            self._save_branch_sync(main_branch)

        return version

    async def get_version(self, version_id: str) -> Optional[ObjectVersion]:
        """Get a version by ID."""
        # Search through all version files
        for root, dirs, files in os.walk(self.versions_path):
            for file in files:
                if version_id in file and file.endswith(".json"):
                    path = os.path.join(root, file)
                    with open(path) as f:
                        data = json.load(f)
                    return self._dict_to_version(data)
        return None

    async def get_history(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        limit: int = 100,
    ) -> ObjectHistory:
        """Get version history for an object."""
        object_dir = os.path.join(
            self.versions_path,
            schema_name,
            object_type.value,
        )

        versions = []
        if os.path.exists(object_dir):
            for file in os.listdir(object_dir):
                if file.startswith(object_name) and file.endswith(".json"):
                    path = os.path.join(object_dir, file)
                    with open(path) as f:
                        data = json.load(f)
                    versions.append(self._dict_to_version(data))

        # Sort by version number descending
        versions.sort(key=lambda v: v.version_number, reverse=True)
        versions = versions[:limit]

        # Get current version
        main_branch = await self.get_branch("main")
        current_id = None
        if main_branch:
            full_name = f"{schema_name}.{object_name}"
            current_id = main_branch.head_versions.get(full_name)

        return ObjectHistory(
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            versions=versions,
            current_version_id=current_id,
        )

    async def get_latest_version(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        branch: Optional[str] = None,
    ) -> Optional[ObjectVersion]:
        """Get the latest version of an object."""
        branch_name = branch or "main"
        branch_obj = await self.get_branch(branch_name)

        if not branch_obj:
            return None

        full_name = f"{schema_name}.{object_name}"
        version_id = branch_obj.head_versions.get(full_name)

        if version_id:
            return await self.get_version(version_id)

        return None

    async def diff_versions(
        self,
        from_version_id: Optional[str],
        to_version_id: str,
    ) -> VersionDiff:
        """Get diff between two versions."""
        to_version = await self.get_version(to_version_id)
        if not to_version:
            raise ValueError(f"Version {to_version_id} not found")

        from_version = None
        if from_version_id:
            from_version = await self.get_version(from_version_id)

        # Determine action
        if not from_version:
            action = ChangeAction.CREATE
        elif not to_version.definition:
            action = ChangeAction.DROP
        else:
            action = ChangeAction.ALTER

        # Simple line-by-line diff
        from_lines = (from_version.definition.split("\n") if from_version else [])
        to_lines = to_version.definition.split("\n")

        from_set = set(from_lines)
        to_set = set(to_lines)

        added = [line for line in to_lines if line not in from_set]
        removed = [line for line in from_lines if line not in to_set]

        return VersionDiff(
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            object_name=to_version.object_name,
            schema_name=to_version.schema_name,
            object_type=to_version.object_type,
            action=action,
            added_lines=added,
            removed_lines=removed,
        )

    async def blame(
        self,
        object_name: str,
        schema_name: str,
        object_type: ObjectType,
        version_id: Optional[str] = None,
    ) -> BlameResult:
        """Get blame information for an object."""
        if version_id:
            target = await self.get_version(version_id)
        else:
            target = await self.get_latest_version(object_name, schema_name, object_type)

        if not target:
            return BlameResult(
                object_name=object_name,
                schema_name=schema_name,
                object_type=object_type,
            )

        history = await self.get_history(object_name, schema_name, object_type)

        current_lines = target.definition.split("\n")
        blame_lines = []

        for i, line in enumerate(current_lines, 1):
            introducing_version = target
            for version in history.versions:
                if version.version_number <= target.version_number:
                    if line in version.definition:
                        introducing_version = version
                        break

            blame_lines.append(BlameLine(
                line_number=i,
                content=line,
                version_id=introducing_version.id,
                version_number=introducing_version.version_number,
                author=introducing_version.created_by,
                timestamp=introducing_version.created_at,
                commit_message=introducing_version.message,
            ))

        return BlameResult(
            object_name=object_name,
            schema_name=schema_name,
            object_type=object_type,
            lines=blame_lines,
        )

    async def create_branch(self, branch: Branch) -> Branch:
        """Create a new branch."""
        path = os.path.join(self.branches_path, f"{branch.name}.json")
        if os.path.exists(path):
            raise ValueError(f"Branch {branch.name} already exists")

        # Copy head versions from main
        main_branch = await self.get_branch("main")
        if main_branch:
            branch.head_versions = dict(main_branch.head_versions)

        self._save_branch_sync(branch)
        return branch

    async def get_branch(self, name: str) -> Optional[Branch]:
        """Get a branch by name."""
        path = os.path.join(self.branches_path, f"{name}.json")
        if not os.path.exists(path):
            return None

        with open(path) as f:
            data = json.load(f)

        return Branch(
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by"),
            is_default=data.get("is_default", False),
            head_versions=data.get("head_versions", {}),
        )

    async def list_branches(self) -> list[Branch]:
        """List all branches."""
        branches = []
        for file in os.listdir(self.branches_path):
            if file.endswith(".json"):
                name = file[:-5]
                branch = await self.get_branch(name)
                if branch:
                    branches.append(branch)
        return branches

    async def create_tag(self, tag: Tag) -> Tag:
        """Create a new tag."""
        path = os.path.join(self.tags_path, f"{tag.name}.json")
        if os.path.exists(path):
            raise ValueError(f"Tag {tag.name} already exists")

        # Snapshot current versions
        main_branch = await self.get_branch("main")
        if main_branch:
            tag.version_snapshot = dict(main_branch.head_versions)

        data = {
            "name": tag.name,
            "description": tag.description,
            "created_at": tag.created_at.isoformat(),
            "created_by": tag.created_by,
            "version_snapshot": tag.version_snapshot,
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return tag

    async def get_tag(self, name: str) -> Optional[Tag]:
        """Get a tag by name."""
        path = os.path.join(self.tags_path, f"{name}.json")
        if not os.path.exists(path):
            return None

        with open(path) as f:
            data = json.load(f)

        return Tag(
            name=data["name"],
            description=data.get("description"),
            created_at=datetime.fromisoformat(data["created_at"]),
            created_by=data.get("created_by"),
            version_snapshot=data.get("version_snapshot", {}),
        )

    async def list_tags(self) -> list[Tag]:
        """List all tags."""
        tags = []
        for file in os.listdir(self.tags_path):
            if file.endswith(".json"):
                name = file[:-5]
                tag = await self.get_tag(name)
                if tag:
                    tags.append(tag)
        return tags
