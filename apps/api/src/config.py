"""SQL2.AI API Configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Settings
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://sql2.ai",
        "https://app.sql2.ai",
    ]

    # Database
    DATABASE_URL: str = ""

    # Authentication
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # External Services
    ANTHROPIC_API_KEY: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
