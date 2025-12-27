"""Clerk authentication middleware for FastAPI."""

from typing import Optional
import httpx
import structlog
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel

from sql2ai_api.config import settings

logger = structlog.get_logger()

# HTTP Bearer security scheme
security = HTTPBearer(auto_error=False)


class ClerkUser(BaseModel):
    """Clerk user model from JWT claims."""

    id: str
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    org_id: Optional[str] = None
    org_role: Optional[str] = None
    org_slug: Optional[str] = None


class AuthMiddleware:
    """Clerk authentication middleware.

    Verifies JWT tokens from Clerk and extracts user information.
    Sets user and tenant context for RLS.
    """

    def __init__(
        self,
        clerk_secret_key: str,
        clerk_publishable_key: str,
        jwks_url: str = "https://clerk.sql2ai.com/.well-known/jwks.json",
    ):
        self.clerk_secret_key = clerk_secret_key
        self.clerk_publishable_key = clerk_publishable_key
        self.jwks_url = jwks_url
        self._jwks_cache: Optional[dict] = None
        self._jwks_cache_time: float = 0

    async def get_jwks(self) -> dict:
        """Fetch and cache JWKS from Clerk."""
        import time

        # Cache JWKS for 1 hour
        if self._jwks_cache and (time.time() - self._jwks_cache_time) < 3600:
            return self._jwks_cache

        async with httpx.AsyncClient() as client:
            response = await client.get(self.jwks_url)
            response.raise_for_status()
            self._jwks_cache = response.json()
            self._jwks_cache_time = time.time()
            return self._jwks_cache

    async def verify_token(self, token: str) -> ClerkUser:
        """Verify JWT token and extract user information."""
        try:
            # Get JWKS for verification
            jwks = await self.get_jwks()

            # Decode without verification to get the key ID
            unverified_header = jwt.get_unverified_header(token)
            key_id = unverified_header.get("kid")

            # Find the matching key
            key = None
            for k in jwks.get("keys", []):
                if k.get("kid") == key_id:
                    key = k
                    break

            if not key:
                raise HTTPException(status_code=401, detail="Invalid token key")

            # Verify and decode the token
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                options={"verify_aud": False},
            )

            # Extract user information
            user = ClerkUser(
                id=payload.get("sub", ""),
                email=payload.get("email"),
                first_name=payload.get("first_name"),
                last_name=payload.get("last_name"),
                org_id=payload.get("org_id"),
                org_role=payload.get("org_role"),
                org_slug=payload.get("org_slug"),
            )

            return user

        except ExpiredSignatureError:
            logger.warning("token_expired")
            raise HTTPException(status_code=401, detail="Token expired")
        except JWTError as e:
            logger.warning("token_invalid", error=str(e))
            raise HTTPException(status_code=401, detail="Invalid token")

    async def __call__(self, request: Request, call_next):
        """Process request through authentication middleware."""
        from fastapi.responses import JSONResponse

        # Skip auth for public routes
        public_routes = ["/", "/health", "/ready", "/api/docs", "/api/redoc", "/api/openapi.json"]
        if request.url.path in public_routes:
            return await call_next(request)

        # Skip auth for webhook routes (they have their own verification)
        if request.url.path.startswith("/api/webhooks"):
            return await call_next(request)

        # Skip auth for public billing endpoints
        if request.url.path in ["/api/billing/pricing"]:
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authorization header"}
            )

        token = auth_header.replace("Bearer ", "")

        # Verify token and get user
        try:
            user = await self.verify_token(token)
        except HTTPException as e:
            return JSONResponse(status_code=e.status_code, content={"detail": e.detail})

        # Attach user to request state
        request.state.user = user
        request.state.tenant_id = user.org_id or user.id  # Use org or personal

        # Log authentication
        logger.info(
            "request_authenticated",
            user_id=user.id,
            org_id=user.org_id,
            path=request.url.path,
        )

        # Continue with request
        response = await call_next(request)
        return response


def create_auth_middleware() -> AuthMiddleware:
    """Factory function to create auth middleware with settings."""
    return AuthMiddleware(
        clerk_secret_key=settings.clerk_secret_key,
        clerk_publishable_key=settings.clerk_publishable_key,
    )
