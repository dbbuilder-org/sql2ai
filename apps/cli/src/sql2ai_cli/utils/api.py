"""API client for SQL2.AI CLI."""

from typing import Any, Optional

import httpx

from sql2ai_cli.utils.config import get_api_key, get_config


class ApiClient:
    """HTTP client for SQL2.AI API."""

    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        config = get_config()
        self.base_url = base_url or config.api_url
        self.api_key = api_key or get_api_key()
        self._client: Optional[httpx.Client] = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.Client(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    @property
    def is_authenticated(self) -> bool:
        """Check if API key is configured."""
        return bool(self.api_key)

    def health_check(self) -> bool:
        """Check API health."""
        try:
            response = self.client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    def get(self, path: str, **kwargs) -> dict:
        """Make GET request."""
        response = self.client.get(path, **kwargs)
        response.raise_for_status()
        return response.json()

    def post(self, path: str, data: Optional[dict] = None, **kwargs) -> dict:
        """Make POST request."""
        response = self.client.post(path, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    def put(self, path: str, data: Optional[dict] = None, **kwargs) -> dict:
        """Make PUT request."""
        response = self.client.put(path, json=data, **kwargs)
        response.raise_for_status()
        return response.json()

    def delete(self, path: str, **kwargs) -> dict:
        """Make DELETE request."""
        response = self.client.delete(path, **kwargs)
        response.raise_for_status()
        return response.json()

    # Convenience methods for specific endpoints

    def optimize_query(self, sql: str, db_type: str = "postgresql") -> dict:
        """Optimize a SQL query."""
        return self.post("/api/optimize/query", {"sql": sql, "db_type": db_type})

    def explain_query(self, sql: str, db_type: str = "postgresql") -> dict:
        """Explain a SQL query."""
        return self.post("/api/writer/explain", {"sql": sql, "db_type": db_type})

    def review_code(self, sql: str, db_type: str = "postgresql") -> dict:
        """Review SQL code."""
        return self.post("/api/codereview/analyze", {"sql": sql, "db_type": db_type})

    def generate_sql(
        self, prompt: str, db_type: str = "postgresql", context: Optional[str] = None
    ) -> dict:
        """Generate SQL from natural language."""
        return self.post(
            "/api/writer/generate",
            {"prompt": prompt, "db_type": db_type, "context": context},
        )

    def generate_crud(
        self, table_name: str, schema: str = "dbo", db_type: str = "postgresql"
    ) -> dict:
        """Generate CRUD procedures."""
        return self.post(
            "/api/writer/crud",
            {"table_name": table_name, "schema": schema, "db_type": db_type},
        )

    def list_connections(self) -> list[dict]:
        """List database connections."""
        return self.get("/api/connections")["connections"]

    def get_connection(self, connection_id: str) -> dict:
        """Get connection details."""
        return self.get(f"/api/connections/{connection_id}")

    def test_connection(self, connection_id: str) -> dict:
        """Test a connection."""
        return self.post(f"/api/connections/{connection_id}/test")

    def create_connection(self, data: dict) -> dict:
        """Create a new connection."""
        return self.post("/api/connections", data)

    def extract_schema(self, connection_id: str) -> dict:
        """Extract schema from a connection."""
        return self.post(f"/api/schemas/{connection_id}/extract")


_api_client: Optional[ApiClient] = None


def get_api_client() -> ApiClient:
    """Get singleton API client instance."""
    global _api_client
    if _api_client is None:
        _api_client = ApiClient()
    return _api_client
