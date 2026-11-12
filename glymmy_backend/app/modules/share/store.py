"""In-memory share token store."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

_shares: dict[str, dict[str, Any]] = {}


def create_share(user_id: str, config_dict: dict[str, Any]) -> str:
    token = uuid4().hex[:10]
    _shares[token] = {
        "user_id": user_id,
        "config": config_dict,
        "created_at": datetime.now().isoformat(),
    }
    return token


def get_share(token: str) -> dict[str, Any] | None:
    return _shares.get(token)
