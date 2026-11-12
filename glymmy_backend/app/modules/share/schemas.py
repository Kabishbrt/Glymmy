"""Share / QR schemas."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ShareConfig(BaseModel):
    include_profile: bool = True
    include_glucose: bool = True
    include_vitals: bool = True
    include_medications: bool = True
    include_conditions: bool = True


class ShareResponse(BaseModel):
    share_token: str
    share_url: str
    qr_data_url: str
    created_at: str


class SharedData(BaseModel):
    user_name: str
    shared_at: str
    profile: dict[str, Any] | None = None
    glucose_summary: dict[str, Any] | None = None
    vitals: dict[str, Any] | None = None
    medications: list[dict[str, Any]] | None = None
    conditions: list[dict[str, Any]] | None = None
