"""Sentry error tracking and performance monitoring integration."""

from typing import Any, Dict, Optional, Callable
from contextlib import contextmanager
from functools import wraps
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()


class SentryConfig(BaseModel):
    """Sentry configuration."""

    dsn: str
    environment: str = "development"
    release: Optional[str] = None
    traces_sample_rate: float = 0.1
    profiles_sample_rate: float = 0.1
    debug: bool = False
    disabled: bool = False

    # Performance monitoring
    enable_tracing: bool = True
    attach_stacktrace: bool = True

    # Data scrubbing
    send_default_pii: bool = False


class SentryIntegration:
    """Sentry error tracking and APM integration."""

    def __init__(self, config: SentryConfig):
        self.config = config
        self._sdk = None

        if not config.disabled:
            self._init_sdk()

    def _init_sdk(self):
        """Initialize Sentry SDK."""
        try:
            import sentry_sdk
            from sentry_sdk.integrations.fastapi import FastApiIntegration
            from sentry_sdk.integrations.starlette import StarletteIntegration
            from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
            from sentry_sdk.integrations.redis import RedisIntegration
            from sentry_sdk.integrations.httpx import HttpxIntegration

            sentry_sdk.init(
                dsn=self.config.dsn,
                environment=self.config.environment,
                release=self.config.release,
                traces_sample_rate=self.config.traces_sample_rate,
                profiles_sample_rate=self.config.profiles_sample_rate,
                debug=self.config.debug,
                send_default_pii=self.config.send_default_pii,
                attach_stacktrace=self.config.attach_stacktrace,
                integrations=[
                    FastApiIntegration(transaction_style="endpoint"),
                    StarletteIntegration(transaction_style="endpoint"),
                    SqlalchemyIntegration(),
                    RedisIntegration(),
                    HttpxIntegration(),
                ],
            )

            self._sdk = sentry_sdk
            logger.info(
                "sentry_initialized",
                environment=self.config.environment,
                release=self.config.release,
            )

        except ImportError:
            logger.warning("sentry_sdk_not_installed")
        except Exception as e:
            logger.error("sentry_init_failed", error=str(e))

    def capture_exception(
        self,
        error: Exception,
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Capture an exception and send to Sentry."""
        if not self._sdk:
            return None

        try:
            with self._sdk.push_scope() as scope:
                if extra:
                    for key, value in extra.items():
                        scope.set_extra(key, value)
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

                event_id = self._sdk.capture_exception(error)
                logger.debug("sentry_exception_captured", event_id=event_id)
                return event_id

        except Exception as e:
            logger.error("sentry_capture_failed", error=str(e))
            return None

    def capture_message(
        self,
        message: str,
        level: str = "info",
        extra: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, str]] = None,
    ) -> Optional[str]:
        """Capture a message and send to Sentry."""
        if not self._sdk:
            return None

        try:
            with self._sdk.push_scope() as scope:
                scope.level = level
                if extra:
                    for key, value in extra.items():
                        scope.set_extra(key, value)
                if tags:
                    for key, value in tags.items():
                        scope.set_tag(key, value)

                event_id = self._sdk.capture_message(message)
                return event_id

        except Exception as e:
            logger.error("sentry_message_failed", error=str(e))
            return None

    def set_user(
        self,
        user_id: str,
        email: Optional[str] = None,
        username: Optional[str] = None,
        ip_address: Optional[str] = None,
    ) -> None:
        """Set user context for error tracking."""
        if not self._sdk:
            return

        user_data = {"id": user_id}
        if email:
            user_data["email"] = email
        if username:
            user_data["username"] = username
        if ip_address:
            user_data["ip_address"] = ip_address

        self._sdk.set_user(user_data)

    def set_context(self, name: str, data: Dict[str, Any]) -> None:
        """Set additional context for errors."""
        if self._sdk:
            self._sdk.set_context(name, data)

    def set_tag(self, key: str, value: str) -> None:
        """Set a tag for error grouping."""
        if self._sdk:
            self._sdk.set_tag(key, value)

    def add_breadcrumb(
        self,
        message: str,
        category: str = "default",
        level: str = "info",
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add a breadcrumb for debugging."""
        if self._sdk:
            self._sdk.add_breadcrumb(
                message=message,
                category=category,
                level=level,
                data=data,
            )

    @contextmanager
    def start_transaction(
        self,
        name: str,
        op: str = "task",
        description: Optional[str] = None,
    ):
        """Start a performance transaction."""
        if not self._sdk:
            yield None
            return

        transaction = self._sdk.start_transaction(
            name=name,
            op=op,
            description=description,
        )

        try:
            with transaction:
                yield transaction
        except Exception as e:
            transaction.set_status("internal_error")
            raise

    @contextmanager
    def start_span(
        self,
        op: str,
        description: Optional[str] = None,
    ):
        """Start a performance span within current transaction."""
        if not self._sdk:
            yield None
            return

        with self._sdk.start_span(op=op, description=description) as span:
            yield span

    def flush(self, timeout: float = 2.0) -> None:
        """Flush pending events."""
        if self._sdk:
            self._sdk.flush(timeout=timeout)


def traced(
    op: str = "function",
    description: Optional[str] = None,
):
    """Decorator to trace function execution."""
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            import sentry_sdk
            with sentry_sdk.start_span(
                op=op,
                description=description or func.__name__,
            ):
                return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import sentry_sdk
            with sentry_sdk.start_span(
                op=op,
                description=description or func.__name__,
            ):
                return func(*args, **kwargs)

        if hasattr(func, "__wrapped__"):
            return async_wrapper
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
