"""Nightscout CGM adapter — production stub."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.adapters.cgm.base import CGMAdapter


class NightscoutAdapter(CGMAdapter):
    """Stub — wired in production against a real Nightscout REST endpoint."""

    @property
    def provider_name(self) -> str:
        return "nightscout"

    def list_patients(self) -> list[dict[str, Any]]:
        raise NotImplementedError(
            "NightscoutAdapter is a production stub. Use CGM_PROVIDER=glucobench."
        )

    def get_readings(
        self,
        patient_id: str,
        start: datetime | None = None,
        end: datetime | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError("Nightscout integration not implemented yet.")

    def get_meal_events(self, patient_id: str) -> list[dict[str, Any]]:
        raise NotImplementedError("Nightscout integration not implemented yet.")
