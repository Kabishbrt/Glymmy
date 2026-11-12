"""Storage adapter interface — for chat history, uploaded files, profiles, users & devices."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class StorageAdapter(ABC):
    """Persistence layer for patient profiles, chat history, uploaded files, users & devices."""

    # ── Legacy (patient profiles, chat, uploads) ──────────────────────────────

    @abstractmethod
    def save_profile(self, patient_id: str, profile: dict[str, Any]) -> None: ...

    @abstractmethod
    def load_profile(self, patient_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def save_chat_message(self, patient_id: str, message: dict[str, Any]) -> None: ...

    @abstractmethod
    def load_chat_history(self, patient_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def save_upload(self, name: str, content: bytes) -> str:
        """Save a binary upload and return its path."""

    # ── Users & devices ───────────────────────────────────────────────────────

    @abstractmethod
    def save_user(self, user: dict[str, Any]) -> None: ...

    @abstractmethod
    def load_user(self, user_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def list_users(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def delete_user(self, user_id: str) -> bool: ...

    @abstractmethod
    def save_device(self, device: dict[str, Any]) -> None: ...

    @abstractmethod
    def load_device(self, device_id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def list_devices(self, user_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    def save_readings(self, device_id: str, readings: list[dict[str, Any]]) -> int: ...

    @abstractmethod
    def load_readings(
        self,
        device_id: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]: ...

    @property
    @abstractmethod
    def provider_name(self) -> str: ...
