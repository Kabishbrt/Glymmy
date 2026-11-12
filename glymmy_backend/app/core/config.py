"""Singleton configuration via Pydantic Settings + lru_cache.

Every adapter reads from this single source of truth. Swap providers
by changing environment variables — no code changes required.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    # Application
    APP_NAME: str = "Glymmy API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM provider: ollama_gemma | anthropic
    LLM_PROVIDER: str = "ollama_gemma"

    # Ollama (default) — Gemma 4 E4B: ~4.5B effective params, multimodal (text+vision),
    # 256K context, Apache 2.0, released April 2026.
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma4:latest"

    # Anthropic (production)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5"

    # Data providers
    CGM_PROVIDER: str = "glucobench"
    LABS_PROVIDER: str = "mimic"
    STORAGE_PROVIDER: str = "memory"

    # Dataset paths (relative to glymmy_backend/ directory)
    DATASET_DIR: str = "../notebooks/datasets"

    # Vector store (RAG)
    CHROMA_MODE: str = "embedded"  # embedded | server
    CHROMA_HOST: str = "http://localhost:8100"  # only used when CHROMA_MODE=server
    CHROMA_PERSIST_DIR: str = "./chroma_data"  # only used when CHROMA_MODE=embedded

    # Demo / single-user mode
    DEMO_MODE: bool = True  # skip auth, auto-resolve to first user
    AUTO_SEED: bool = True  # seed synthetic data on startup if storage is empty

    # Clerk Authentication (optional — leave empty for demo/no-auth mode)
    CLERK_SECRET_KEY: str = ""
    CLERK_JWT_ISSUER: str = ""

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, value: object) -> object:
        """Accept common environment labels in addition to strict booleans."""
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if normalized in {"0", "false", "no", "off", "release", "prod", "production"}:
                return False
        return value

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a singleton Settings instance.

    The lru_cache ensures this is instantiated exactly once per process.
    Import and call this anywhere: `settings = get_settings()`.
    """
    return Settings()
