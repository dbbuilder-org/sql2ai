"""AI provider implementations with LiteLLM."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Dict, List, Optional, Union
import time
from pydantic import BaseModel, SecretStr
import structlog

from sql2ai_shared.ai.models import (
    ChatRequest,
    ChatResponse,
    Choice,
    EmbeddingRequest,
    EmbeddingResponse,
    Embedding,
    Message,
    MessageRole,
    StreamChunk,
    ToolCall,
    UsageStats,
)
from sql2ai_shared.tenancy.context import get_current_tenant
from sql2ai_shared.tenancy.limits import check_limit

logger = structlog.get_logger()


class AIConfig(BaseModel):
    """AI provider configuration."""

    # Provider settings
    default_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"
    fallback_models: List[str] = []

    # API keys (stored securely)
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    azure_api_key: Optional[SecretStr] = None
    azure_api_base: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"

    # Local model settings
    local_model_url: Optional[str] = None
    local_model_name: Optional[str] = None

    # Rate limiting
    max_requests_per_minute: int = 60
    max_tokens_per_minute: int = 100000

    # Caching
    cache_enabled: bool = True
    cache_ttl_seconds: int = 3600

    # Retry settings
    max_retries: int = 3
    retry_delay_seconds: float = 1.0

    # Observability
    log_requests: bool = True
    log_responses: bool = False
    trace_enabled: bool = True


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    def __init__(self, config: AIConfig):
        self.config = config

    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request."""
        pass

    @abstractmethod
    async def chat_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request."""
        pass

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings for text."""
        pass

    async def generate_sql(
        self,
        prompt: str,
        database_type: str,
        schema_context: Optional[str] = None,
    ) -> str:
        """Generate SQL from natural language."""
        system_prompt = f"""You are an expert {database_type} database developer.
Generate SQL queries based on user requests.
Only output valid {database_type} SQL syntax.
Do not include explanations unless asked."""

        if schema_context:
            system_prompt += f"\n\nDatabase Schema:\n{schema_context}"

        request = ChatRequest(
            messages=[
                Message.system(system_prompt),
                Message.user(prompt),
            ],
            model=self.config.default_model,
            temperature=0.2,
        )

        response = await self.chat(request)
        return response.content

    async def optimize_query(
        self,
        query: str,
        database_type: str,
        execution_plan: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Optimize a SQL query."""
        system_prompt = f"""You are an expert {database_type} query optimization specialist.
Analyze the provided query and suggest optimizations.
Return a JSON object with:
- optimized_query: the improved SQL
- improvements: list of improvements made
- index_suggestions: list of recommended indexes
- explanation: brief explanation of changes"""

        user_prompt = f"Query:\n{query}"
        if execution_plan:
            user_prompt += f"\n\nExecution Plan:\n{execution_plan}"

        request = ChatRequest(
            messages=[
                Message.system(system_prompt),
                Message.user(user_prompt),
            ],
            model=self.config.default_model,
            temperature=0.1,
        )

        response = await self.chat(request)

        # Parse JSON response
        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "optimized_query": query,
                "improvements": [],
                "explanation": response.content,
            }


class LiteLLMProvider(AIProvider):
    """LiteLLM-based provider supporting multiple AI backends."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        self._setup_litellm()

    def _setup_litellm(self) -> None:
        """Configure LiteLLM with API keys."""
        import litellm

        # Set API keys
        if self.config.openai_api_key:
            litellm.openai_key = self.config.openai_api_key.get_secret_value()

        if self.config.anthropic_api_key:
            litellm.anthropic_key = self.config.anthropic_api_key.get_secret_value()

        if self.config.azure_api_key:
            litellm.azure_key = self.config.azure_api_key.get_secret_value()

        # Configure caching
        if self.config.cache_enabled:
            litellm.cache = litellm.Cache(
                type="redis",
                ttl=self.config.cache_ttl_seconds,
            )

        # Configure retries
        litellm.num_retries = self.config.max_retries

        # Enable logging
        if self.config.log_requests:
            litellm.set_verbose = True

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion request via LiteLLM."""
        import litellm

        # Check tenant limits
        tenant = get_current_tenant()
        if tenant:
            check_limit(tenant.limits, "ai_requests_per_day")

        start_time = time.perf_counter()

        # Convert messages to LiteLLM format
        messages = [
            {"role": m.role.value, "content": m.content, "name": m.name}
            for m in request.messages
        ]

        # Prepare request kwargs
        kwargs = {
            "model": request.model or self.config.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "frequency_penalty": request.frequency_penalty,
            "presence_penalty": request.presence_penalty,
        }

        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens

        if request.stop:
            kwargs["stop"] = request.stop

        if request.tools:
            kwargs["tools"] = [t.model_dump() for t in request.tools]

        if request.tool_choice:
            kwargs["tool_choice"] = request.tool_choice

        # Add fallback models
        if self.config.fallback_models:
            kwargs["fallbacks"] = [
                {"model": m} for m in self.config.fallback_models
            ]

        try:
            # Make the request
            response = await litellm.acompletion(**kwargs)

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Parse tool calls if present
            tool_calls = None
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                tool_calls = [
                    ToolCall(
                        id=tc.id,
                        type=tc.type,
                        function={
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    )
                    for tc in response.choices[0].message.tool_calls
                ]

            # Build response
            chat_response = ChatResponse(
                id=response.id,
                model=response.model,
                choices=[
                    Choice(
                        index=c.index,
                        message=Message(
                            role=MessageRole(c.message.role),
                            content=c.message.content or "",
                            tool_calls=tool_calls,
                        ),
                        finish_reason=c.finish_reason or "stop",
                    )
                    for c in response.choices
                ],
                usage=UsageStats(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                ),
                request_id=request.request_id,
                latency_ms=latency_ms,
                provider="litellm",
            )

            # Log metrics
            logger.info(
                "ai_chat_completed",
                model=response.model,
                tokens=response.usage.total_tokens,
                latency_ms=latency_ms,
                request_id=request.request_id,
            )

            return chat_response

        except Exception as e:
            logger.error(
                "ai_chat_failed",
                model=request.model or self.config.default_model,
                error=str(e),
                request_id=request.request_id,
            )
            raise

    async def chat_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[StreamChunk]:
        """Send a streaming chat completion request."""
        import litellm

        messages = [
            {"role": m.role.value, "content": m.content}
            for m in request.messages
        ]

        kwargs = {
            "model": request.model or self.config.default_model,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }

        if request.max_tokens:
            kwargs["max_tokens"] = request.max_tokens

        response = await litellm.acompletion(**kwargs)

        async for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                yield StreamChunk(
                    id=chunk.id,
                    model=chunk.model,
                    delta={
                        "role": getattr(delta, "role", None),
                        "content": getattr(delta, "content", None),
                    },
                    finish_reason=chunk.choices[0].finish_reason,
                    index=chunk.choices[0].index,
                )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings using LiteLLM."""
        import litellm

        start_time = time.perf_counter()

        response = await litellm.aembedding(
            model=request.model or self.config.embedding_model,
            input=request.input,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000

        return EmbeddingResponse(
            model=response.model,
            data=[
                Embedding(
                    index=e["index"],
                    embedding=e["embedding"],
                )
                for e in response.data
            ],
            usage=UsageStats(
                prompt_tokens=response.usage.prompt_tokens,
                total_tokens=response.usage.total_tokens,
            ),
            request_id=request.request_id,
            latency_ms=latency_ms,
        )


class LocalModelProvider(AIProvider):
    """Provider for local models (Ollama, llama.cpp, etc.)."""

    def __init__(self, config: AIConfig):
        super().__init__(config)
        if not config.local_model_url:
            raise ValueError("local_model_url is required for LocalModelProvider")

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send a chat completion to a local model."""
        import httpx

        start_time = time.perf_counter()

        messages = [
            {"role": m.role.value, "content": m.content}
            for m in request.messages
        ]

        payload = {
            "model": request.model or self.config.local_model_name,
            "messages": messages,
            "temperature": request.temperature,
            "stream": False,
        }

        if request.max_tokens:
            payload["max_tokens"] = request.max_tokens

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.local_model_url}/v1/chat/completions",
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        return ChatResponse(
            id=data.get("id", request.request_id),
            model=data.get("model", self.config.local_model_name),
            choices=[
                Choice(
                    index=c["index"],
                    message=Message(
                        role=MessageRole(c["message"]["role"]),
                        content=c["message"]["content"],
                    ),
                    finish_reason=c.get("finish_reason", "stop"),
                )
                for c in data.get("choices", [])
            ],
            usage=UsageStats(
                prompt_tokens=data.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=data.get("usage", {}).get("completion_tokens", 0),
                total_tokens=data.get("usage", {}).get("total_tokens", 0),
            ),
            request_id=request.request_id,
            latency_ms=latency_ms,
            provider="local",
        )

    async def chat_stream(
        self, request: ChatRequest
    ) -> AsyncIterator[StreamChunk]:
        """Stream from a local model."""
        import httpx

        messages = [
            {"role": m.role.value, "content": m.content}
            for m in request.messages
        ]

        payload = {
            "model": request.model or self.config.local_model_name,
            "messages": messages,
            "temperature": request.temperature,
            "stream": True,
        }

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.config.local_model_url}/v1/chat/completions",
                json=payload,
                timeout=120.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break

                        import json
                        chunk = json.loads(data)
                        if chunk.get("choices"):
                            delta = chunk["choices"][0].get("delta", {})
                            yield StreamChunk(
                                id=chunk.get("id", ""),
                                model=chunk.get("model", ""),
                                delta=delta,
                                finish_reason=chunk["choices"][0].get("finish_reason"),
                            )

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings from local model."""
        import httpx

        start_time = time.perf_counter()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.config.local_model_url}/v1/embeddings",
                json={
                    "model": request.model or self.config.embedding_model,
                    "input": request.input,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.perf_counter() - start_time) * 1000

        return EmbeddingResponse(
            model=data.get("model", ""),
            data=[
                Embedding(
                    index=e["index"],
                    embedding=e["embedding"],
                )
                for e in data.get("data", [])
            ],
            request_id=request.request_id,
            latency_ms=latency_ms,
        )


# Global provider instance
_ai_provider: Optional[AIProvider] = None


def get_ai_provider() -> AIProvider:
    """Get the global AI provider."""
    global _ai_provider
    if _ai_provider is None:
        raise RuntimeError("AI provider not initialized")
    return _ai_provider


def create_ai_provider(config: AIConfig) -> AIProvider:
    """Create and set the global AI provider."""
    global _ai_provider

    if config.local_model_url:
        _ai_provider = LocalModelProvider(config)
    else:
        _ai_provider = LiteLLMProvider(config)

    logger.info(
        "ai_provider_initialized",
        provider=type(_ai_provider).__name__,
        default_model=config.default_model,
    )

    return _ai_provider
