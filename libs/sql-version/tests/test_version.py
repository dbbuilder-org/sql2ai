"""Tests for SQL Version module."""

import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(__file__).replace('/tests/test_version.py', '/src'))

from models import (
    ObjectVersion,
    ObjectType,
    VersionDiff,
    DiffLine,
    DiffOperation,
    Branch,
    Tag,
    BlameLine,
    MergeConflict,
)
from repository import InMemoryRepository, FileSystemRepository
from version_control import SQLVersionControl


class TestObjectVersion:
    """Test ObjectVersion model."""

    def test_create_version(self):
        version = ObjectVersion(
            version_id="v_001",
            object_name="dbo.GetCustomers",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.GetCustomers AS SELECT * FROM Customers",
            author="developer@example.com",
            message="Initial version",
        )
        assert version.version_id == "v_001"
        assert version.object_type == ObjectType.STORED_PROCEDURE

    def test_version_hash(self):
        version = ObjectVersion(
            version_id="v_001",
            object_name="dbo.GetCustomers",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.GetCustomers AS SELECT * FROM Customers",
            author="developer@example.com",
        )
        assert version.content_hash is not None
        assert len(version.content_hash) > 0


class TestBranch:
    """Test Branch model."""

    def test_create_branch(self):
        branch = Branch(
            name="feature/add-customer-search",
            base_branch="main",
            created_at=datetime.utcnow(),
            created_by="developer@example.com",
        )
        assert branch.name == "feature/add-customer-search"
        assert branch.base_branch == "main"


class TestTag:
    """Test Tag model."""

    def test_create_tag(self):
        tag = Tag(
            name="v1.0.0",
            version_id="v_123",
            message="Release 1.0.0",
            created_by="developer@example.com",
        )
        assert tag.name == "v1.0.0"


class TestVersionDiff:
    """Test VersionDiff model."""

    def test_create_diff(self):
        diff = VersionDiff(
            old_version_id="v_001",
            new_version_id="v_002",
            object_name="dbo.GetCustomers",
            lines=[
                DiffLine(line_number=1, operation=DiffOperation.UNCHANGED, content="CREATE PROCEDURE dbo.GetCustomers"),
                DiffLine(line_number=2, operation=DiffOperation.DELETE, content="AS SELECT * FROM Customers"),
                DiffLine(line_number=3, operation=DiffOperation.ADD, content="AS SELECT * FROM Customers WHERE IsActive = 1"),
            ],
        )
        assert len(diff.lines) == 3
        assert diff.has_changes is True


class TestInMemoryRepository:
    """Test InMemoryRepository."""

    def test_save_and_get_version(self):
        repo = InMemoryRepository()
        version = ObjectVersion(
            version_id="v_001",
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 1",
            author="test@example.com",
        )

        repo.save(version)
        retrieved = repo.get("v_001")
        assert retrieved is not None
        assert retrieved.object_name == "dbo.TestProc"

    def test_get_history(self):
        repo = InMemoryRepository()

        for i in range(3):
            version = ObjectVersion(
                version_id=f"v_00{i+1}",
                object_name="dbo.TestProc",
                object_type=ObjectType.STORED_PROCEDURE,
                content=f"CREATE PROCEDURE dbo.TestProc AS SELECT {i+1}",
                author="test@example.com",
            )
            repo.save(version)

        history = repo.get_history("dbo.TestProc")
        assert len(history) == 3

    def test_get_latest(self):
        repo = InMemoryRepository()

        for i in range(3):
            version = ObjectVersion(
                version_id=f"v_00{i+1}",
                object_name="dbo.TestProc",
                object_type=ObjectType.STORED_PROCEDURE,
                content=f"CREATE PROCEDURE dbo.TestProc AS SELECT {i+1}",
                author="test@example.com",
            )
            repo.save(version)

        latest = repo.get_latest("dbo.TestProc")
        assert latest is not None
        assert latest.version_id == "v_003"


class TestSQLVersionControl:
    """Test SQLVersionControl."""

    def test_commit(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        version = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 1",
            author="test@example.com",
            message="Initial commit",
        )

        assert version is not None
        assert version.message == "Initial commit"

    def test_diff(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        v1 = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc\nAS\nSELECT 1",
            author="test@example.com",
            message="v1",
        )

        v2 = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc\nAS\nSELECT 2",
            author="test@example.com",
            message="v2",
        )

        diff = vc.diff(v1.version_id, v2.version_id)
        assert diff is not None
        assert diff.has_changes is True

    def test_history(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        for i in range(5):
            vc.commit(
                object_name="dbo.TestProc",
                object_type=ObjectType.STORED_PROCEDURE,
                content=f"CREATE PROCEDURE dbo.TestProc AS SELECT {i+1}",
                author="test@example.com",
                message=f"Commit {i+1}",
            )

        history = vc.history("dbo.TestProc")
        assert len(history) == 5

    def test_blame(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc\nAS\nSELECT 1",
            author="dev1@example.com",
            message="Initial",
        )

        vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc\nAS\nSELECT 2",
            author="dev2@example.com",
            message="Updated select",
        )

        blame = vc.blame("dbo.TestProc")
        assert blame is not None
        assert len(blame) > 0
        assert any(line.author == "dev2@example.com" for line in blame)

    def test_create_branch(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 1",
            author="test@example.com",
            message="Initial",
        )

        branch = vc.create_branch(
            name="feature/test",
            base_branch="main",
            created_by="test@example.com",
        )

        assert branch is not None
        assert branch.name == "feature/test"

    def test_create_tag(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        version = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 1",
            author="test@example.com",
            message="Initial",
        )

        tag = vc.create_tag(
            name="v1.0.0",
            version_id=version.version_id,
            message="Release 1.0.0",
            created_by="test@example.com",
        )

        assert tag is not None
        assert tag.name == "v1.0.0"

    def test_restore(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        v1 = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 1",
            author="test@example.com",
            message="v1",
        )

        vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc AS SELECT 2",
            author="test@example.com",
            message="v2",
        )

        restored = vc.restore(v1.version_id, author="test@example.com")
        assert restored is not None
        assert "SELECT 1" in restored.content


class TestMergeConflict:
    """Test merge conflict detection."""

    def test_detect_conflict(self):
        vc = SQLVersionControl(repository=InMemoryRepository())

        # Create base version
        base = vc.commit(
            object_name="dbo.TestProc",
            object_type=ObjectType.STORED_PROCEDURE,
            content="CREATE PROCEDURE dbo.TestProc\nAS\nSELECT 1",
            author="test@example.com",
            message="base",
        )

        # Simulate conflicting changes
        conflict = MergeConflict(
            object_name="dbo.TestProc",
            base_version_id=base.version_id,
            source_version_id="v_source",
            target_version_id="v_target",
            conflict_lines=[(3, "SELECT 2", "SELECT 3")],
        )

        assert conflict.has_conflicts is True
        assert len(conflict.conflict_lines) == 1
