"""LLM adapter factory — reads config and returns the right adapter."""

from __future__ import annotations

from functools import lru_cache

from loguru import logger

from app.adapters.llm.base import LLMAdapter
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_llm_adapter() -> LLMAdapter:
    """Return the configured LLM adapter as a singleton."""
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()

    if provider == "ollama_gemma":
        from app.adapters.llm.ollama_gemma import OllamaGemmaAdapter

        adapter: LLMAdapter = OllamaGemmaAdapter()
    elif provider == "anthropic":
        from app.adapters.llm.anthropic import AnthropicAdapter

        adapter = AnthropicAdapter()
    else:
        raise ConfigurationError(
            f"Unknown LLM_PROVIDER={provider!r}. "
            "Valid options: ollama_gemma, anthropic"
        )

    logger.info(f"LLM adapter resolved: {adapter.provider_name}")
    return adapter
