"""Prompt executor that integrates prompts with AI service and tracking."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
import time
import structlog

from sql2ai_shared.constants import AIModel
from sql2ai_shared.prompts.base import (
    Prompt,
    PromptExecution,
    prompt_registry,
)

logger = structlog.get_logger()


@dataclass
class ExecutionConfig:
    """Configuration for prompt execution."""

    model: Optional[AIModel] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout_seconds: int = 60
    retry_count: int = 2
    track_execution: bool = True
    store_response: bool = True


class PromptExecutor:
    """Executes prompts with tracking, retry logic, and AI service integration.

    Usage:
        executor = PromptExecutor(ai_service)

        # Execute a prompt
        result = await executor.execute(
            QueryGenerationPrompt(
                request="Get all active customers",
                dialect=DatabaseDialect.SQLSERVER,
                schema_context="...",
            )
        )

        # Access execution metrics
        print(result.execution.latency_ms)
        print(result.execution.prompt_hash)
    """

    def __init__(
        self,
        ai_service: Any,  # AIService from integrations
        default_config: Optional[ExecutionConfig] = None,
    ):
        self.ai_service = ai_service
        self.default_config = default_config or ExecutionConfig()
        self._execution_callbacks: List[callable] = []

    def on_execution(self, callback: callable) -> None:
        """Register a callback to be called after each execution."""
        self._execution_callbacks.append(callback)

    async def execute(
        self,
        prompt: Prompt,
        config: Optional[ExecutionConfig] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionResult":
        """Execute a prompt and return the result with tracking."""
        cfg = config or self.default_config
        context = context or {}

        # Get prompt metadata for model selection
        metadata = prompt.get_metadata()

        # Determine model to use (priority: config > prompt > default)
        model = cfg.model or metadata.recommended_model or AIModel.GPT4
        temperature = cfg.temperature if cfg.temperature is not None else metadata.temperature
        max_tokens = cfg.max_tokens or metadata.max_tokens

        # Create execution record
        execution = prompt.create_execution()
        execution.tenant_id = context.get("tenant_id")
        execution.user_id = context.get("user_id")
        execution.request_id = context.get("request_id")

        start_time = time.time()
        response_text = ""
        error = None

        try:
            # Get messages from prompt
            messages = prompt.get_messages()

            # Convert to AI service format
            from sql2ai_shared.integrations.ai import Message
            ai_messages = [
                Message(role=m["role"], content=m["content"])
                for m in messages
            ]

            # Execute with AI service
            response = await self.ai_service.complete(
                messages=ai_messages,
                model=model.value if isinstance(model, AIModel) else model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            response_text = response.content
            latency_ms = (time.time() - start_time) * 1000

            # Record response
            prompt.record_response(
                response=response_text,
                model=response.model,
                input_tokens=response.usage.get("prompt_tokens", 0) if response.usage else 0,
                output_tokens=response.usage.get("completion_tokens", 0) if response.usage else 0,
                latency_ms=latency_ms,
            )

        except Exception as e:
            error = str(e)
            latency_ms = (time.time() - start_time) * 1000

            prompt.record_response(
                response="",
                model=model.value if isinstance(model, AIModel) else str(model),
                latency_ms=latency_ms,
                error=error,
            )

            logger.error(
                "prompt_execution_failed",
                prompt_id=prompt.id,
                prompt_version=prompt.version,
                error=error,
            )

        # Get final execution record
        execution = prompt._execution

        # Track in registry
        if cfg.track_execution:
            prompt_registry.record_execution(execution)

        # Notify callbacks
        for callback in self._execution_callbacks:
            try:
                callback(execution)
            except Exception as e:
                logger.warning("execution_callback_failed", error=str(e))

        # Log execution
        logger.info(
            "prompt_executed",
            prompt_id=prompt.id,
            prompt_version=prompt.version,
            prompt_hash=prompt.hash,
            model=execution.model_used,
            latency_ms=execution.latency_ms,
            success=execution.success,
        )

        return ExecutionResult(
            content=response_text,
            execution=execution,
            error=error,
        )

    async def execute_with_retry(
        self,
        prompt: Prompt,
        config: Optional[ExecutionConfig] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "ExecutionResult":
        """Execute with retry logic for transient failures."""
        cfg = config or self.default_config
        last_error = None

        for attempt in range(cfg.retry_count + 1):
            result = await self.execute(prompt, config, context)

            if result.success:
                return result

            last_error = result.error
            logger.warning(
                "prompt_execution_retry",
                prompt_id=prompt.id,
                attempt=attempt + 1,
                error=last_error,
            )

            # Exponential backoff
            if attempt < cfg.retry_count:
                import asyncio
                await asyncio.sleep(2 ** attempt)

        return result

    async def execute_batch(
        self,
        prompts: List[Prompt],
        config: Optional[ExecutionConfig] = None,
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = False,
    ) -> List["ExecutionResult"]:
        """Execute multiple prompts, optionally in parallel."""
        if parallel:
            import asyncio
            tasks = [
                self.execute(prompt, config, context)
                for prompt in prompts
            ]
            return await asyncio.gather(*tasks)
        else:
            results = []
            for prompt in prompts:
                result = await self.execute(prompt, config, context)
                results.append(result)
            return results


@dataclass
class ExecutionResult:
    """Result of a prompt execution."""

    content: str
    execution: PromptExecution
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and self.execution.success

    @property
    def prompt_id(self) -> str:
        return self.execution.prompt_id

    @property
    def prompt_version(self) -> str:
        return self.execution.prompt_version

    @property
    def prompt_hash(self) -> str:
        return self.execution.prompt_hash

    @property
    def latency_ms(self) -> float:
        return self.execution.latency_ms

    @property
    def tokens_used(self) -> int:
        return self.execution.input_tokens + self.execution.output_tokens

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "content": self.content,
            "success": self.success,
            "error": self.error,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "prompt_hash": self.prompt_hash,
            "latency_ms": self.latency_ms,
            "tokens_used": self.tokens_used,
            "model": self.execution.model_used,
        }


class PromptExecutionLogger:
    """Logs prompt executions to various backends for analysis."""

    def __init__(self):
        self._backends: List[callable] = []

    def add_backend(self, backend: callable) -> None:
        """Add a logging backend."""
        self._backends.append(backend)

    async def log(self, execution: PromptExecution) -> None:
        """Log execution to all backends."""
        for backend in self._backends:
            try:
                await backend(execution)
            except Exception as e:
                logger.warning(
                    "execution_logging_failed",
                    backend=backend.__name__,
                    error=str(e),
                )

    @staticmethod
    async def database_backend(execution: PromptExecution) -> None:
        """Log to database (placeholder - implement with actual DB)."""
        # Would insert execution record into prompt_executions table
        pass

    @staticmethod
    async def posthog_backend(execution: PromptExecution) -> None:
        """Log to PostHog for analytics."""
        # Would call PostHog track event
        pass

    @staticmethod
    async def file_backend(execution: PromptExecution) -> None:
        """Log to file for debugging."""
        import json
        with open("prompt_executions.jsonl", "a") as f:
            f.write(json.dumps(execution.to_dict()) + "\n")


class ABTestManager:
    """Manages A/B testing for prompt variations."""

    def __init__(self):
        self._experiments: Dict[str, "ABExperiment"] = {}

    def create_experiment(
        self,
        name: str,
        control: Type[Prompt],
        variants: Dict[str, Type[Prompt]],
        traffic_split: Optional[Dict[str, float]] = None,
    ) -> "ABExperiment":
        """Create a new A/B experiment."""
        experiment = ABExperiment(
            name=name,
            control=control,
            variants=variants,
            traffic_split=traffic_split,
        )
        self._experiments[name] = experiment
        return experiment

    def get_experiment(self, name: str) -> Optional["ABExperiment"]:
        return self._experiments.get(name)

    def select_variant(
        self,
        experiment_name: str,
        user_id: str,
    ) -> Type[Prompt]:
        """Select a variant for a user based on traffic split."""
        experiment = self._experiments.get(experiment_name)
        if not experiment:
            raise ValueError(f"Experiment not found: {experiment_name}")

        return experiment.select_variant(user_id)


@dataclass
class ABExperiment:
    """An A/B testing experiment for prompts."""

    name: str
    control: Type[Prompt]
    variants: Dict[str, Type[Prompt]]
    traffic_split: Optional[Dict[str, float]] = None
    started_at: datetime = None
    ended_at: Optional[datetime] = None

    def __post_init__(self):
        if self.started_at is None:
            self.started_at = datetime.utcnow()

        if self.traffic_split is None:
            # Equal split between control and variants
            total_variants = len(self.variants) + 1
            split = 1.0 / total_variants
            self.traffic_split = {"control": split}
            for variant_name in self.variants:
                self.traffic_split[variant_name] = split

    def select_variant(self, user_id: str) -> Type[Prompt]:
        """Select a variant based on user ID hash."""
        import hashlib

        # Hash user ID to get consistent assignment
        hash_value = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        bucket = (hash_value % 100) / 100.0

        cumulative = 0.0
        for variant_name, weight in self.traffic_split.items():
            cumulative += weight
            if bucket < cumulative:
                if variant_name == "control":
                    return self.control
                return self.variants[variant_name]

        return self.control

    def get_results(self) -> Dict[str, Any]:
        """Get experiment results from recorded executions."""
        control_stats = prompt_registry.get_prompt_stats(
            f"{self.control.__module__}.{self.control.__name__}"
        )

        variant_stats = {}
        for name, variant_class in self.variants.items():
            variant_stats[name] = prompt_registry.get_prompt_stats(
                f"{variant_class.__module__}.{variant_class.__name__}"
            )

        return {
            "experiment": self.name,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "control": control_stats,
            "variants": variant_stats,
        }
