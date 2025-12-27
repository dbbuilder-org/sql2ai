"""API Routers."""

# Core routers (always available)
from sql2ai_api.routers import (
    schemas, queries, migrations, telemetry, connections,
    dashboard, billing
)

__all__ = [
    "schemas", "queries", "migrations", "telemetry", "connections",
    "dashboard", "billing"
]

# Optional routers (depend on external libs that may not be in Docker)
_optional_routers = [
    "orchestrator", "migrator", "optimize", "compliance",
    "writer", "codereview", "version"
]

for _router_name in _optional_routers:
    try:
        _module = __import__(f"sql2ai_api.routers.{_router_name}", fromlist=[_router_name])
        globals()[_router_name] = _module
        __all__.append(_router_name)
    except ImportError as e:
        # Router not available - skip it
        pass
