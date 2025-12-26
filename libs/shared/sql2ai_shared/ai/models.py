"""AI request and response models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from ulid import ULID


class MessageRole(str, Enum):
    """Message role in a conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A message in a conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List["ToolCall"]] = None

    @classmethod
    def system(cls, content: str) -> "Message":
        return cls(role=MessageRole.SYSTEM, content=content)

    @classmethod
    def user(cls, content: str) -> "Message":
        return cls(role=MessageRole.USER, content=content)

    @classmethod
    def assistant(cls, content: str) -> "Message":
        return cls(role=MessageRole.ASSISTANT, content=content)

    @classmethod
    def tool(cls, content: str, tool_call_id: str, name: str) -> "Message":
        return cls(
            role=MessageRole.TOOL,
            content=content,
            tool_call_id=tool_call_id,
            name=name,
        )


class ToolFunction(BaseModel):
    """Function definition for a tool."""

    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Tool(BaseModel):
    """Tool definition for function calling."""

    type: str = "function"
    function: ToolFunction


class ToolCall(BaseModel):
    """A tool call made by the model."""

    id: str
    type: str = "function"
    function: Dict[str, Any]

    @property
    def name(self) -> str:
        return self.function.get("name", "")

    @property
    def arguments(self) -> str:
        return self.function.get("arguments", "{}")


class ToolResult(BaseModel):
    """Result of a tool call execution."""

    tool_call_id: str
    name: str
    result: Any
    error: Optional[str] = None
    execution_time_ms: float = 0


class ChatRequest(BaseModel):
    """Request for chat completion."""

    messages: List[Message]
    model: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    stream: bool = False
    user: Optional[str] = None

    # SQL2.AI specific
    request_id: str = Field(default_factory=lambda: str(ULID()))
    tenant_id: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class UsageStats(BaseModel):
    """Token usage statistics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Choice(BaseModel):
    """A completion choice."""

    index: int = 0
    message: Message
    finish_reason: str = "stop"


class ChatResponse(BaseModel):
    """Response from chat completion."""

    id: str = Field(default_factory=lambda: str(ULID()))
    model: str
    choices: List[Choice]
    usage: UsageStats = Field(default_factory=UsageStats)
    created: datetime = Field(default_factory=datetime.utcnow)

    # Metadata
    request_id: Optional[str] = None
    latency_ms: float = 0
    provider: str = "unknown"

    @property
    def content(self) -> str:
        """Get the content of the first choice."""
        if self.choices:
            return self.choices[0].message.content
        return ""

    @property
    def tool_calls(self) -> Optional[List[ToolCall]]:
        """Get tool calls from the first choice."""
        if self.choices:
            return self.choices[0].message.tool_calls
        return None


class EmbeddingRequest(BaseModel):
    """Request for text embeddings."""

    input: Union[str, List[str]]
    model: Optional[str] = None
    encoding_format: str = "float"

    # SQL2.AI specific
    request_id: str = Field(default_factory=lambda: str(ULID()))
    tenant_id: Optional[str] = None


class Embedding(BaseModel):
    """A single embedding."""

    index: int
    embedding: List[float]
    object: str = "embedding"


class EmbeddingResponse(BaseModel):
    """Response from embedding request."""

    id: str = Field(default_factory=lambda: str(ULID()))
    model: str
    data: List[Embedding]
    usage: UsageStats = Field(default_factory=UsageStats)

    # Metadata
    request_id: Optional[str] = None
    latency_ms: float = 0


class StreamChunk(BaseModel):
    """A chunk in a streaming response."""

    id: str
    model: str
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None
    index: int = 0


# SQL-specific models
class SQLGenerationRequest(BaseModel):
    """Request for SQL generation."""

    prompt: str
    database_type: str  # sqlserver, postgresql
    schema_context: Optional[str] = None
    sample_data: Optional[Dict[str, Any]] = None
    max_tokens: int = 2000
    include_explanation: bool = True


class SQLGenerationResponse(BaseModel):
    """Response from SQL generation."""

    sql: str
    explanation: Optional[str] = None
    confidence: float = 0.0
    warnings: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)


class QueryOptimizationRequest(BaseModel):
    """Request for query optimization."""

    query: str
    database_type: str
    execution_plan: Optional[str] = None
    table_stats: Optional[Dict[str, Any]] = None


class QueryOptimizationResponse(BaseModel):
    """Response from query optimization."""

    optimized_query: str
    improvements: List[str]
    estimated_speedup: Optional[float] = None
    index_suggestions: List[str] = Field(default_factory=list)
    explanation: str = ""
