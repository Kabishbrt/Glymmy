"""In-memory storage adapter — fine for MVP/demos."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from loguru import logger

from app.adapters.storage.base import StorageAdapter


class MemoryStorageAdapter(StorageAdapter):
    """Keeps everything in RAM; files go to a temp dir on disk."""

    def __init__(self) -> None:
        self._profiles: dict[str, dict[str, Any]] = {}
        self._chats: dict[str, list[dict[str, Any]]] = {}
        self._users: dict[str, dict[str, Any]] = {}
        self._devices: dict[str, dict[str, Any]] = {}
        self._readings: dict[str, list[dict[str, Any]]] = {}  # device_id → readings
        self._uploads_dir = Path("./uploads")
        self._uploads_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"MemoryStorageAdapter ready | uploads={self._uploads_dir}")

    @property
    def provider_name(self) -> str:
        return "memory"

    # ── Profiles & chat (legacy) ──────────────────────────────────────────────

    def save_profile(self, patient_id: str, profile: dict[str, Any]) -> None:
        self._profiles[patient_id] = profile

    def load_profile(self, patient_id: str) -> dict[str, Any] | None:
        return self._profiles.get(patient_id)

    def save_chat_message(self, patient_id: str, message: dict[str, Any]) -> None:
        self._chats.setdefault(patient_id, []).append(message)

    def load_chat_history(self, patient_id: str) -> list[dict[str, Any]]:
        return list(self._chats.get(patient_id, []))

    def save_upload(self, name: str, content: bytes) -> str:
        ext = Path(name).suffix or ".bin"
        path = self._uploads_dir / f"{uuid4().hex}{ext}"
        path.write_bytes(content)
        return str(path)

    # ── Users ─────────────────────────────────────────────────────────────────

    def save_user(self, user: dict[str, Any]) -> None:
        self._users[user["id"]] = user

    def load_user(self, user_id: str) -> dict[str, Any] | None:
        return self._users.get(user_id)

    def list_users(self) -> list[dict[str, Any]]:
        return list(self._users.values())

    def delete_user(self, user_id: str) -> bool:
        if user_id not in self._users:
            return False
        del self._users[user_id]
        # Cascade: remove devices and their readings
        device_ids = [d["id"] for d in self._devices.values() if d["user_id"] == user_id]
        for did in device_ids:
            self._devices.pop(did, None)
            self._readings.pop(did, None)
        return True

    # ── Devices ───────────────────────────────────────────────────────────────

    def save_device(self, device: dict[str, Any]) -> None:
        self._devices[device["id"]] = device

    def load_device(self, device_id: str) -> dict[str, Any] | None:
        return self._devices.get(device_id)

    def list_devices(self, user_id: str) -> list[dict[str, Any]]:
        return [d for d in self._devices.values() if d["user_id"] == user_id]

    # ── Readings ──────────────────────────────────────────────────────────────

    def save_readings(self, device_id: str, readings: list[dict[str, Any]]) -> int:
        self._readings.setdefault(device_id, []).extend(readings)
        return len(readings)

    def load_readings(
        self,
        device_id: str,
        start: str | None = None,
        end: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        data = self._readings.get(device_id, [])
        if start:
            data = [r for r in data if r["timestamp"] >= start]
        if end:
            data = [r for r in data if r["timestamp"] <= end]
        data = sorted(data, key=lambda r: r["timestamp"])
        if limit:
            data = data[-limit:]  # most recent
        return data
