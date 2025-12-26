"""Base classes for versionable prompts with tracking."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Type, TypeVar
import hashlib
import json
from uuid import uuid4

from pydantic import BaseModel

from sql2ai_shared.constants import (
    DatabaseDialect,
    PromptCategory,
    PromptRole,
    AIModel,
)


class PromptVersion(BaseModel):
    """Version information for a prompt."""

    major: int = 1
    minor: int = 0
    patch: int = 0

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def bump_major(self) -> "PromptVersion":
        return PromptVersion(major=self.major + 1, minor=0, patch=0)

    def bump_minor(self) -> "PromptVersion":
        return PromptVersion(major=self.major, minor=self.minor + 1, patch=0)

    def bump_patch(self) -> "PromptVersion":
        return PromptVersion(major=self.major, minor=self.minor, patch=self.patch + 1)


class PromptMetadata(BaseModel):
    """Metadata for tracking and organizing prompts."""

    id: str = field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    category: PromptCategory
    role: PromptRole
    version: PromptVersion = PromptVersion()
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    author: Optional[str] = None
    tags: List[str] = []

    # Performance expectations
    expected_tokens: Optional[int] = None
    recommended_model: Optional[AIModel] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    class Config:
        use_enum_values = True


@dataclass
class PromptExecution:
    """Record of a prompt execution for tracking and evaluation."""

    execution_id: str = field(default_factory=lambda: str(uuid4()))
    prompt_id: str = ""
    prompt_version: str = ""
    prompt_hash: str = ""

    # Input
    rendered_prompt: str = ""
    variables: Dict[str, Any] = field(default_factory=dict)

    # Output
    response: str = ""
    model_used: str = ""

    # Metrics
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0

    # Evaluation
    success: bool = True
    error: Optional[str] = None
    feedback_score: Optional[float] = None  # 1-5 rating
    feedback_notes: Optional[str] = None

    # Timestamps
    executed_at: datetime = field(default_factory=datetime.utcnow)

    # Context
    tenant_id: Optional[str] = None
    user_id: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "execution_id": self.execution_id,
            "prompt_id": self.prompt_id,
            "prompt_version": self.prompt_version,
            "prompt_hash": self.prompt_hash,
            "rendered_prompt": self.rendered_prompt,
            "variables": self.variables,
            "response": self.response,
            "model_used": self.model_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "latency_ms": self.latency_ms,
            "success": self.success,
            "error": self.error,
            "feedback_score": self.feedback_score,
            "feedback_notes": self.feedback_notes,
            "executed_at": self.executed_at.isoformat(),
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "request_id": self.request_id,
        }


T = TypeVar("T", bound="Prompt")


class Prompt(ABC):
    """Base class for versionable prompts.

    All prompts should inherit from this class to enable:
    - Version tracking
    - Content hashing for change detection
    - Execution logging
    - A/B testing support
    """

    # Class-level metadata
    _name: str = "base_prompt"
    _description: str = "Base prompt class"
    _category: PromptCategory = PromptCategory.QUERY_GENERATION
    _role: PromptRole = PromptRole.SQL_EXPERT
    _version: PromptVersion = PromptVersion()
    _tags: List[str] = []
    _recommended_model: Optional[AIModel] = None
    _temperature: float = 0.7
    _max_tokens: Optional[int] = None

    def __init__(self, **variables: Any):
        """Initialize prompt with variables for rendering."""
        self.variables = variables
        self._rendered: Optional[str] = None
        self._execution: Optional[PromptExecution] = None

    @property
    def id(self) -> str:
        """Unique identifier based on class name."""
        return f"{self.__class__.__module__}.{self.__class__.__name__}"

    @property
    def version(self) -> str:
        """Version string."""
        return str(self._version)

    @property
    def hash(self) -> str:
        """Content hash of the prompt template."""
        content = self.system_prompt + self.user_prompt_template
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    @property
    def full_id(self) -> str:
        """Full identifier including version and hash."""
        return f"{self.id}@{self.version}#{self.hash}"

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """The system prompt defining AI behavior."""
        pass

    @property
    @abstractmethod
    def user_prompt_template(self) -> str:
        """Template for the user prompt with {variable} placeholders."""
        pass

    def render(self) -> str:
        """Render the user prompt with variables."""
        if self._rendered is None:
            try:
                self._rendered = self.user_prompt_template.format(**self.variables)
            except KeyError as e:
                raise ValueError(f"Missing required variable: {e}")
        return self._rendered

    def get_messages(self) -> List[Dict[str, str]]:
        """Get the full message list for the AI model."""
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.render()},
        ]

    def create_execution(self) -> PromptExecution:
        """Create an execution record for tracking."""
        self._execution = PromptExecution(
            prompt_id=self.id,
            prompt_version=self.version,
            prompt_hash=self.hash,
            rendered_prompt=self.render(),
            variables=self.variables,
        )
        return self._execution

    def record_response(
        self,
        response: str,
        model: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: float = 0.0,
        error: Optional[str] = None,
    ) -> PromptExecution:
        """Record the response from the AI model."""
        if self._execution is None:
            self._execution = self.create_execution()

        self._execution.response = response
        self._execution.model_used = model
        self._execution.input_tokens = input_tokens
        self._execution.output_tokens = output_tokens
        self._execution.latency_ms = latency_ms
        self._execution.success = error is None
        self._execution.error = error

        return self._execution

    def get_metadata(self) -> PromptMetadata:
        """Get prompt metadata."""
        return PromptMetadata(
            id=self.id,
            name=self._name,
            description=self._description,
            category=self._category,
            role=self._role,
            version=self._version,
            tags=self._tags,
            recommended_model=self._recommended_model,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )

    @classmethod
    def with_variables(cls: Type[T], **variables: Any) -> T:
        """Factory method for creating prompt with variables."""
        return cls(**variables)


class PromptRegistry:
    """Registry for managing and tracking prompts.

    Provides:
    - Prompt registration and lookup
    - Version management
    - Execution history storage
    - A/B testing support
    """

    def __init__(self):
        self._prompts: Dict[str, Type[Prompt]] = {}
        self._executions: List[PromptExecution] = []
        self._execution_handlers: List[callable] = []

    def register(self, prompt_class: Type[Prompt]) -> Type[Prompt]:
        """Register a prompt class. Can be used as decorator."""
        prompt_id = f"{prompt_class.__module__}.{prompt_class.__name__}"
        self._prompts[prompt_id] = prompt_class
        return prompt_class

    def get(self, prompt_id: str) -> Optional[Type[Prompt]]:
        """Get a prompt class by ID."""
        return self._prompts.get(prompt_id)

    def list_prompts(self) -> List[Dict[str, Any]]:
        """List all registered prompts with metadata."""
        result = []
        for prompt_id, prompt_class in self._prompts.items():
            instance = prompt_class()
            metadata = instance.get_metadata()
            result.append({
                "id": prompt_id,
                "name": metadata.name,
                "description": metadata.description,
                "category": metadata.category,
                "role": metadata.role,
                "version": str(metadata.version),
                "hash": instance.hash,
            })
        return result

    def record_execution(self, execution: PromptExecution) -> None:
        """Record a prompt execution."""
        self._executions.append(execution)

        # Notify handlers
        for handler in self._execution_handlers:
            try:
                handler(execution)
            except Exception:
                pass  # Don't let handler errors break execution

    def on_execution(self, handler: callable) -> None:
        """Register a handler to be called on each execution."""
        self._execution_handlers.append(handler)

    def get_executions(
        self,
        prompt_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[PromptExecution]:
        """Get execution history, optionally filtered by prompt ID."""
        executions = self._executions
        if prompt_id:
            executions = [e for e in executions if e.prompt_id == prompt_id]
        return executions[-limit:]

    def get_prompt_stats(self, prompt_id: str) -> Dict[str, Any]:
        """Get statistics for a specific prompt."""
        executions = [e for e in self._executions if e.prompt_id == prompt_id]

        if not executions:
            return {"executions": 0}

        successful = [e for e in executions if e.success]
        with_feedback = [e for e in executions if e.feedback_score is not None]

        return {
            "executions": len(executions),
            "success_rate": len(successful) / len(executions) if executions else 0,
            "avg_latency_ms": sum(e.latency_ms for e in executions) / len(executions),
            "avg_input_tokens": sum(e.input_tokens for e in executions) / len(executions),
            "avg_output_tokens": sum(e.output_tokens for e in executions) / len(executions),
            "avg_feedback_score": (
                sum(e.feedback_score for e in with_feedback) / len(with_feedback)
                if with_feedback else None
            ),
            "models_used": list(set(e.model_used for e in executions if e.model_used)),
            "versions_used": list(set(e.prompt_version for e in executions)),
        }


# Global registry instance
prompt_registry = PromptRegistry()
