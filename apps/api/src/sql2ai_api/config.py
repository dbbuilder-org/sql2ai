"""SQL2.AI API Configuration."""

from functools import lru_cache
from typing import List
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_prefix="SQL2AI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "SQL2.AI API"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    environment: str = "development"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://sql2.ai",
        "https://app.sql2.ai",
    ]

    # Database (Platform)
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sql2ai"
    database_pool_size: int = 10

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Authentication - JWT
    SECRET_KEY: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    refresh_token_expire_days: int = 7

    # Authentication - Clerk
    clerk_secret_key: SecretStr = Field(default=SecretStr(""))
    clerk_publishable_key: str = ""
    clerk_webhook_secret: SecretStr = Field(default=SecretStr(""))

    # Payments - Stripe
    stripe_secret_key: SecretStr = Field(default=SecretStr(""))
    stripe_publishable_key: str = ""
    stripe_webhook_secret: SecretStr = Field(default=SecretStr(""))

    # Email - Resend
    resend_api_key: SecretStr = Field(default=SecretStr(""))
    resend_from_email: str = "SQL2.AI <notifications@sql2.ai>"

    # Analytics - PostHog
    posthog_api_key: str = ""
    posthog_host: str = "https://app.posthog.com"

    # Error Tracking - Sentry
    sentry_dsn: str = ""
    sentry_traces_sample_rate: float = 0.1

    # Observability - Datadog
    datadog_api_key: str = ""
    datadog_service: str = "sql2ai-api"

    # AI - LLM Providers
    openai_api_key: SecretStr = Field(default=SecretStr(""))
    ANTHROPIC_API_KEY: str = ""
    azure_openai_api_key: SecretStr = Field(default=SecretStr(""))
    azure_openai_endpoint: str = ""

    # AI - Observability
    langsmith_api_key: str = ""
    langsmith_project: str = "sql2ai"
    helicone_api_key: str = ""

    # AI - Default settings
    default_llm_model: str = "gpt-4"
    default_embedding_model: str = "text-embedding-3-small"
    ai_max_tokens: int = 4000
    ai_temperature: float = 0.7

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 60

    # Feature Flags
    feature_ai_agents: bool = True
    feature_compliance_scanning: bool = True
    feature_real_time_monitoring: bool = True

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
