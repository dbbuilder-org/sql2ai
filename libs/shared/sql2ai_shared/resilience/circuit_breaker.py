"""Circuit breaker pattern for fault tolerance."""

from functools import wraps
from typing import Callable, Tuple, Type, TypeVar, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import structlog

logger = structlog.get_logger()

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening
    recovery_timeout: float = 30.0  # Seconds before trying again
    half_open_max_calls: int = 3  # Test calls in half-open state
    expected_exceptions: Tuple[Type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        OSError,
    )


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, circuit_name: str, retry_after: datetime):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit breaker '{circuit_name}' is open. "
            f"Retry after {retry_after.isoformat()}"
        )


class CircuitBreaker:
    """Circuit breaker implementation."""

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None
        self.half_open_calls = 0
        self._lock = asyncio.Lock()

    async def _check_state(self) -> None:
        """Check and potentially transition state."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self.last_failure_time:
                    recovery_time = self.last_failure_time + timedelta(
                        seconds=self.config.recovery_timeout
                    )
                    if datetime.utcnow() >= recovery_time:
                        logger.info(
                            "circuit_breaker_half_open",
                            circuit=self.name,
                        )
                        self.state = CircuitState.HALF_OPEN
                        self.half_open_calls = 0

    async def _record_success(self) -> None:
        """Record a successful call."""
        async with self._lock:
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                self.half_open_calls += 1
                if self.success_count >= self.config.half_open_max_calls:
                    logger.info(
                        "circuit_breaker_closed",
                        circuit=self.name,
                    )
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
            elif self.state == CircuitState.CLOSED:
                self.failure_count = max(0, self.failure_count - 1)

    async def _record_failure(self, exc: Exception) -> None:
        """Record a failed call."""
        async with self._lock:
            self.failure_count += 1
            self.last_failure_time = datetime.utcnow()

            if self.state == CircuitState.HALF_OPEN:
                logger.warning(
                    "circuit_breaker_open",
                    circuit=self.name,
                    reason="failure_in_half_open",
                    exception=str(exc),
                )
                self.state = CircuitState.OPEN
            elif (
                self.state == CircuitState.CLOSED
                and self.failure_count >= self.config.failure_threshold
            ):
                logger.warning(
                    "circuit_breaker_open",
                    circuit=self.name,
                    reason="threshold_exceeded",
                    failures=self.failure_count,
                )
                self.state = CircuitState.OPEN

    async def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Execute a function through the circuit breaker."""
        await self._check_state()

        if self.state == CircuitState.OPEN:
            retry_after = self.last_failure_time + timedelta(
                seconds=self.config.recovery_timeout
            )
            raise CircuitBreakerError(self.name, retry_after)

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            await self._record_success()
            return result
        except self.config.expected_exceptions as e:
            await self._record_failure(e)
            raise


# Global circuit breaker registry
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    name: str, config: CircuitBreakerConfig = CircuitBreakerConfig()
) -> CircuitBreaker:
    """Get or create a circuit breaker by name."""
    if name not in _circuit_breakers:
        _circuit_breakers[name] = CircuitBreaker(name, config)
    return _circuit_breakers[name]


def circuit_protected(
    name: str | None = None,
    config: CircuitBreakerConfig = CircuitBreakerConfig(),
):
    """Decorator for protecting functions with a circuit breaker.

    Usage:
        @circuit_protected("external_api")
        async def call_api():
            return await client.get(url)

        @circuit_protected(config=CircuitBreakerConfig(failure_threshold=3))
        async def sensitive_operation():
            pass
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        circuit_name = name or f"{func.__module__}.{func.__name__}"
        circuit = get_circuit_breaker(circuit_name, config)

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            return await circuit.call(func, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            import asyncio

            return asyncio.get_event_loop().run_until_complete(
                circuit.call(func, *args, **kwargs)
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
