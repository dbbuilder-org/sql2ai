"""Bulkhead pattern for resource isolation."""

from functools import wraps
from typing import Callable, TypeVar, Any
from dataclasses import dataclass
import asyncio
import structlog

logger = structlog.get_logger()

T = TypeVar("T")


@dataclass
class BulkheadConfig:
    """Configuration for a bulkhead."""

    max_concurrent: int
    max_waiting: int = 0  # 0 = no queue, reject immediately
    timeout: float = 30.0  # Seconds to wait in queue


class BulkheadFullError(Exception):
    """Raised when bulkhead is at capacity."""

    def __init__(self, bulkhead_name: str, current: int, max_concurrent: int):
        self.bulkhead_name = bulkhead_name
        self.current = current
        self.max_concurrent = max_concurrent
        super().__init__(
            f"Bulkhead '{bulkhead_name}' is full: {current}/{max_concurrent}. "
            f"Please try again later."
        )


class Bulkhead:
    """Bulkhead implementation using semaphores."""

    def __init__(self, name: str, config: BulkheadConfig):
        self.name = name
        self.config = config
        self._semaphore = asyncio.Semaphore(config.max_concurrent)
        self._waiting = 0
        self._active = 0
        self._lock = asyncio.Lock()

    @property
    def available(self) -> int:
        """Number of available slots."""
        return self.config.max_concurrent - self._active

    @property
    def waiting(self) -> int:
        """Number of waiting requests."""
        return self._waiting

    async def acquire(self) -> bool:
        """Acquire a slot in the bulkhead."""
        async with self._lock:
            if self._active >= self.config.max_concurrent:
                if self.config.max_waiting > 0 and self._waiting < self.config.max_waiting:
                    self._waiting += 1
                else:
                    raise BulkheadFullError(
                        self.name, self._active, self.config.max_concurrent
                    )

        try:
            acquired = await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self.config.timeout,
            )
            async with self._lock:
                if self._waiting > 0:
                    self._waiting -= 1
                self._active += 1
            return acquired
        except asyncio.TimeoutError:
            async with self._lock:
                if self._waiting > 0:
                    self._waiting -= 1
            raise BulkheadFullError(
                self.name, self._active, self.config.max_concurrent
            )

    def release(self) -> None:
        """Release a slot in the bulkhead."""
        self._semaphore.release()
        asyncio.create_task(self._decrement_active())

    async def _decrement_active(self) -> None:
        async with self._lock:
            self._active = max(0, self._active - 1)

    async def __aenter__(self) -> "Bulkhead":
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        self.release()


class BulkheadManager:
    """Manager for multiple bulkheads."""

    def __init__(self):
        self._bulkheads: dict[str, Bulkhead] = {}
        self._lock = asyncio.Lock()

        # Default bulkhead configurations
        self._default_configs = {
            "ai_requests": BulkheadConfig(max_concurrent=10, max_waiting=50, timeout=60.0),
            "db_connections": BulkheadConfig(max_concurrent=50, max_waiting=100, timeout=30.0),
            "file_processing": BulkheadConfig(max_concurrent=5, max_waiting=20, timeout=120.0),
            "external_api": BulkheadConfig(max_concurrent=20, max_waiting=50, timeout=30.0),
        }

    async def get_bulkhead(
        self, name: str, config: BulkheadConfig | None = None
    ) -> Bulkhead:
        """Get or create a bulkhead by name."""
        async with self._lock:
            if name not in self._bulkheads:
                if config is None:
                    config = self._default_configs.get(
                        name, BulkheadConfig(max_concurrent=10)
                    )
                self._bulkheads[name] = Bulkhead(name, config)
            return self._bulkheads[name]

    async def execute(
        self, bulkhead_name: str, func: Callable[..., T], *args: Any, **kwargs: Any
    ) -> T:
        """Execute a function within a bulkhead."""
        bulkhead = await self.get_bulkhead(bulkhead_name)
        async with bulkhead:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)

    def status(self) -> dict[str, dict]:
        """Get status of all bulkheads."""
        return {
            name: {
                "active": b._active,
                "waiting": b._waiting,
                "available": b.available,
                "max_concurrent": b.config.max_concurrent,
            }
            for name, b in self._bulkheads.items()
        }


# Global bulkhead manager
_bulkhead_manager = BulkheadManager()


def get_bulkhead_manager() -> BulkheadManager:
    """Get the global bulkhead manager."""
    return _bulkhead_manager


def bulkhead(name: str, config: BulkheadConfig | None = None):
    """Decorator for protecting functions with a bulkhead.

    Usage:
        @bulkhead("ai_requests")
        async def call_ai():
            return await litellm.acompletion(...)

        @bulkhead("db_connections", BulkheadConfig(max_concurrent=20))
        async def query_database():
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await _bulkhead_manager.execute(name, func, *args, **kwargs)

        return wrapper

    return decorator
