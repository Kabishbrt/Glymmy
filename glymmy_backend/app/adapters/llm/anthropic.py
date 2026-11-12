"""Anthropic Claude LLM adapter (production option)."""

from __future__ import annotations

import base64
from collections.abc import AsyncIterator
from pathlib import Path

from anthropic import AsyncAnthropic
from loguru import logger

from app.adapters.llm.base import LLMAdapter
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError, LLMProviderError


class AnthropicAdapter(LLMAdapter):
    """Claude via Anthropic SDK."""

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.ANTHROPIC_API_KEY:
            raise ConfigurationError(
                "ANTHROPIC_API_KEY not set but LLM_PROVIDER=anthropic"
            )
        self._model = settings.ANTHROPIC_MODEL
        self._client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        logger.info(f"AnthropicAdapter initialized | model={self._model}")

    @property
    def supports_vision(self) -> bool:
        return True

    @property
    def provider_name(self) -> str:
        return f"anthropic:{self._model}"

    def _split_system(
        self, messages: list[dict[str, str]]
    ) -> tuple[str, list[dict[str, str]]]:
        system = ""
        rest: list[dict[str, str]] = []
        for m in messages:
            if m.get("role") == "system":
                system = m.get("content", "")
            else:
                rest.append(m)
        return system, rest

    async def chat(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> str:
        system, rest = self._split_system(messages)
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                temperature=temperature,
                system=system,
                messages=rest,
            )
            return response.content[0].text
        except Exception as exc:
            logger.error(f"Anthropic chat failed: {exc}")
            raise LLMProviderError(f"Anthropic request failed: {exc}") from exc

    async def chat_stream(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        system, rest = self._split_system(messages)
        try:
            async with self._client.messages.stream(
                model=self._model,
                max_tokens=2048,
                temperature=temperature,
                system=system,
                messages=rest,
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as exc:
            logger.error(f"Anthropic stream failed: {exc}")
            raise LLMProviderError(f"Anthropic stream failed: {exc}") from exc

    async def chat_with_image(
        self,
        messages: list[dict[str, str]],
        image_path: str,
        temperature: float = 0.3,
    ) -> str:
        system, rest = self._split_system(messages)
        if not rest:
            raise LLMProviderError("Empty messages for chat_with_image")

        image_bytes = Path(image_path).read_bytes()
        b64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        suffix = Path(image_path).suffix.lower().lstrip(".")
        media_type = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "webp": "image/webp",
        }.get(suffix, "image/jpeg")

        last_user = rest[-1]
        content_blocks = [
            {
                "type": "image",
                "source": {"type": "base64", "media_type": media_type, "data": b64},
            },
            {"type": "text", "text": last_user.get("content", "")},
        ]
        anthropic_messages = rest[:-1] + [{"role": "user", "content": content_blocks}]

        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=2048,
                temperature=temperature,
                system=system,
                messages=anthropic_messages,
            )
            return response.content[0].text
        except Exception as exc:
            logger.error(f"Anthropic vision failed: {exc}")
            raise LLMProviderError(f"Anthropic vision request failed: {exc}") from exc
