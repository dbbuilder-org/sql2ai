"""API endpoints for SQL Version Control."""

import sys
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Add version library to path
sys.path.insert(0, "/Users/admin/dev2/sql2ai/libs/sql-version/src")

from sql2ai_api.dependencies.auth import (
    AuthenticatedUser,
    Permission,
    require_permissions,
)

router = APIRouter()


# Request/Response models

class CommitRequest(BaseModel):
    """Request to commit an object version."""

    object_name: str = Field(..., description="Object name")
    schema_name: str = Field("dbo", description="Schema name")
    object_type: str = Field(..., description="table, view, stored_procedure, function, trigger")
    definition: str = Field(..., description="SQL definition")
    message: Optional[str] = Field(None, description="Commit message")
    branch: Optional[str] = Field(None, description="Target branch")


class VersionResponse(BaseModel):
    """Response for a version."""

    id: str
    object_name: str
    schema_name: str
    object_type: str
    version_number: int
    content_hash: str
    created_at: str
    created_by: str
    message: Optional[str]


class HistoryResponse(BaseModel):
    """Response for version history."""

    object_name: str
    schema_name: str
    object_type: str
    version_count: int
    current_version_id: Optional[str]
    versions: list[VersionResponse]


class DiffResponse(BaseModel):
    """Response for version diff."""

    from_version_id: Optional[str]
    to_version_id: str
    object_name: str
    action: str
    additions: int
    deletions: int
    unified_diff: str


class BlameLineResponse(BaseModel):
    """Response for a blame line."""

    line_number: int
    content: str
    version_number: int
    author: str
    timestamp: str
    message: Optional[str]


class BlameResponse(BaseModel):
    """Response for blame."""

    object_name: str
    schema_name: str
    line_count: int
    authors: list[str]
    lines: list[BlameLineResponse]


class BranchResponse(BaseModel):
    """Response for a branch."""

    name: str
    description: Optional[str]
    created_at: str
    created_by: Optional[str]
    is_default: bool
    object_count: int


class TagResponse(BaseModel):
    """Response for a tag."""

    name: str
    description: Optional[str]
    created_at: str
    created_by: Optional[str]
    object_count: int


class MergeResponse(BaseModel):
    """Response for merge."""

    source_branch: str
    target_branch: str
    success: bool
    merged_count: int
    conflict_count: int
    message: Optional[str]
    conflicts: list[dict]


class SyncStatusResponse(BaseModel):
    """Response for sync status."""

    database_name: str
    branch: str
    objects_in_sync: int
    objects_ahead: int
    objects_behind: int
    modified_objects: list[str]
    untracked_objects: list[str]


# Endpoints

@router.post("/commit", response_model=VersionResponse)
async def commit_version(
    request: CommitRequest,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_WRITE])
    ),
):
    """Commit a new version of a database object.

    Creates a new version in version control with proper
    tracking and attribution.
    """
    from version_control import SQLVersionControl
    from models import ObjectType

    # Map string to ObjectType
    type_map = {
        "table": ObjectType.TABLE,
        "view": ObjectType.VIEW,
        "stored_procedure": ObjectType.STORED_PROCEDURE,
        "function": ObjectType.FUNCTION,
        "trigger": ObjectType.TRIGGER,
        "index": ObjectType.INDEX,
    }

    object_type = type_map.get(request.object_type.lower())
    if not object_type:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid object_type. Must be one of: {list(type_map.keys())}"
        )

    vc = SQLVersionControl()

    try:
        version = await vc.commit(
            object_name=request.object_name,
            schema_name=request.schema_name,
            object_type=object_type,
            definition=request.definition,
            author=user.email or user.user_id,
            message=request.message,
            branch=request.branch,
        )

        return VersionResponse(
            id=version.id,
            object_name=version.object_name,
            schema_name=version.schema_name,
            object_type=version.object_type.value,
            version_number=version.version_number,
            content_hash=version.content_hash,
            created_at=version.created_at.isoformat(),
            created_by=version.created_by,
            message=version.message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{schema_name}/{object_name}", response_model=HistoryResponse)
async def get_history(
    schema_name: str,
    object_name: str,
    object_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get version history for an object.

    Returns all versions of a database object with metadata.
    """
    from version_control import SQLVersionControl
    from models import ObjectType

    vc = SQLVersionControl()

    obj_type = None
    if object_type:
        type_map = {
            "table": ObjectType.TABLE,
            "view": ObjectType.VIEW,
            "stored_procedure": ObjectType.STORED_PROCEDURE,
            "function": ObjectType.FUNCTION,
            "trigger": ObjectType.TRIGGER,
        }
        obj_type = type_map.get(object_type.lower())

    try:
        history = await vc.history(
            object_name=object_name,
            schema_name=schema_name,
            object_type=obj_type,
            limit=limit,
        )

        return HistoryResponse(
            object_name=history.object_name,
            schema_name=history.schema_name,
            object_type=history.object_type.value if history.object_type else "unknown",
            version_count=history.version_count,
            current_version_id=history.current_version_id,
            versions=[
                VersionResponse(
                    id=v.id,
                    object_name=v.object_name,
                    schema_name=v.schema_name,
                    object_type=v.object_type.value,
                    version_number=v.version_number,
                    content_hash=v.content_hash,
                    created_at=v.created_at.isoformat(),
                    created_by=v.created_by,
                    message=v.message,
                )
                for v in history.versions
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diff/{schema_name}/{object_name}", response_model=DiffResponse)
async def get_diff(
    schema_name: str,
    object_name: str,
    from_version: Optional[str] = None,
    to_version: Optional[str] = None,
    object_type: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get diff between versions.

    Shows what changed between two versions of an object.
    """
    from version_control import SQLVersionControl
    from models import ObjectType

    vc = SQLVersionControl()

    obj_type = None
    if object_type:
        type_map = {
            "stored_procedure": ObjectType.STORED_PROCEDURE,
            "view": ObjectType.VIEW,
            "function": ObjectType.FUNCTION,
            "trigger": ObjectType.TRIGGER,
        }
        obj_type = type_map.get(object_type.lower())

    try:
        diff = await vc.diff(
            object_name=object_name,
            schema_name=schema_name,
            from_version=from_version,
            to_version=to_version,
            object_type=obj_type,
        )

        return DiffResponse(
            from_version_id=diff.from_version_id,
            to_version_id=diff.to_version_id,
            object_name=diff.object_name,
            action=diff.action.value,
            additions=diff.additions,
            deletions=diff.deletions,
            unified_diff=diff.to_unified_diff(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blame/{schema_name}/{object_name}", response_model=BlameResponse)
async def get_blame(
    schema_name: str,
    object_name: str,
    version: Optional[str] = None,
    object_type: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get blame for an object.

    Shows who changed each line and when.
    """
    from version_control import SQLVersionControl
    from models import ObjectType

    vc = SQLVersionControl()

    obj_type = None
    if object_type:
        type_map = {
            "stored_procedure": ObjectType.STORED_PROCEDURE,
            "view": ObjectType.VIEW,
            "function": ObjectType.FUNCTION,
        }
        obj_type = type_map.get(object_type.lower())

    try:
        blame = await vc.blame(
            object_name=object_name,
            schema_name=schema_name,
            object_type=obj_type,
            version=version,
        )

        return BlameResponse(
            object_name=blame.object_name,
            schema_name=blame.schema_name,
            line_count=len(blame.lines),
            authors=blame.get_authors(),
            lines=[
                BlameLineResponse(
                    line_number=line.line_number,
                    content=line.content,
                    version_number=line.version_number,
                    author=line.author,
                    timestamp=line.timestamp.isoformat(),
                    message=line.commit_message,
                )
                for line in blame.lines
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/restore")
async def restore_version(
    schema_name: str,
    object_name: str,
    version: str,
    object_type: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_EXECUTE])
    ),
):
    """Restore an object to a previous version.

    Creates a new version with the content of a previous version.
    """
    from version_control import SQLVersionControl
    from models import ObjectType

    type_map = {
        "stored_procedure": ObjectType.STORED_PROCEDURE,
        "view": ObjectType.VIEW,
        "function": ObjectType.FUNCTION,
        "trigger": ObjectType.TRIGGER,
    }

    obj_type = type_map.get(object_type.lower())
    if not obj_type:
        raise HTTPException(status_code=400, detail="Invalid object_type")

    vc = SQLVersionControl()

    try:
        new_version = await vc.restore(
            object_name=object_name,
            schema_name=schema_name,
            object_type=obj_type,
            version=version,
            author=user.email or user.user_id,
        )

        return VersionResponse(
            id=new_version.id,
            object_name=new_version.object_name,
            schema_name=new_version.schema_name,
            object_type=new_version.object_type.value,
            version_number=new_version.version_number,
            content_hash=new_version.content_hash,
            created_at=new_version.created_at.isoformat(),
            created_by=new_version.created_by,
            message=new_version.message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Branch endpoints

@router.get("/branches", response_model=list[BranchResponse])
async def list_branches(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """List all branches."""
    from version_control import SQLVersionControl

    vc = SQLVersionControl()
    branches = await vc.list_branches()

    return [
        BranchResponse(
            name=b.name,
            description=b.description,
            created_at=b.created_at.isoformat(),
            created_by=b.created_by,
            is_default=b.is_default,
            object_count=len(b.head_versions),
        )
        for b in branches
    ]


@router.post("/branches")
async def create_branch(
    name: str,
    description: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_WRITE])
    ),
):
    """Create a new branch."""
    from version_control import SQLVersionControl

    vc = SQLVersionControl()

    try:
        branch = await vc.create_branch(
            name=name,
            description=description,
            author=user.email or user.user_id,
        )

        return BranchResponse(
            name=branch.name,
            description=branch.description,
            created_at=branch.created_at.isoformat(),
            created_by=branch.created_by,
            is_default=branch.is_default,
            object_count=len(branch.head_versions),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/branches/{source}/merge/{target}", response_model=MergeResponse)
async def merge_branches(
    source: str,
    target: str,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_EXECUTE])
    ),
):
    """Merge one branch into another."""
    from version_control import SQLVersionControl

    vc = SQLVersionControl()

    try:
        result = await vc.merge(
            source_branch=source,
            target_branch=target,
            author=user.email or user.user_id,
        )

        return MergeResponse(
            source_branch=result.source_branch,
            target_branch=result.target_branch,
            success=result.success,
            merged_count=len(result.merged_objects),
            conflict_count=len(result.conflicts),
            message=result.message,
            conflicts=[
                {
                    "object_name": c.object_name,
                    "schema_name": c.schema_name,
                    "object_type": c.object_type.value,
                }
                for c in result.conflicts
            ],
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Tag endpoints

@router.get("/tags", response_model=list[TagResponse])
async def list_tags(
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """List all tags."""
    from version_control import SQLVersionControl

    vc = SQLVersionControl()
    tags = await vc.list_tags()

    return [
        TagResponse(
            name=t.name,
            description=t.description,
            created_at=t.created_at.isoformat(),
            created_by=t.created_by,
            object_count=len(t.version_snapshot),
        )
        for t in tags
    ]


@router.post("/tags")
async def create_tag(
    name: str,
    description: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_WRITE])
    ),
):
    """Create a new tag at current state."""
    from version_control import SQLVersionControl

    vc = SQLVersionControl()

    try:
        tag = await vc.create_tag(
            name=name,
            description=description,
            author=user.email or user.user_id,
        )

        return TagResponse(
            name=tag.name,
            description=tag.description,
            created_at=tag.created_at.isoformat(),
            created_by=tag.created_by,
            object_count=len(tag.version_snapshot),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Sync endpoints

@router.get("/connections/{connection_id}/status", response_model=SyncStatusResponse)
async def get_sync_status(
    connection_id: str,
    branch: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.SCHEMA_READ])
    ),
):
    """Get sync status between database and version control.

    Shows objects that are ahead, behind, or modified.
    """
    # In production, would connect to actual database
    return SyncStatusResponse(
        database_name=f"database_{connection_id}",
        branch=branch or "main",
        objects_in_sync=0,
        objects_ahead=0,
        objects_behind=0,
        modified_objects=[],
        untracked_objects=[],
    )


@router.post("/connections/{connection_id}/pull")
async def pull_from_database(
    connection_id: str,
    branch: Optional[str] = None,
    user: AuthenticatedUser = Depends(
        require_permissions([Permission.MIGRATION_WRITE])
    ),
):
    """Pull changes from database into version control.

    Imports current state of database objects as new versions.
    """
    # In production, would connect and pull from database
    return {
        "connection_id": connection_id,
        "branch": branch or "main",
        "message": "Pull requires live database connection",
        "new_versions": [],
    }
