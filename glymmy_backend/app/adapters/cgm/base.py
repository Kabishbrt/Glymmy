"""CGM data adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


class CGMAdapter(ABC):
    """Interface for CGM data providers (files, APIs, etc.)."""

    @abstractmethod
    def list_patients(self) -> list[dict[str, Any]]:
        """Return metadata for every available patient."""

    @abstractmethod
    def get_readings(
        self,
        patient_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return glucose readings for the given patient (optionally filtered)."""

    @abstractmethod
    def get_meal_events(self, patient_id: str) -> list[dict[str, Any]]:
        """Return meal events (times and calories where available)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name for logging."""
