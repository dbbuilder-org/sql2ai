"""Clerk authentication integration for SQL2.AI."""

from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, SecretStr
import structlog

logger = structlog.get_logger()


class ClerkConfig(BaseModel):
    """Clerk configuration."""

    secret_key: SecretStr
    publishable_key: str
    api_url: str = "https://api.clerk.com/v1"
    jwt_verification_key: Optional[str] = None
    disabled: bool = False


class ClerkUser(BaseModel):
    """Clerk user data model."""

    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    public_metadata: Dict[str, Any] = {}
    private_metadata: Dict[str, Any] = {}


class ClerkOrganization(BaseModel):
    """Clerk organization data model."""

    id: str
    name: str
    slug: str
    image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    public_metadata: Dict[str, Any] = {}
    private_metadata: Dict[str, Any] = {}


class ClerkAuth:
    """Clerk authentication service."""

    def __init__(self, config: ClerkConfig):
        self.config = config
        self._client = None

        if not config.disabled:
            self._init_client()

    def _init_client(self):
        """Initialize HTTP client for Clerk API."""
        try:
            import httpx

            self._client = httpx.AsyncClient(
                base_url=self.config.api_url,
                headers={
                    "Authorization": f"Bearer {self.config.secret_key.get_secret_value()}",
                    "Content-Type": "application/json",
                },
            )
            logger.info("clerk_initialized")

        except ImportError:
            logger.warning("httpx_not_installed")
        except Exception as e:
            logger.error("clerk_init_failed", error=str(e))

    async def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a Clerk session token."""
        if not self._client:
            return None

        try:
            import jwt

            # Decode without verification to get claims
            unverified = jwt.decode(
                token,
                options={"verify_signature": False},
            )

            # For production, verify with Clerk's JWKS
            if self.config.jwt_verification_key:
                verified = jwt.decode(
                    token,
                    self.config.jwt_verification_key,
                    algorithms=["RS256"],
                    audience=self.config.publishable_key,
                )
                return verified

            # Verify session via API
            session_id = unverified.get("sid")
            if session_id:
                response = await self._client.get(f"/sessions/{session_id}/verify")
                if response.status_code == 200:
                    return response.json()

            return unverified

        except Exception as e:
            logger.warning("clerk_token_verification_failed", error=str(e))
            return None

    async def get_user(self, user_id: str) -> Optional[ClerkUser]:
        """Get user details by ID."""
        if not self._client:
            return None

        try:
            response = await self._client.get(f"/users/{user_id}")

            if response.status_code == 200:
                data = response.json()
                return ClerkUser(
                    id=data["id"],
                    email=data.get("email_addresses", [{}])[0].get("email_address")
                    if data.get("email_addresses")
                    else None,
                    first_name=data.get("first_name"),
                    last_name=data.get("last_name"),
                    username=data.get("username"),
                    image_url=data.get("image_url"),
                    created_at=datetime.fromtimestamp(data["created_at"] / 1000)
                    if data.get("created_at")
                    else None,
                    updated_at=datetime.fromtimestamp(data["updated_at"] / 1000)
                    if data.get("updated_at")
                    else None,
                    public_metadata=data.get("public_metadata", {}),
                    private_metadata=data.get("private_metadata", {}),
                )

            logger.warning(
                "clerk_user_not_found",
                user_id=user_id,
                status=response.status_code,
            )
            return None

        except Exception as e:
            logger.error("clerk_get_user_failed", user_id=user_id, error=str(e))
            return None

    async def update_user_metadata(
        self,
        user_id: str,
        public_metadata: Optional[Dict[str, Any]] = None,
        private_metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Update user metadata."""
        if not self._client:
            return False

        try:
            payload = {}
            if public_metadata is not None:
                payload["public_metadata"] = public_metadata
            if private_metadata is not None:
                payload["private_metadata"] = private_metadata

            response = await self._client.patch(
                f"/users/{user_id}",
                json=payload,
            )

            if response.status_code == 200:
                logger.info("clerk_user_metadata_updated", user_id=user_id)
                return True

            logger.warning(
                "clerk_user_update_failed",
                user_id=user_id,
                status=response.status_code,
            )
            return False

        except Exception as e:
            logger.error("clerk_update_user_failed", user_id=user_id, error=str(e))
            return False

    async def get_organization(self, org_id: str) -> Optional[ClerkOrganization]:
        """Get organization details by ID."""
        if not self._client:
            return None

        try:
            response = await self._client.get(f"/organizations/{org_id}")

            if response.status_code == 200:
                data = response.json()
                return ClerkOrganization(
                    id=data["id"],
                    name=data["name"],
                    slug=data["slug"],
                    image_url=data.get("image_url"),
                    created_at=datetime.fromtimestamp(data["created_at"] / 1000)
                    if data.get("created_at")
                    else None,
                    public_metadata=data.get("public_metadata", {}),
                    private_metadata=data.get("private_metadata", {}),
                )

            return None

        except Exception as e:
            logger.error("clerk_get_org_failed", org_id=org_id, error=str(e))
            return None

    async def get_organization_members(
        self,
        org_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all members of an organization."""
        if not self._client:
            return []

        try:
            response = await self._client.get(
                f"/organizations/{org_id}/memberships",
            )

            if response.status_code == 200:
                return response.json().get("data", [])

            return []

        except Exception as e:
            logger.error("clerk_get_members_failed", org_id=org_id, error=str(e))
            return []

    async def create_organization(
        self,
        name: str,
        slug: Optional[str] = None,
        created_by: Optional[str] = None,
        public_metadata: Optional[Dict[str, Any]] = None,
        private_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[ClerkOrganization]:
        """Create a new organization."""
        if not self._client:
            return None

        try:
            payload = {"name": name}
            if slug:
                payload["slug"] = slug
            if created_by:
                payload["created_by"] = created_by
            if public_metadata:
                payload["public_metadata"] = public_metadata
            if private_metadata:
                payload["private_metadata"] = private_metadata

            response = await self._client.post("/organizations", json=payload)

            if response.status_code == 200:
                data = response.json()
                logger.info("clerk_organization_created", org_id=data["id"])
                return ClerkOrganization(
                    id=data["id"],
                    name=data["name"],
                    slug=data["slug"],
                    image_url=data.get("image_url"),
                    public_metadata=data.get("public_metadata", {}),
                    private_metadata=data.get("private_metadata", {}),
                )

            logger.warning(
                "clerk_create_org_failed",
                name=name,
                status=response.status_code,
            )
            return None

        except Exception as e:
            logger.error("clerk_create_org_failed", name=name, error=str(e))
            return None

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (GDPR compliance)."""
        if not self._client:
            return False

        try:
            response = await self._client.delete(f"/users/{user_id}")

            if response.status_code == 200:
                logger.info("clerk_user_deleted", user_id=user_id)
                return True

            return False

        except Exception as e:
            logger.error("clerk_delete_user_failed", user_id=user_id, error=str(e))
            return False

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()


class ClerkWebhookHandler:
    """Handler for Clerk webhook events."""

    def __init__(self, webhook_secret: str):
        self.webhook_secret = webhook_secret
        self._handlers: Dict[str, callable] = {}

    def on(self, event_type: str):
        """Decorator to register a webhook handler."""
        def decorator(func):
            self._handlers[event_type] = func
            return func
        return decorator

    def verify_webhook(
        self,
        payload: bytes,
        headers: Dict[str, str],
    ) -> Optional[Dict[str, Any]]:
        """Verify and parse a Clerk webhook event."""
        try:
            from svix.webhooks import Webhook

            wh = Webhook(self.webhook_secret)
            event = wh.verify(payload, headers)
            return event

        except Exception as e:
            logger.warning("clerk_webhook_verification_failed", error=str(e))
            return None

    async def handle(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a webhook event."""
        event_type = event.get("type")
        handler = self._handlers.get(event_type)

        if handler:
            try:
                result = await handler(event.get("data", {}))
                logger.info(
                    "clerk_webhook_handled",
                    event_type=event_type,
                )
                return {"status": "handled", "result": result}
            except Exception as e:
                logger.error(
                    "clerk_webhook_handler_failed",
                    event_type=event_type,
                    error=str(e),
                )
                return {"status": "error", "error": str(e)}

        logger.debug("clerk_webhook_ignored", event_type=event_type)
        return {"status": "ignored"}


# Pre-configured webhook handler (secret set at runtime)
webhook_handler: Optional[ClerkWebhookHandler] = None


def init_webhook_handler(secret: str) -> ClerkWebhookHandler:
    """Initialize the webhook handler with a secret."""
    global webhook_handler
    webhook_handler = ClerkWebhookHandler(secret)
    return webhook_handler
