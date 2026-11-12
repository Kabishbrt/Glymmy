"""Lab data adapter interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LabAdapter(ABC):
    """Interface for lab test data providers."""

    @abstractmethod
    def list_patients(self, limit: int = 20) -> list[dict[str, Any]]:
        """Return metadata for available patients (sorted by 'demo value')."""

    @abstractmethod
    def get_lab_events(
        self,
        patient_id: str,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return lab events for a patient with reference ranges + flags."""

    @abstractmethod
    def get_test_catalog(self) -> list[dict[str, Any]]:
        """Return the catalog of available tests (itemid → label)."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...
