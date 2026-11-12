"""Gemma via Ollama — local, multimodal LLM adapter.

Default model is Gemma 4 E4B (released April 2026):
- Multimodal (text + vision in one model)
- 256K context window
- Apache 2.0 license (fully permissive)
- ~4.5B effective parameters (runs on a laptop)
- Replaces the vision (moondream) + text (qwen) pair from the POCs.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import ollama
from loguru import logger

from app.adapters.llm.base import LLMAdapter
from app.core.config import get_settings
from app.core.exceptions import LLMProviderError


class OllamaGemmaAdapter(LLMAdapter):
    """Gemma 3 via Ollama."""

    def __init__(self) -> None:
        settings = get_settings()
        self._host = settings.OLLAMA_HOST
        self._model = settings.OLLAMA_MODEL
        self._client = ollama.AsyncClient(host=self._host)
        logger.info(
            f"OllamaGemmaAdapter initialized | host={self._host} model={self._model}"
        )

    @property
    def supports_vision(self) -> bool:
        return True

    @property
    def provider_name(self) -> str:
        return f"ollama:{self._model}"

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> str:
        try:
            response = await self._client.chat(
                model=self._model,
                messages=messages,
                options={"temperature": temperature},
            )
            return response["message"]["content"]
        except Exception as exc:
            logger.error(f"Ollama chat failed: {exc}")
            raise LLMProviderError(f"Ollama request failed: {exc}") from exc

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        try:
            stream = await self._client.chat(
                model=self._model,
                messages=messages,
                options={"temperature": temperature},
                stream=True,
            )
            async for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        except Exception as exc:
            logger.error(f"Ollama stream failed: {exc}")
            raise LLMProviderError(f"Ollama stream failed: {exc}") from exc

    async def chat_with_image(
        self,
        messages: list[dict[str, str]],
        image_path: str,
        temperature: float = 0.3,
    ) -> str:
        # Attach the image to the last user message
        if not messages:
            raise LLMProviderError("Empty messages for chat_with_image")
        last = messages[-1].copy()
        last["images"] = [image_path]
        all_messages = messages[:-1] + [last]
        try:
            response = await self._client.chat(
                model=self._model,
                messages=all_messages,
                options={"temperature": temperature},
            )
            return response["message"]["content"]
        except Exception as exc:
            logger.error(f"Ollama vision chat failed: {exc}")
            raise LLMProviderError(f"Ollama vision request failed: {exc}") from exc
