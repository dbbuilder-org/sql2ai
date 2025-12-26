"""Audit decorators for automatic audit logging."""

from typing import Any, Callable, Dict, Optional, TypeVar
from functools import wraps
import inspect

from sql2ai_shared.audit.models import AuditAction, AuditSeverity
from sql2ai_shared.audit.logger import get_audit_logger

F = TypeVar("F", bound=Callable[..., Any])


def audited(
    action: AuditAction,
    resource_type: str,
    resource_id_param: Optional[str] = None,
    resource_id_result: Optional[str] = None,
    include_args: bool = False,
    include_result: bool = False,
    severity: Optional[AuditSeverity] = None,
) -> Callable[[F], F]:
    """Decorator to automatically audit function calls.

    Args:
        action: The audit action type
        resource_type: Type of resource being acted upon
        resource_id_param: Parameter name containing the resource ID
        resource_id_result: Result attribute containing the resource ID
        include_args: Whether to include function arguments in details
        include_result: Whether to include the result in details
        severity: Override severity level

    Usage:
        @audited(
            action=AuditAction.USER_UPDATE,
            resource_type="user",
            resource_id_param="user_id",
        )
        async def update_user(user_id: str, data: dict) -> User:
            return await db.update_user(user_id, data)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()

            # Get function signature
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Extract resource ID from parameters
            resource_id = "unknown"
            if resource_id_param and resource_id_param in bound.arguments:
                resource_id = str(bound.arguments[resource_id_param])

            # Build details from arguments
            details = {}
            if include_args:
                for param_name, param_value in bound.arguments.items():
                    if param_name in ("self", "cls", "password"):
                        continue
                    if isinstance(param_value, (str, int, float, bool, list, dict)):
                        details[param_name] = param_value

            # Execute function
            try:
                result = await func(*args, **kwargs)

                # Extract resource ID from result if specified
                if resource_id_result and hasattr(result, resource_id_result):
                    resource_id = str(getattr(result, resource_id_result))

                # Include result in details
                if include_result:
                    if hasattr(result, "model_dump"):
                        details["result"] = result.model_dump()
                    elif isinstance(result, (dict, list, str, int, float, bool)):
                        details["result"] = result

                # Log success
                await audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    success=True,
                    severity=severity,
                )

                return result

            except Exception as e:
                # Log failure
                await audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details=details,
                    success=False,
                    error_message=str(e),
                    severity=severity or AuditSeverity.HIGH,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            import asyncio

            return asyncio.get_event_loop().run_until_complete(
                async_wrapper(*args, **kwargs)
            )

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def audit_data_access(
    resource_type: str,
    resource_id_param: str = "id",
) -> Callable[[F], F]:
    """Shortcut decorator for data access auditing.

    Usage:
        @audit_data_access(resource_type="customer")
        async def get_customer(id: str) -> Customer:
            return await db.get_customer(id)
    """
    return audited(
        action=AuditAction.DATA_READ,
        resource_type=resource_type,
        resource_id_param=resource_id_param,
        severity=AuditSeverity.INFO,
    )


def audit_data_change(
    action: AuditAction,
    resource_type: str,
    resource_id_param: str = "id",
    capture_changes: bool = True,
) -> Callable[[F], F]:
    """Shortcut decorator for data change auditing with before/after capture.

    Usage:
        @audit_data_change(
            action=AuditAction.DATA_UPDATE,
            resource_type="customer",
        )
        async def update_customer(id: str, data: dict) -> Customer:
            return await db.update_customer(id, data)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()

            # Get function signature
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            # Extract resource ID
            resource_id = str(bound.arguments.get(resource_id_param, "unknown"))

            # Capture changes
            old_value = None
            new_value = None

            if capture_changes and "data" in bound.arguments:
                new_value = bound.arguments["data"]
                if isinstance(new_value, dict):
                    new_value = dict(new_value)
                elif hasattr(new_value, "model_dump"):
                    new_value = new_value.model_dump()

            try:
                result = await func(*args, **kwargs)

                # Log with changes
                await audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    old_value=old_value,
                    new_value=new_value,
                    success=True,
                )

                return result

            except Exception as e:
                await audit_logger.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    success=False,
                    error_message=str(e),
                    severity=AuditSeverity.HIGH,
                )
                raise

        return wrapper

    return decorator


def audit_pii_access(
    resource_type: str,
    resource_id_param: str = "id",
    pii_fields: Optional[list] = None,
) -> Callable[[F], F]:
    """Decorator for auditing PII data access with compliance tracking.

    Usage:
        @audit_pii_access(
            resource_type="customer",
            pii_fields=["ssn", "email", "phone"],
        )
        async def get_customer_details(id: str) -> CustomerDetails:
            return await db.get_customer_details(id)
    """

    def decorator(func: F) -> F:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            audit_logger = get_audit_logger()

            # Get function signature
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            resource_id = str(bound.arguments.get(resource_id_param, "unknown"))

            try:
                result = await func(*args, **kwargs)

                # Log PII access
                await audit_logger.log(
                    action=AuditAction.PII_ACCESS,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={
                        "pii_fields_accessed": pii_fields or [],
                        "function": func.__name__,
                    },
                    success=True,
                    severity=AuditSeverity.HIGH,
                )

                return result

            except Exception as e:
                await audit_logger.log(
                    action=AuditAction.PII_ACCESS,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    details={"pii_fields_requested": pii_fields or []},
                    success=False,
                    error_message=str(e),
                    severity=AuditSeverity.CRITICAL,
                )
                raise

        return wrapper

    return decorator


class AuditContext:
    """Context manager for manual audit logging."""

    def __init__(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        user_id: Optional[str] = None,
        severity: Optional[AuditSeverity] = None,
    ):
        self.action = action
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.user_id = user_id
        self.severity = severity
        self.details: Dict[str, Any] = {}
        self._old_value = None
        self._new_value = None
        self._success = True
        self._error_message = None

    def set_old_value(self, value: Any) -> None:
        """Set the old value for change tracking."""
        if hasattr(value, "model_dump"):
            self._old_value = value.model_dump()
        else:
            self._old_value = value

    def set_new_value(self, value: Any) -> None:
        """Set the new value for change tracking."""
        if hasattr(value, "model_dump"):
            self._new_value = value.model_dump()
        else:
            self._new_value = value

    def add_detail(self, key: str, value: Any) -> None:
        """Add a detail to the audit entry."""
        self.details[key] = value

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._success = False
            self._error_message = str(exc_val)

        audit_logger = get_audit_logger()
        await audit_logger.log(
            action=self.action,
            resource_type=self.resource_type,
            resource_id=self.resource_id,
            user_id=self.user_id,
            details=self.details,
            old_value=self._old_value,
            new_value=self._new_value,
            success=self._success,
            error_message=self._error_message,
            severity=self.severity,
        )
