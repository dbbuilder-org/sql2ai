"""Configuration management for SQL2.AI CLI."""

import os
from pathlib import Path
from typing import Optional

import keyring
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path.home() / ".sql2ai"
CONFIG_FILE = CONFIG_DIR / "config.toml"
LOCAL_CONFIG_FILE = Path(".sql2ai.toml")
KEYRING_SERVICE = "sql2ai"


class Config(BaseSettings):
    """SQL2.AI CLI configuration."""

    model_config = SettingsConfigDict(
        env_prefix="SQL2AI_",
        env_file=".env",
        extra="ignore",
    )

    api_url: str = Field(default="https://api.sql2.ai")
    default_database: str = Field(default="postgresql")
    output_format: str = Field(default="rich")  # rich, json, plain
    color: bool = Field(default=True)


def get_config_dir() -> Path:
    """Get or create the config directory."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def get_config() -> Config:
    """Load configuration from environment and files."""
    return Config()


def create_config_file() -> Path:
    """Create a local configuration file."""
    config_content = """# SQL2.AI Configuration
# https://sql2.ai/docs/cli

[settings]
# API URL (default: https://api.sql2.ai)
# api_url = "https://api.sql2.ai"

# Default database type: postgresql, sqlserver
default_database = "postgresql"

# Output format: rich, json, plain
output_format = "rich"

[connections]
# Database connections can be added with:
#   sql2ai connections add
#
# Or manually configured here:
# [connections.mydb]
# name = "My Database"
# type = "postgresql"
# host = "localhost"
# port = 5432
# database = "mydb"
# username = "user"
# # Password stored securely in system keyring
"""

    LOCAL_CONFIG_FILE.write_text(config_content)
    return LOCAL_CONFIG_FILE


def get_api_key() -> Optional[str]:
    """Get API key from keyring or environment."""
    # Check environment first
    key = os.environ.get("SQL2AI_API_KEY")
    if key:
        return key

    # Try keyring
    try:
        return keyring.get_password(KEYRING_SERVICE, "api_key")
    except Exception:
        return None


def save_api_key(api_key: str) -> None:
    """Save API key to system keyring."""
    keyring.set_password(KEYRING_SERVICE, "api_key", api_key)


def delete_api_key() -> None:
    """Delete API key from system keyring."""
    try:
        keyring.delete_password(KEYRING_SERVICE, "api_key")
    except keyring.errors.PasswordDeleteError:
        pass


def get_connection_password(connection_name: str) -> Optional[str]:
    """Get connection password from keyring."""
    try:
        return keyring.get_password(KEYRING_SERVICE, f"conn:{connection_name}")
    except Exception:
        return None


def save_connection_password(connection_name: str, password: str) -> None:
    """Save connection password to keyring."""
    keyring.set_password(KEYRING_SERVICE, f"conn:{connection_name}", password)
