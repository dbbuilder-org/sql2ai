"""Metrics collection with OpenTelemetry."""

from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps
import time
import inspect
from pydantic import BaseModel

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.semconv.resource import ResourceAttributes

from sql2ai_shared.tenancy.context import get_current_tenant

F = TypeVar("F", bound=Callable[..., Any])


class MetricsConfig(BaseModel):
    """Metrics configuration."""

    service_name: str = "sql2ai"
    service_version: str = "1.0.0"
    environment: str = "development"
    otlp_endpoint: Optional[str] = None
    otlp_headers: Dict[str, str] = {}
    export_interval_ms: int = 60000
    enabled: bool = True


_meter_provider: Optional[MeterProvider] = None
_config: Optional[MetricsConfig] = None
_meters: Dict[str, metrics.Meter] = {}


def init_metrics(config: MetricsConfig) -> None:
    """Initialize OpenTelemetry metrics."""
    global _meter_provider, _config

    if not config.enabled:
        return

    _config = config

    # Create resource with service info
    resource = Resource.create({
        ResourceAttributes.SERVICE_NAME: config.service_name,
        ResourceAttributes.SERVICE_VERSION: config.service_version,
        ResourceAttributes.DEPLOYMENT_ENVIRONMENT: config.environment,
    })

    readers = []

    # Add OTLP exporter if endpoint is configured
    if config.otlp_endpoint:
        from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
            OTLPMetricExporter,
        )

        exporter = OTLPMetricExporter(
            endpoint=config.otlp_endpoint,
            headers=config.otlp_headers,
        )
        reader = PeriodicExportingMetricReader(
            exporter,
            export_interval_millis=config.export_interval_ms,
        )
        readers.append(reader)

    # Create meter provider
    _meter_provider = MeterProvider(
        resource=resource,
        metric_readers=readers,
    )

    # Set global meter provider
    metrics.set_meter_provider(_meter_provider)


def get_meter(name: Optional[str] = None) -> metrics.Meter:
    """Get a meter instance."""
    meter_name = name or (_config.service_name if _config else "sql2ai")

    if meter_name not in _meters:
        if _meter_provider:
            _meters[meter_name] = _meter_provider.get_meter(meter_name)
        else:
            _meters[meter_name] = metrics.get_meter(meter_name)

    return _meters[meter_name]


def counter(
    name: str,
    description: str = "",
    unit: str = "1",
    attributes: Optional[Dict[str, str]] = None,
) -> Callable[[F], F]:
    """Decorator to count function calls.

    Usage:
        @counter("api.requests", description="API request count")
        async def handle_request():
            pass
    """

    def decorator(func: F) -> F:
        meter = get_meter()
        _counter = meter.create_counter(
            name=name,
            description=description,
            unit=unit,
        )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attrs = dict(attributes or {})

            # Add tenant context
            tenant = get_current_tenant()
            if tenant:
                attrs["tenant_id"] = tenant.id
                attrs["tenant_tier"] = tenant.tier

            try:
                result = await func(*args, **kwargs)
                attrs["status"] = "success"
                _counter.add(1, attrs)
                return result
            except Exception as e:
                attrs["status"] = "error"
                attrs["error_type"] = type(e).__name__
                _counter.add(1, attrs)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attrs = dict(attributes or {})

            tenant = get_current_tenant()
            if tenant:
                attrs["tenant_id"] = tenant.id

            try:
                result = func(*args, **kwargs)
                attrs["status"] = "success"
                _counter.add(1, attrs)
                return result
            except Exception as e:
                attrs["status"] = "error"
                attrs["error_type"] = type(e).__name__
                _counter.add(1, attrs)
                raise

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def histogram(
    name: str,
    description: str = "",
    unit: str = "ms",
    buckets: Optional[List[float]] = None,
    attributes: Optional[Dict[str, str]] = None,
) -> Callable[[F], F]:
    """Decorator to record function execution time.

    Usage:
        @histogram("api.latency", description="API latency")
        async def handle_request():
            pass
    """

    def decorator(func: F) -> F:
        meter = get_meter()
        _histogram = meter.create_histogram(
            name=name,
            description=description,
            unit=unit,
        )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attrs = dict(attributes or {})

            tenant = get_current_tenant()
            if tenant:
                attrs["tenant_id"] = tenant.id
                attrs["tenant_tier"] = tenant.tier

            start = time.perf_counter()
            try:
                result = await func(*args, **kwargs)
                attrs["status"] = "success"
                return result
            except Exception as e:
                attrs["status"] = "error"
                attrs["error_type"] = type(e).__name__
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                _histogram.record(duration_ms, attrs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attrs = dict(attributes or {})

            tenant = get_current_tenant()
            if tenant:
                attrs["tenant_id"] = tenant.id

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                attrs["status"] = "success"
                return result
            except Exception as e:
                attrs["status"] = "error"
                attrs["error_type"] = type(e).__name__
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                _histogram.record(duration_ms, attrs)

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


class GaugeValue:
    """Thread-safe gauge value container."""

    def __init__(self, initial: float = 0.0):
        self._value = initial

    @property
    def value(self) -> float:
        return self._value

    def set(self, value: float) -> None:
        self._value = value

    def increment(self, amount: float = 1.0) -> None:
        self._value += amount

    def decrement(self, amount: float = 1.0) -> None:
        self._value -= amount


_gauges: Dict[str, GaugeValue] = {}


def gauge(
    name: str,
    description: str = "",
    unit: str = "1",
) -> GaugeValue:
    """Create or get a gauge metric.

    Usage:
        active_connections = gauge("db.connections.active")
        active_connections.increment()
        # ... do work ...
        active_connections.decrement()
    """
    if name not in _gauges:
        meter = get_meter()
        gauge_value = GaugeValue()
        _gauges[name] = gauge_value

        # Create observable gauge
        def callback(options):
            tenant = get_current_tenant()
            attrs = {}
            if tenant:
                attrs["tenant_id"] = tenant.id
            yield metrics.Observation(gauge_value.value, attrs)

        meter.create_observable_gauge(
            name=name,
            description=description,
            unit=unit,
            callbacks=[callback],
        )

    return _gauges[name]


class MetricsCollector:
    """Helper class for collecting custom metrics."""

    def __init__(self, prefix: str = "sql2ai"):
        self.prefix = prefix
        self.meter = get_meter(prefix)
        self._counters: Dict[str, Any] = {}
        self._histograms: Dict[str, Any] = {}

    def count(
        self,
        name: str,
        value: int = 1,
        attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a counter value."""
        full_name = f"{self.prefix}.{name}"

        if full_name not in self._counters:
            self._counters[full_name] = self.meter.create_counter(full_name)

        attrs = dict(attributes or {})
        tenant = get_current_tenant()
        if tenant:
            attrs["tenant_id"] = tenant.id

        self._counters[full_name].add(value, attrs)

    def record_duration(
        self,
        name: str,
        duration_ms: float,
        attributes: Optional[Dict[str, str]] = None,
    ) -> None:
        """Record a duration value."""
        full_name = f"{self.prefix}.{name}"

        if full_name not in self._histograms:
            self._histograms[full_name] = self.meter.create_histogram(
                full_name, unit="ms"
            )

        attrs = dict(attributes or {})
        tenant = get_current_tenant()
        if tenant:
            attrs["tenant_id"] = tenant.id

        self._histograms[full_name].record(duration_ms, attrs)


# Pre-built metrics for common use cases
class SQL2AIMetrics:
    """Pre-built metrics for SQL2.AI platform."""

    def __init__(self):
        self.collector = MetricsCollector("sql2ai")

    def query_executed(
        self,
        duration_ms: float,
        database_type: str,
        success: bool,
    ) -> None:
        """Record a query execution."""
        self.collector.count(
            "queries.total",
            attributes={
                "database_type": database_type,
                "status": "success" if success else "error",
            },
        )
        self.collector.record_duration(
            "queries.duration",
            duration_ms,
            attributes={"database_type": database_type},
        )

    def ai_request(
        self,
        duration_ms: float,
        model: str,
        tokens: int,
        success: bool,
    ) -> None:
        """Record an AI request."""
        self.collector.count(
            "ai.requests",
            attributes={
                "model": model,
                "status": "success" if success else "error",
            },
        )
        self.collector.count("ai.tokens", tokens, attributes={"model": model})
        self.collector.record_duration(
            "ai.latency",
            duration_ms,
            attributes={"model": model},
        )

    def cache_operation(
        self,
        operation: str,
        hit: bool,
    ) -> None:
        """Record a cache operation."""
        self.collector.count(
            "cache.operations",
            attributes={
                "operation": operation,
                "result": "hit" if hit else "miss",
            },
        )
