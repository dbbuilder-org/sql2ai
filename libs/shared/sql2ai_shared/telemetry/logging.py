"""Structured logging with OpenTelemetry correlation."""

from typing import Any, Dict, List, Optional
import logging
import sys
from pydantic import BaseModel
import structlog
from structlog.typing import EventDict, WrappedLogger

from sql2ai_shared.tenancy.context import get_current_tenant


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = "INFO"
    format: str = "json"  # "json" or "console"
    service_name: str = "sql2ai"
    environment: str = "development"
    include_trace_id: bool = True
    include_tenant_id: bool = True
    additional_processors: List[str] = []


_config: Optional[LoggingConfig] = None


def add_tenant_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add tenant context to log events."""
    tenant = get_current_tenant()
    if tenant:
        event_dict["tenant_id"] = tenant.id
        event_dict["tenant_tier"] = tenant.tier
    return event_dict


def add_trace_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add OpenTelemetry trace context to log events."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        if span.is_recording():
            ctx = span.get_span_context()
            event_dict["trace_id"] = format(ctx.trace_id, "032x")
            event_dict["span_id"] = format(ctx.span_id, "016x")
    except ImportError:
        pass
    except Exception:
        pass

    return event_dict


def add_service_context(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """Add service context to log events."""
    if _config:
        event_dict["service"] = _config.service_name
        event_dict["environment"] = _config.environment
    return event_dict


def init_logging(config: LoggingConfig) -> None:
    """Initialize structured logging."""
    global _config
    _config = config

    # Build processor chain
    processors: List[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        add_service_context,
    ]

    if config.include_tenant_id:
        processors.append(add_tenant_context)

    if config.include_trace_id:
        processors.append(add_trace_context)

    processors.extend([
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ])

    # Add format-specific processors
    if config.format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    # Configure structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, config.level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, config.level.upper()),
    )

    # Integrate standard library logging with structlog
    structlog.configure_once(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: Optional[str] = None) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary log context."""

    def __init__(self, **kwargs):
        self.context = kwargs
        self._token = None

    def __enter__(self):
        self._token = structlog.contextvars.bind_contextvars(**self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())


def bind_context(**kwargs) -> None:
    """Bind context variables for all subsequent log calls."""
    structlog.contextvars.bind_contextvars(**kwargs)


def unbind_context(*keys: str) -> None:
    """Unbind context variables."""
    structlog.contextvars.unbind_contextvars(*keys)


def clear_context() -> None:
    """Clear all context variables."""
    structlog.contextvars.clear_contextvars()


class AuditLogger:
    """Specialized logger for audit events."""

    def __init__(self, name: str = "audit"):
        self.logger = get_logger(name)

    def log_action(
        self,
        action: str,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ) -> None:
        """Log an auditable action."""
        self.logger.info(
            "audit_event",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            success=success,
            **(details or {}),
        )

    def log_access(
        self,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        access_type: str = "read",
    ) -> None:
        """Log resource access."""
        self.logger.info(
            "access_event",
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            access_type=access_type,
        )

    def log_security_event(
        self,
        event_type: str,
        severity: str,
        details: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> None:
        """Log a security event."""
        log_method = getattr(self.logger, severity.lower(), self.logger.warning)
        log_method(
            "security_event",
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            **details,
        )


class PerformanceLogger:
    """Specialized logger for performance metrics."""

    def __init__(self, name: str = "performance"):
        self.logger = get_logger(name)

    def log_query(
        self,
        query_hash: str,
        duration_ms: float,
        rows_affected: int,
        database_type: str,
    ) -> None:
        """Log query performance."""
        level = "warning" if duration_ms > 1000 else "info"
        log_method = getattr(self.logger, level)
        log_method(
            "query_performance",
            query_hash=query_hash,
            duration_ms=duration_ms,
            rows_affected=rows_affected,
            database_type=database_type,
            slow=duration_ms > 1000,
        )

    def log_operation(
        self,
        operation: str,
        duration_ms: float,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log operation performance."""
        self.logger.info(
            "operation_performance",
            operation=operation,
            duration_ms=duration_ms,
            success=success,
            **(details or {}),
        )
