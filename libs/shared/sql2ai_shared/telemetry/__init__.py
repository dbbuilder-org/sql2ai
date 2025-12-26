"""Telemetry and observability with OpenTelemetry."""

from sql2ai_shared.telemetry.tracing import (
    TracingConfig,
    init_tracing,
    get_tracer,
    traced,
    span_event,
    set_span_attribute,
)
from sql2ai_shared.telemetry.metrics import (
    MetricsConfig,
    init_metrics,
    get_meter,
    counter,
    histogram,
    gauge,
)
from sql2ai_shared.telemetry.logging import (
    LoggingConfig,
    init_logging,
    get_logger,
)

__all__ = [
    # Tracing
    "TracingConfig",
    "init_tracing",
    "get_tracer",
    "traced",
    "span_event",
    "set_span_attribute",
    # Metrics
    "MetricsConfig",
    "init_metrics",
    "get_meter",
    "counter",
    "histogram",
    "gauge",
    # Logging
    "LoggingConfig",
    "init_logging",
    "get_logger",
]
