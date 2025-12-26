"""Trigger system for SQL Orchestrator checks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from croniter import croniter

from models import CheckCategory


class TriggerType(str, Enum):
    """Types of check triggers."""

    SCHEDULED = "scheduled"
    DEPLOYMENT = "deployment"
    ANOMALY = "anomaly"
    ON_DEMAND = "on_demand"
    SCHEMA_CHANGE = "schema_change"
    THRESHOLD = "threshold"


@dataclass
class TriggerContext:
    """Context passed to triggered checks."""

    trigger_type: TriggerType
    source: str
    connection_id: str
    tenant_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    before_snapshot: Optional[dict] = None
    triggered_at: datetime = field(default_factory=datetime.utcnow)


class CheckTrigger(ABC):
    """Base class for check triggers."""

    def __init__(self, trigger_type: TriggerType):
        self.trigger_type = trigger_type
        self.enabled = True

    @abstractmethod
    def should_trigger(self, context: dict[str, Any]) -> bool:
        """Determine if the trigger should fire."""
        pass

    @abstractmethod
    def get_checks_to_run(self) -> list[str]:
        """Get list of check IDs to run when triggered."""
        pass

    def create_context(
        self,
        connection_id: str,
        tenant_id: str,
        source: str,
        **metadata
    ) -> TriggerContext:
        """Create a trigger context."""
        return TriggerContext(
            trigger_type=self.trigger_type,
            source=source,
            connection_id=connection_id,
            tenant_id=tenant_id,
            metadata=metadata,
        )


class ScheduledTrigger(CheckTrigger):
    """Trigger checks on a cron schedule."""

    def __init__(
        self,
        cron_expression: str,
        check_ids: list[str],
        categories: Optional[list[CheckCategory]] = None,
    ):
        super().__init__(TriggerType.SCHEDULED)
        self.cron_expression = cron_expression
        self.check_ids = check_ids
        self.categories = categories or []
        self._cron = croniter(cron_expression)
        self.last_run: Optional[datetime] = None

    def should_trigger(self, context: dict[str, Any]) -> bool:
        """Check if it's time to run based on cron schedule."""
        now = context.get("current_time", datetime.utcnow())

        if self.last_run is None:
            return True

        next_run = self._cron.get_next(datetime, self.last_run)
        return now >= next_run

    def get_checks_to_run(self) -> list[str]:
        """Get scheduled check IDs."""
        return self.check_ids

    def get_next_run(self, from_time: Optional[datetime] = None) -> datetime:
        """Get the next scheduled run time."""
        base = from_time or datetime.utcnow()
        return croniter(self.cron_expression, base).get_next(datetime)

    def mark_run(self):
        """Mark that the trigger has run."""
        self.last_run = datetime.utcnow()


class DeploymentTrigger(CheckTrigger):
    """Trigger checks on database deployments."""

    def __init__(
        self,
        check_ids: Optional[list[str]] = None,
        run_before: bool = True,
        run_after: bool = True,
        capture_snapshot: bool = True,
    ):
        super().__init__(TriggerType.DEPLOYMENT)
        self.check_ids = check_ids or []
        self.run_before = run_before
        self.run_after = run_after
        self.capture_snapshot = capture_snapshot

    def should_trigger(self, context: dict[str, Any]) -> bool:
        """Check if deployment event matches trigger criteria."""
        event_type = context.get("event_type")

        if event_type == "deployment_started" and self.run_before:
            return True
        if event_type == "deployment_completed" and self.run_after:
            return True

        return False

    def get_checks_to_run(self) -> list[str]:
        """Get deployment-related check IDs."""
        if self.check_ids:
            return self.check_ids
        # Default checks for deployments
        return ["PERF001", "PERF002", "SEC001", "SEC002"]


class AnomalyTrigger(CheckTrigger):
    """Trigger checks when anomalies are detected."""

    def __init__(
        self,
        metric: str,
        threshold: float,
        comparison: str,  # "gt", "lt", "gte", "lte"
        check_ids: list[str],
        cooldown_seconds: int = 300,
    ):
        super().__init__(TriggerType.ANOMALY)
        self.metric = metric
        self.threshold = threshold
        self.comparison = comparison
        self.check_ids = check_ids
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered: Optional[datetime] = None

    def should_trigger(self, context: dict[str, Any]) -> bool:
        """Check if metric exceeds threshold."""
        value = context.get("metrics", {}).get(self.metric)
        if value is None:
            return False

        # Check cooldown
        if self.last_triggered:
            elapsed = (datetime.utcnow() - self.last_triggered).total_seconds()
            if elapsed < self.cooldown_seconds:
                return False

        # Compare value to threshold
        comparisons = {
            "gt": value > self.threshold,
            "lt": value < self.threshold,
            "gte": value >= self.threshold,
            "lte": value <= self.threshold,
        }

        triggered = comparisons.get(self.comparison, False)
        if triggered:
            self.last_triggered = datetime.utcnow()

        return triggered

    def get_checks_to_run(self) -> list[str]:
        """Get anomaly-related check IDs."""
        return self.check_ids


class OnDemandTrigger(CheckTrigger):
    """Trigger checks on demand via API or UI."""

    def __init__(self, check_ids: Optional[list[str]] = None):
        super().__init__(TriggerType.ON_DEMAND)
        self.check_ids = check_ids or []

    def should_trigger(self, context: dict[str, Any]) -> bool:
        """On-demand triggers always fire when requested."""
        return context.get("requested", False)

    def get_checks_to_run(self) -> list[str]:
        """Get requested check IDs."""
        return self.check_ids


class SchemaChangeTrigger(CheckTrigger):
    """Trigger checks when schema changes are detected."""

    def __init__(
        self,
        check_ids: Optional[list[str]] = None,
        object_types: Optional[list[str]] = None,
        schemas: Optional[list[str]] = None,
    ):
        super().__init__(TriggerType.SCHEMA_CHANGE)
        self.check_ids = check_ids or []
        self.object_types = object_types or ["table", "view", "procedure", "function"]
        self.schemas = schemas  # None = all schemas

    def should_trigger(self, context: dict[str, Any]) -> bool:
        """Check if schema change matches trigger criteria."""
        change = context.get("schema_change", {})
        if not change:
            return False

        object_type = change.get("object_type", "").lower()
        schema_name = change.get("schema", "")

        if object_type not in self.object_types:
            return False

        if self.schemas and schema_name not in self.schemas:
            return False

        return True

    def get_checks_to_run(self) -> list[str]:
        """Get schema-related check IDs."""
        if self.check_ids:
            return self.check_ids
        return ["PERF001", "SEC001"]


class TriggerManager:
    """Manages all triggers for an orchestrator instance."""

    def __init__(self):
        self._triggers: list[CheckTrigger] = []

    def add_trigger(self, trigger: CheckTrigger):
        """Add a trigger."""
        self._triggers.append(trigger)

    def remove_trigger(self, trigger: CheckTrigger):
        """Remove a trigger."""
        self._triggers.remove(trigger)

    def get_triggered_checks(self, context: dict[str, Any]) -> list[tuple[CheckTrigger, list[str]]]:
        """Get all triggers that should fire and their checks."""
        results = []
        for trigger in self._triggers:
            if trigger.enabled and trigger.should_trigger(context):
                checks = trigger.get_checks_to_run()
                if checks:
                    results.append((trigger, checks))
        return results

    def get_triggers_by_type(self, trigger_type: TriggerType) -> list[CheckTrigger]:
        """Get all triggers of a specific type."""
        return [t for t in self._triggers if t.trigger_type == trigger_type]

    def get_scheduled_triggers(self) -> list[ScheduledTrigger]:
        """Get all scheduled triggers."""
        return [t for t in self._triggers if isinstance(t, ScheduledTrigger)]
