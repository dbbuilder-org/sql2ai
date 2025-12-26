"""JWT authentication service."""

from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from ulid import ULID
import structlog

from sql2ai_shared.auth.models import User, TokenPayload, AuthResult

logger = structlog.get_logger()


class JWTConfig(BaseModel):
    """JWT configuration."""

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    issuer: str = "sql2ai"
    audience: str = "sql2ai-api"


class JWTService:
    """JWT token service for authentication."""

    def __init__(self, config: JWTConfig):
        self.config = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def create_access_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create an access token for a user."""
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.config.access_token_expire_minutes)

        now = datetime.utcnow()
        expire = now + expires_delta

        payload = TokenPayload(
            sub=user.id,
            email=user.email,
            roles=user.roles,
            tenant_id=user.tenant_id,
            iat=int(now.timestamp()),
            exp=int(expire.timestamp()),
            jti=str(ULID()),
            type="access",
        )

        return jwt.encode(
            payload.model_dump(),
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    def create_refresh_token(
        self,
        user: User,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a refresh token for a user."""
        if expires_delta is None:
            expires_delta = timedelta(days=self.config.refresh_token_expire_days)

        now = datetime.utcnow()
        expire = now + expires_delta

        payload = TokenPayload(
            sub=user.id,
            email=user.email,
            roles=[],  # Refresh tokens don't carry roles
            tenant_id=user.tenant_id,
            iat=int(now.timestamp()),
            exp=int(expire.timestamp()),
            jti=str(ULID()),
            type="refresh",
        )

        return jwt.encode(
            payload.model_dump(),
            self.config.secret_key,
            algorithm=self.config.algorithm,
        )

    def create_tokens(self, user: User) -> AuthResult:
        """Create both access and refresh tokens."""
        access_token = self.create_access_token(user)
        refresh_token = self.create_refresh_token(user)

        return AuthResult(
            success=True,
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=self.config.access_token_expire_minutes * 60,
        )

    def verify_token(self, token: str, token_type: str = "access") -> Optional[TokenPayload]:
        """Verify and decode a JWT token.

        Args:
            token: The JWT token to verify
            token_type: Expected token type (access, refresh)

        Returns:
            TokenPayload if valid, None if invalid
        """
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key,
                algorithms=[self.config.algorithm],
            )

            token_payload = TokenPayload(**payload)

            # Verify token type
            if token_payload.type != token_type:
                logger.warning(
                    "jwt_wrong_type",
                    expected=token_type,
                    actual=token_payload.type,
                )
                return None

            return token_payload

        except JWTError as e:
            logger.warning("jwt_verification_failed", error=str(e))
            return None

    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def refresh_access_token(
        self,
        refresh_token: str,
        get_user: callable,
    ) -> AuthResult:
        """Refresh an access token using a refresh token.

        Args:
            refresh_token: The refresh token
            get_user: Async function to get user by ID

        Returns:
            AuthResult with new tokens or error
        """
        payload = self.verify_token(refresh_token, token_type="refresh")
        if not payload:
            return AuthResult(
                success=False,
                error="invalid_token",
                error_description="Invalid or expired refresh token",
            )

        # Get user from database
        user = await get_user(payload.sub)
        if not user:
            return AuthResult(
                success=False,
                error="user_not_found",
                error_description="User not found",
            )

        if not user.is_active:
            return AuthResult(
                success=False,
                error="user_disabled",
                error_description="User account is disabled",
            )

        return self.create_tokens(user)


# Factory function
def create_jwt_service(
    secret_key: str,
    algorithm: str = "HS256",
    access_token_expire_minutes: int = 30,
    refresh_token_expire_days: int = 7,
) -> JWTService:
    """Create a JWT service with the given configuration."""
    config = JWTConfig(
        secret_key=secret_key,
        algorithm=algorithm,
        access_token_expire_minutes=access_token_expire_minutes,
        refresh_token_expire_days=refresh_token_expire_days,
    )
    return JWTService(config)
