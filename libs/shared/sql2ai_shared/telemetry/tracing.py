"""Distributed tracing with OpenTelemetry."""

from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps
import inspect
from pydantic import BaseModel

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.trace import Status, StatusCode, Span

from sql2ai_shared.tenancy.context import get_current_tenant

F = TypeVar("F", bound=Callable[..., Any])


class TracingConfig(BaseModel):
    """Tracing configuration."""

    service_name: str = "sql2ai"
    service_version: str = "1.0.0"
    environment: str = "development"
    otlp_endpoint: Optional[str] = None
    otlp_headers: Dict[str, str] = {}
    sample_rate: float = 1.0
    enabled: bool = True


_tracer_provider: Optional[TracerProvider] = None
_config: Optional[TracingConfig] = None


def init_tracing(config: TracingConfig) -> None:
    """Initialize OpenTelemetry tracing."""
    global _tracer_provider, _config

    if not config.enabled:
        return

    _config = config

    # Create resource with service info
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: config.service_name,
        ResourceAttributes.SERVICE_VERSION: config.service_version,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: config.environment,
    })

    # Create tracer provider
    _tracer_provider = TracerProvider(resource=resource)

    # Add OTLP exporter if endpoint is configured
    if config.otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )

        exporter = OTLPSpanExporter(
            endpoint=config.otlp_endpoint,
            headers=config.otlp_headers,
        )
        _tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

    # Set global tracer provider
    trace.set_tracer_provider(_tracer_provider)


def get_tracer(name: Optional[str] = None) -> trace.Tracer:
    """Get a tracer instance."""
    if _tracer_provider is None:
        return trace.get_tracer(name or "sql2ai")
    return _tracer_provider.get_tracer(name or _config.service_name)


def span_event(
    name: str,
    attributes: Optional[Dict[str, Any]] = None,
) -> None:
    """Add an event to the current span."""
    span = trace.get_current_span()
    if span.is_recording():
        span.add_event(name, attributes=attributes or {})


def set_span_attribute(key: str, value: Any) -> None:
    """Set an attribute on the current span."""
    span = trace.get_current_span()
    if span.is_recording():
        span.set_attribute(key, value)


def traced(
    name: Optional[str] = None,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True,
    include_args: bool = False,
) -> Callable[[F], F]:
    """Decorator to trace function execution.

    Args:
        name: Span name (defaults to function name)
        attributes: Static attributes to add to span
        record_exception: Whether to record exceptions
        include_args: Whether to include function arguments as attributes

    Usage:
        @traced(name="fetch_user", attributes={"component": "user_service"})
        async def get_user(user_id: str) -> User:
            return await db.get_user(user_id)
    """

    def decorator(func: F) -> F:
        span_name = name or f"{func.__module__}.{func.__name__}"
        tracer = get_tracer()

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add tenant context
                tenant = get_current_tenant()
                if tenant:
                    span.set_attribute("tenant.id", tenant.id)
                    span.set_attribute("tenant.tier", tenant.tier)

                # Add function arguments
                if include_args:
                    sig = inspect.signature(func)
                    bound = sig.bind(*args, **kwargs)
                    bound.apply_defaults()

                    for param_name, param_value in bound.arguments.items():
                        if param_name not in ("self", "cls"):
                            # Only include simple types
                            if isinstance(param_value, (str, int, float, bool)):
                                span.set_attribute(
                                    f"arg.{param_name}", param_value
                                )

                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            with tracer.start_as_current_span(span_name) as span:
                # Add static attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, value)

                # Add tenant context
                tenant = get_current_tenant()
                if tenant:
                    span.set_attribute("tenant.id", tenant.id)
                    span.set_attribute("tenant.tier", tenant.tier)

                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result

                except Exception as e:
                    if record_exception:
                        span.record_exception(e)
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                    raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class SpanContext:
    """Context manager for creating spans."""

    def __init__(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        self.name = name
        self.attributes = attributes or {}
        self._span: Optional[Span] = None
        self._tracer = get_tracer()

    def __enter__(self) -> "SpanContext":
        self._span = self._tracer.start_span(self.name)
        self._span.__enter__()

        # Add attributes
        for key, value in self.attributes.items():
            self._span.set_attribute(key, value)

        # Add tenant context
        tenant = get_current_tenant()
        if tenant:
            self._span.set_attribute("tenant.id", tenant.id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._span.record_exception(exc_val)
            self._span.set_status(Status(StatusCode.ERROR, str(exc_val)))
        else:
            self._span.set_status(Status(StatusCode.OK))

        self._span.__exit__(exc_type, exc_val, exc_tb)

    def add_event(self, name: str, attributes: Optional[Dict[str, Any]] = None):
        """Add an event to the span."""
        if self._span and self._span.is_recording():
            self._span.add_event(name, attributes=attributes or {})

    def set_attribute(self, key: str, value: Any):
        """Set an attribute on the span."""
        if self._span and self._span.is_recording():
            self._span.set_attribute(key, value)
