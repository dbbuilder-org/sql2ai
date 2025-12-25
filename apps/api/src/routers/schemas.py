"""Schema analysis endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_schemas() -> dict[str, list]:
    """List all analyzed schemas."""
    return {"schemas": []}


@router.post("/analyze")
async def analyze_schema(connection_id: str) -> dict[str, str]:
    """Analyze a database schema."""
    return {"status": "analysis_started", "connection_id": connection_id}


@router.get("/{schema_id}")
async def get_schema(schema_id: str) -> dict[str, str]:
    """Get schema details."""
    return {"schema_id": schema_id}


@router.post("/compare")
async def compare_schemas(source_id: str, target_id: str) -> dict[str, list]:
    """Compare two schemas."""
    return {"differences": [], "source_id": source_id, "target_id": target_id}
