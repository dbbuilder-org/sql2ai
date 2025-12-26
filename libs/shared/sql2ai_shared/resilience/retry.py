"""Retry patterns with exponential backoff."""

from functools import wraps
from typing import Callable, Tuple, Type, TypeVar, Any
from dataclasses import dataclass
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
    RetryError,
)
import structlog

logger = structlog.get_logger()

T = TypeVar("T")


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    min_wait_seconds: float = 1.0
    max_wait_seconds: float = 30.0
    exponential_base: float = 2.0
    retryable_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


DEFAULT_RETRY_CONFIG = RetryConfig()


def with_retry(
    config: RetryConfig = DEFAULT_RETRY_CONFIG,
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """Decorator for adding retry logic with exponential backoff.

    Args:
        config: Retry configuration
        on_retry: Optional callback called on each retry

    Usage:
        @with_retry()
        async def fetch_data():
            return await client.get(url)

        @with_retry(RetryConfig(max_attempts=5))
        async def important_operation():
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.exponential_base,
                min=config.min_wait_seconds,
                max=config.max_wait_seconds,
            ),
            retry=retry_if_exception_type(config.retryable_exceptions),
            before_sleep=before_sleep_log(logger, structlog.stdlib.INFO),
            reraise=True,
        )
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            return await func(*args, **kwargs)

        @retry(
            stop=stop_after_attempt(config.max_attempts),
            wait=wait_exponential(
                multiplier=config.exponential_base,
                min=config.min_wait_seconds,
                max=config.max_wait_seconds,
            ),
            retry=retry_if_exception_type(config.retryable_exceptions),
            before_sleep=before_sleep_log(logger, structlog.stdlib.INFO),
            reraise=True,
        )
        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            return func(*args, **kwargs)

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class RetryableError(Exception):
    """Base class for errors that should trigger retry."""

    pass


class NonRetryableError(Exception):
    """Base class for errors that should NOT trigger retry."""

    pass
