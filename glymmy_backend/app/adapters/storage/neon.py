"""Neon Postgres storage adapter — stub for future production use."""

from __future__ import annotations

from typing import Any

from app.adapters.storage.base import StorageAdapter


class NeonStorageAdapter(StorageAdapter):
    """Placeholder for Neon Postgres. Not implemented yet."""

    @property
    def provider_name(self) -> str:
        return "neon-postgres"

    def save_profile(self, patient_id: str, profile: dict[str, Any]) -> None:
        raise NotImplementedError("Neon adapter not implemented yet.")

    def load_profile(self, patient_id: str) -> dict[str, Any] | None:
        raise NotImplementedError("Neon adapter not implemented yet.")

    def save_chat_message(self, patient_id: str, message: dict[str, Any]) -> None:
        raise NotImplementedError("Neon adapter not implemented yet.")

    def load_chat_history(self, patient_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError("Neon adapter not implemented yet.")

    def save_upload(self, name: str, content: bytes) -> str:
        raise NotImplementedError("Neon adapter not implemented yet.")
