"""Abstract base class for LLM adapters.

Every LLM provider (Ollama/Gemma, Anthropic/Claude, etc.) implements
this interface. Swap providers via the LLM_PROVIDER env var.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator


class LLMAdapter(ABC):
    """Interface that all LLM providers must implement."""

    @abstractmethod
    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> str:
        """Send a chat request and return the complete response."""

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        """Send a chat request and yield response tokens as they arrive."""

    @abstractmethod
    async def chat_with_image(
        self,
        messages: list[dict[str, str]],
        image_path: str,
        temperature: float = 0.3,
    ) -> str:
        """Send a chat request with an attached image (requires vision support)."""

    @property
    @abstractmethod
    def supports_vision(self) -> bool:
        """Whether this adapter can process images."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name for logs/debug."""
