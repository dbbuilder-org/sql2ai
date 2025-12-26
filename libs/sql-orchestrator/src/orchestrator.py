"""Main SQL Orchestrator implementation."""

import asyncio
import uuid
from datetime import datetime
from typing import Any, Callable, Optional

import structlog

from checks import BaseCheck, CheckRegistry
from models import (
    CheckCategory,
    CheckExecution,
    CheckResult,
    CheckStatus,
    DatabaseHealth,
    OrchestratorConfig,
)
from triggers import (
    CheckTrigger,
    DeploymentTrigger,
    OnDemandTrigger,
    ScheduledTrigger,
    TriggerContext,
    TriggerManager,
    TriggerType,
)

logger = structlog.get_logger()


class SQLOrchestrator:
    """Unified monitoring, security auditing, and compliance checking."""

    def __init__(
        self,
        config: OrchestratorConfig,
        connection_provider: Callable[[str], Any],
        schema_snapshot_fn: Optional[Callable[[str], dict]] = None,
    ):
        """Initialize the orchestrator.

        Args:
            config: Orchestrator configuration
            connection_provider: Function to get database connection by connection_id
            schema_snapshot_fn: Optional function to capture schema snapshots
        """
        self.config = config
        self._connection_provider = connection_provider
        self._schema_snapshot_fn = schema_snapshot_fn
        self._registry = CheckRegistry()
        self._trigger_manager = TriggerManager()
        self._executions: dict[str, CheckExecution] = {}
        self._health_cache: dict[str, DatabaseHealth] = {}
        self._running = False
        self._scheduler_task: Optional[asyncio.Task] = None

    @property
    def registry(self) -> CheckRegistry:
        """Get the check registry."""
        return self._registry

    @property
    def triggers(self) -> TriggerManager:
        """Get the trigger manager."""
        return self._trigger_manager

    async def start(self):
        """Start the orchestrator scheduler."""
        if self._running:
            return

        self._running = True
        self._scheduler_task = asyncio.create_task(self._run_scheduler())
        logger.info("orchestrator_started", tenant_id=self.config.tenant_id)

    async def stop(self):
        """Stop the orchestrator scheduler."""
        self._running = False
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        logger.info("orchestrator_stopped", tenant_id=self.config.tenant_id)

    async def _run_scheduler(self):
        """Background scheduler for scheduled checks."""
        while self._running:
            try:
                # Check scheduled triggers
                scheduled = self._trigger_manager.get_scheduled_triggers()
                for trigger in scheduled:
                    context = {"current_time": datetime.utcnow()}
                    if trigger.should_trigger(context):
                        # TODO: Get connection IDs from config
                        # For now, log that we would run checks
                        logger.info(
                            "scheduled_trigger_fired",
                            checks=trigger.get_checks_to_run(),
                            next_run=trigger.get_next_run().isoformat(),
                        )
                        trigger.mark_run()

                # Sleep until next check (1 minute intervals)
                await asyncio.sleep(60)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("scheduler_error", error=str(e))
                await asyncio.sleep(60)

    async def run_checks(
        self,
        connection_id: str,
        check_ids: Optional[list[str]] = None,
        category: Optional[CheckCategory] = None,
        framework: Optional[str] = None,
        trigger_type: TriggerType = TriggerType.ON_DEMAND,
        trigger_source: Optional[str] = None,
        capture_before_snapshot: bool = False,
    ) -> CheckExecution:
        """Run checks against a database connection.

        Args:
            connection_id: ID of the database connection
            check_ids: Specific checks to run (None = all applicable)
            category: Filter by category
            framework: Filter by compliance framework
            trigger_type: Type of trigger that initiated the run
            trigger_source: Source identifier for the trigger
            capture_before_snapshot: Whether to capture schema before checks

        Returns:
            CheckExecution with results
        """
        execution = CheckExecution(
            id=str(uuid.uuid4()),
            tenant_id=self.config.tenant_id,
            connection_id=connection_id,
            trigger_type=trigger_type.value,
            trigger_source=trigger_source,
            status=CheckStatus.RUNNING,
        )

        self._executions[execution.id] = execution

        logger.info(
            "check_execution_started",
            execution_id=execution.id,
            connection_id=connection_id,
            trigger_type=trigger_type.value,
        )

        try:
            # Get connection
            connection = await self._connection_provider(connection_id)

            # Capture before snapshot if requested
            before_snapshot = None
            if capture_before_snapshot and self._schema_snapshot_fn:
                before_snapshot = await self._schema_snapshot_fn(connection_id)

            # Determine which checks to run
            checks = self._get_checks_to_run(check_ids, category, framework)

            # Run checks with concurrency limit
            semaphore = asyncio.Semaphore(self.config.max_concurrent_checks)
            tasks = [
                self._run_single_check(check, connection, semaphore, before_snapshot)
                for check in checks
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    execution.results.append(CheckResult(
                        check_id="ERROR",
                        check_name="Check Execution Error",
                        category=CheckCategory.CONFIGURATION,
                        severity=CheckSeverity.HIGH,
                        status=CheckStatus.ERROR,
                        message=str(result),
                    ))
                else:
                    execution.results.append(result)

            # Determine overall status
            if any(r.status == CheckStatus.ERROR for r in execution.results):
                execution.status = CheckStatus.ERROR
            elif any(r.status == CheckStatus.FAILED for r in execution.results):
                execution.status = CheckStatus.FAILED
            elif any(r.status == CheckStatus.WARNING for r in execution.results):
                execution.status = CheckStatus.WARNING
            else:
                execution.status = CheckStatus.PASSED

            execution.completed_at = datetime.utcnow()

            # Update health cache
            await self._update_health(connection_id, execution)

            # Send alerts if configured
            if self.config.alert_on_critical or self.config.alert_on_failure:
                await self._send_alerts(execution)

            logger.info(
                "check_execution_completed",
                execution_id=execution.id,
                status=execution.status.value,
                passed=execution.passed_count,
                failed=execution.failed_count,
                duration_ms=execution.duration_ms,
            )

        except Exception as e:
            execution.status = CheckStatus.ERROR
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
            logger.error(
                "check_execution_failed",
                execution_id=execution.id,
                error=str(e),
            )

        return execution

    def _get_checks_to_run(
        self,
        check_ids: Optional[list[str]],
        category: Optional[CheckCategory],
        framework: Optional[str],
    ) -> list[BaseCheck]:
        """Get list of checks to run based on filters."""
        if check_ids:
            # Specific checks requested
            checks = []
            for check_id in check_ids:
                if check_id in self.config.excluded_checks:
                    continue
                check = self._registry.get_check(check_id)
                if check:
                    checks.append(check)
            return checks

        if framework:
            # Get all checks for a framework
            checks = self._registry.get_checks_for_framework(framework)
            return [c for c in checks if c.id not in self.config.excluded_checks]

        # Get all checks, optionally filtered by category
        definitions = self._registry.list_checks(category=category)
        checks = []
        for defn in definitions:
            if defn.id in self.config.excluded_checks:
                continue
            check = self._registry.get_check(defn.id)
            if check:
                checks.append(check)

        return checks

    async def _run_single_check(
        self,
        check: BaseCheck,
        connection: Any,
        semaphore: asyncio.Semaphore,
        before_snapshot: Optional[dict] = None,
    ) -> CheckResult:
        """Run a single check with semaphore control."""
        async with semaphore:
            try:
                result = await asyncio.wait_for(
                    check.execute(connection),
                    timeout=self.config.check_timeout_seconds,
                )
                if before_snapshot:
                    result.before_snapshot = before_snapshot
                return result
            except asyncio.TimeoutError:
                return CheckResult(
                    check_id=check.id,
                    check_name=check.name,
                    category=check.category,
                    severity=check.severity,
                    status=CheckStatus.ERROR,
                    message=f"Check timed out after {self.config.check_timeout_seconds}s",
                )
            except Exception as e:
                return CheckResult(
                    check_id=check.id,
                    check_name=check.name,
                    category=check.category,
                    severity=check.severity,
                    status=CheckStatus.ERROR,
                    message=f"Check failed: {str(e)}",
                )

    async def _update_health(self, connection_id: str, execution: CheckExecution):
        """Update the health cache for a connection."""
        critical = [r for r in execution.results
                    if r.status == CheckStatus.FAILED and r.severity.value in ("critical", "high")]

        # Calculate scores by category
        perf_results = [r for r in execution.results if r.category == CheckCategory.PERFORMANCE]
        sec_results = [r for r in execution.results if r.category == CheckCategory.SECURITY]
        comp_results = [r for r in execution.results if r.category == CheckCategory.COMPLIANCE]

        def calc_score(results: list[CheckResult]) -> float:
            if not results:
                return 100.0
            passed = sum(1 for r in results if r.status == CheckStatus.PASSED)
            return (passed / len(results)) * 100

        health = DatabaseHealth(
            connection_id=connection_id,
            connection_name=connection_id,  # Would be looked up
            overall_status=execution.status,
            last_check=execution.completed_at or datetime.utcnow(),
            checks_passed=execution.passed_count,
            checks_failed=execution.failed_count,
            checks_warning=execution.warning_count,
            critical_issues=critical,
            performance_score=calc_score(perf_results),
            security_score=calc_score(sec_results),
            compliance_score=calc_score(comp_results),
        )

        self._health_cache[connection_id] = health

    async def _send_alerts(self, execution: CheckExecution):
        """Send alerts for critical or failed checks."""
        if not self.config.alert_webhook_url:
            return

        critical_results = [
            r for r in execution.results
            if (self.config.alert_on_critical and r.severity.value == "critical" and r.status == CheckStatus.FAILED)
            or (self.config.alert_on_failure and r.status == CheckStatus.FAILED)
        ]

        if not critical_results:
            return

        # TODO: Implement webhook notification
        logger.info(
            "alerts_would_be_sent",
            execution_id=execution.id,
            alert_count=len(critical_results),
            webhook_url=self.config.alert_webhook_url,
        )

    async def run_deployment_checks(
        self,
        connection_id: str,
        deployment_id: str,
        phase: str,  # "before" or "after"
    ) -> CheckExecution:
        """Run deployment-related checks.

        Args:
            connection_id: Database connection ID
            deployment_id: Unique deployment identifier
            phase: "before" or "after" deployment

        Returns:
            CheckExecution with results
        """
        deployment_triggers = self._trigger_manager.get_triggers_by_type(TriggerType.DEPLOYMENT)

        check_ids = set()
        for trigger in deployment_triggers:
            if isinstance(trigger, DeploymentTrigger):
                event = "deployment_started" if phase == "before" else "deployment_completed"
                if trigger.should_trigger({"event_type": event}):
                    check_ids.update(trigger.get_checks_to_run())

        return await self.run_checks(
            connection_id=connection_id,
            check_ids=list(check_ids) if check_ids else None,
            trigger_type=TriggerType.DEPLOYMENT,
            trigger_source=f"{deployment_id}:{phase}",
            capture_before_snapshot=(phase == "before"),
        )

    async def run_framework_audit(
        self,
        connection_id: str,
        framework: str,
    ) -> CheckExecution:
        """Run all checks for a compliance framework.

        Args:
            connection_id: Database connection ID
            framework: Compliance framework (e.g., "SOC2", "HIPAA")

        Returns:
            CheckExecution with results
        """
        return await self.run_checks(
            connection_id=connection_id,
            framework=framework,
            trigger_type=TriggerType.ON_DEMAND,
            trigger_source=f"framework_audit:{framework}",
        )

    def get_health(self, connection_id: str) -> Optional[DatabaseHealth]:
        """Get cached health status for a connection."""
        return self._health_cache.get(connection_id)

    def get_all_health(self) -> list[DatabaseHealth]:
        """Get health status for all monitored connections."""
        return list(self._health_cache.values())

    def get_execution(self, execution_id: str) -> Optional[CheckExecution]:
        """Get a specific check execution by ID."""
        return self._executions.get(execution_id)

    def get_recent_executions(
        self,
        connection_id: Optional[str] = None,
        limit: int = 10,
    ) -> list[CheckExecution]:
        """Get recent check executions."""
        executions = list(self._executions.values())

        if connection_id:
            executions = [e for e in executions if e.connection_id == connection_id]

        executions.sort(key=lambda e: e.started_at, reverse=True)
        return executions[:limit]

    def add_scheduled_check(
        self,
        cron_expression: str,
        check_ids: list[str],
        categories: Optional[list[CheckCategory]] = None,
    ) -> ScheduledTrigger:
        """Add a scheduled trigger for checks.

        Args:
            cron_expression: Cron expression for schedule
            check_ids: IDs of checks to run
            categories: Optional category filter

        Returns:
            The created ScheduledTrigger
        """
        trigger = ScheduledTrigger(cron_expression, check_ids, categories)
        self._trigger_manager.add_trigger(trigger)
        logger.info(
            "scheduled_trigger_added",
            cron=cron_expression,
            checks=check_ids,
            next_run=trigger.get_next_run().isoformat(),
        )
        return trigger

    def add_deployment_trigger(
        self,
        check_ids: Optional[list[str]] = None,
        run_before: bool = True,
        run_after: bool = True,
    ) -> DeploymentTrigger:
        """Add a deployment trigger.

        Args:
            check_ids: Specific checks to run (None = defaults)
            run_before: Run checks before deployment
            run_after: Run checks after deployment

        Returns:
            The created DeploymentTrigger
        """
        trigger = DeploymentTrigger(check_ids, run_before, run_after)
        self._trigger_manager.add_trigger(trigger)
        logger.info("deployment_trigger_added", checks=check_ids)
        return trigger


# Import CheckSeverity for the error result creation
from models import CheckSeverity
