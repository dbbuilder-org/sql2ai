"""AI/LLM integration using LiteLLM for multi-provider support."""

from typing import Any, AsyncIterator, Dict, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
from pydantic import BaseModel, SecretStr
import structlog

logger = structlog.get_logger()


class AIProvider(str, Enum):
    """Supported AI providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    AZURE = "azure"
    GOOGLE = "google"
    COHERE = "cohere"
    BEDROCK = "bedrock"
    LOCAL = "local"


class AIConfig(BaseModel):
    """AI/LLM configuration."""

    # Default model settings
    default_model: str = "gpt-4"
    fallback_models: List[str] = ["claude-3-sonnet-20240229", "gpt-3.5-turbo"]

    # Provider API keys
    openai_api_key: Optional[SecretStr] = None
    anthropic_api_key: Optional[SecretStr] = None
    azure_api_key: Optional[SecretStr] = None
    azure_api_base: Optional[str] = None
    azure_api_version: str = "2024-02-15-preview"
    google_api_key: Optional[SecretStr] = None
    cohere_api_key: Optional[SecretStr] = None

    # AWS Bedrock
    aws_access_key_id: Optional[SecretStr] = None
    aws_secret_access_key: Optional[SecretStr] = None
    aws_region: str = "us-east-1"

    # Local/Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Request settings
    timeout: int = 60
    max_retries: int = 3
    request_timeout: int = 120

    # Caching
    enable_cache: bool = True
    cache_ttl: int = 3600

    disabled: bool = False


@dataclass
class Message:
    """Chat message."""

    role: str  # system, user, assistant, function, tool
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    tool_call_id: Optional[str] = None


@dataclass
class AIResponse:
    """AI completion response."""

    content: str
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None
    tool_calls: Optional[List[Dict]] = None

    # Metadata
    provider: Optional[str] = None
    latency_ms: Optional[float] = None
    cached: bool = False


@dataclass
class StreamChunk:
    """Streaming response chunk."""

    content: str
    finish_reason: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None


class AIService:
    """LiteLLM-based AI service for SQL2.AI."""

    def __init__(self, config: AIConfig):
        self.config = config
        self._litellm = None
        self._initialized = False

        if not config.disabled:
            self._init_client()

    def _init_client(self):
        """Initialize LiteLLM."""
        try:
            import litellm

            # Set API keys
            if self.config.openai_api_key:
                litellm.openai_key = self.config.openai_api_key.get_secret_value()

            if self.config.anthropic_api_key:
                litellm.anthropic_key = self.config.anthropic_api_key.get_secret_value()

            if self.config.azure_api_key:
                litellm.azure_key = self.config.azure_api_key.get_secret_value()

            # Configure settings
            litellm.request_timeout = self.config.request_timeout
            litellm.num_retries = self.config.max_retries

            # Enable caching if configured
            if self.config.enable_cache:
                litellm.cache = litellm.Cache(
                    type="redis",
                    ttl=self.config.cache_ttl,
                )

            self._litellm = litellm
            self._initialized = True
            logger.info("litellm_initialized", default_model=self.config.default_model)

        except ImportError:
            logger.warning("litellm_not_installed")
        except Exception as e:
            logger.error("litellm_init_failed", error=str(e))

    async def complete(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        response_format: Optional[Dict] = None,
        stop: Optional[List[str]] = None,
        user: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AIResponse:
        """Complete a chat conversation."""
        if not self._litellm:
            raise RuntimeError("AI service not initialized")

        import time
        start_time = time.time()

        model = model or self.config.default_model

        # Convert messages to dict format
        message_dicts = []
        for msg in messages:
            m = {"role": msg.role, "content": msg.content}
            if msg.name:
                m["name"] = msg.name
            if msg.tool_calls:
                m["tool_calls"] = msg.tool_calls
            if msg.tool_call_id:
                m["tool_call_id"] = msg.tool_call_id
            message_dicts.append(m)

        try:
            kwargs = {
                "model": model,
                "messages": message_dicts,
                "temperature": temperature,
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if tools:
                kwargs["tools"] = tools
            if tool_choice:
                kwargs["tool_choice"] = tool_choice
            if response_format:
                kwargs["response_format"] = response_format
            if stop:
                kwargs["stop"] = stop
            if user:
                kwargs["user"] = user
            if metadata:
                kwargs["metadata"] = metadata

            response = await self._litellm.acompletion(**kwargs)

            latency_ms = (time.time() - start_time) * 1000

            choice = response.choices[0]

            return AIResponse(
                content=choice.message.content or "",
                model=response.model,
                finish_reason=choice.finish_reason,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
                tool_calls=[tc.model_dump() for tc in choice.message.tool_calls]
                if choice.message.tool_calls else None,
                latency_ms=latency_ms,
                cached=getattr(response, "_hidden_params", {}).get("cache_hit", False),
            )

        except Exception as e:
            logger.error(
                "ai_completion_failed",
                model=model,
                error=str(e),
            )
            # Try fallback models
            return await self._try_fallback(messages, temperature, max_tokens, e)

    async def _try_fallback(
        self,
        messages: List[Message],
        temperature: float,
        max_tokens: Optional[int],
        original_error: Exception,
    ) -> AIResponse:
        """Try fallback models on failure."""
        for fallback_model in self.config.fallback_models:
            try:
                logger.info("ai_trying_fallback", model=fallback_model)
                return await self.complete(
                    messages=messages,
                    model=fallback_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            except Exception as e:
                logger.warning(
                    "ai_fallback_failed",
                    model=fallback_model,
                    error=str(e),
                )
                continue

        raise original_error

    async def stream(
        self,
        messages: List[Message],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        stop: Optional[List[str]] = None,
    ) -> AsyncIterator[StreamChunk]:
        """Stream a chat completion."""
        if not self._litellm:
            raise RuntimeError("AI service not initialized")

        model = model or self.config.default_model

        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        try:
            kwargs = {
                "model": model,
                "messages": message_dicts,
                "temperature": temperature,
                "stream": True,
            }

            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            if tools:
                kwargs["tools"] = tools
            if stop:
                kwargs["stop"] = stop

            async for chunk in await self._litellm.acompletion(**kwargs):
                delta = chunk.choices[0].delta

                yield StreamChunk(
                    content=delta.content or "",
                    finish_reason=chunk.choices[0].finish_reason,
                    tool_calls=[tc.model_dump() for tc in delta.tool_calls]
                    if delta.tool_calls else None,
                )

        except Exception as e:
            logger.error("ai_stream_failed", model=model, error=str(e))
            raise

    async def embed(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
    ) -> List[List[float]]:
        """Generate embeddings for texts."""
        if not self._litellm:
            raise RuntimeError("AI service not initialized")

        try:
            response = await self._litellm.aembedding(
                model=model,
                input=texts,
            )

            return [item["embedding"] for item in response.data]

        except Exception as e:
            logger.error("ai_embedding_failed", model=model, error=str(e))
            raise

    def get_token_count(
        self,
        text: str,
        model: Optional[str] = None,
    ) -> int:
        """Count tokens in text."""
        if not self._litellm:
            return len(text) // 4  # Rough estimate

        try:
            return self._litellm.token_counter(
                model=model or self.config.default_model,
                text=text,
            )
        except Exception:
            return len(text) // 4

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a model."""
        if not self._litellm:
            return {}

        try:
            return self._litellm.get_model_info(model)
        except Exception:
            return {}


# SQL-specific AI utilities
class SQLAIHelper:
    """SQL-specific AI helper methods."""

    def __init__(self, ai_service: AIService):
        self.ai = ai_service

    async def generate_sql(
        self,
        natural_language: str,
        schema_context: str,
        dialect: str = "sqlserver",
        temperature: float = 0.3,
    ) -> str:
        """Generate SQL from natural language."""
        system_prompt = f"""You are an expert SQL developer. Generate {dialect.upper()} SQL based on the user's request.

Schema context:
{schema_context}

Rules:
- Generate only valid {dialect.upper()} syntax
- Use appropriate JOINs and indexes
- Include proper error handling where applicable
- Return only the SQL query, no explanations"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=natural_language),
        ]

        response = await self.ai.complete(
            messages=messages,
            temperature=temperature,
        )

        return response.content.strip()

    async def explain_sql(
        self,
        sql: str,
        dialect: str = "sqlserver",
    ) -> str:
        """Explain what a SQL query does."""
        system_prompt = f"""You are an expert SQL analyst. Explain what the following {dialect.upper()} query does in plain English.
Be concise but thorough. Mention any potential performance concerns."""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=sql),
        ]

        response = await self.ai.complete(
            messages=messages,
            temperature=0.5,
        )

        return response.content

    async def optimize_sql(
        self,
        sql: str,
        schema_context: str,
        execution_plan: Optional[str] = None,
        dialect: str = "sqlserver",
    ) -> Dict[str, Any]:
        """Suggest optimizations for a SQL query."""
        context = f"""Schema:
{schema_context}"""

        if execution_plan:
            context += f"""

Execution Plan:
{execution_plan}"""

        system_prompt = f"""You are an expert SQL performance tuner. Analyze the following {dialect.upper()} query and suggest optimizations.

{context}

Provide:
1. Specific optimization suggestions
2. Rewritten query if applicable
3. Index recommendations
4. Estimated improvement"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=sql),
        ]

        response = await self.ai.complete(
            messages=messages,
            temperature=0.3,
        )

        return {
            "suggestions": response.content,
            "model": response.model,
            "tokens_used": response.usage.get("total_tokens") if response.usage else None,
        }

    async def generate_stored_procedure(
        self,
        description: str,
        schema_context: str,
        dialect: str = "sqlserver",
        include_error_handling: bool = True,
        include_transactions: bool = True,
    ) -> str:
        """Generate a stored procedure from description."""
        options = []
        if include_error_handling:
            options.append("proper TRY/CATCH error handling")
        if include_transactions:
            options.append("transaction management")

        options_text = ", ".join(options) if options else "standard implementation"

        system_prompt = f"""You are an expert database developer. Create a {dialect.upper()} stored procedure based on the requirements.

Schema context:
{schema_context}

Requirements:
- Include {options_text}
- Follow best practices for {dialect.upper()}
- Add appropriate comments
- Use meaningful parameter and variable names
- Return appropriate status codes"""

        messages = [
            Message(role="system", content=system_prompt),
            Message(role="user", content=description),
        ]

        response = await self.ai.complete(
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
        )

        return response.content
