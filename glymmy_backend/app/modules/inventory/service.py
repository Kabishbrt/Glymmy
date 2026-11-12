"""Health inventory service — CRUD on user's health card."""

from __future__ import annotations

from typing import Any

from app.adapters.storage import get_storage_adapter
from app.modules.inventory.schemas import HealthInventory


def get_inventory(user_id: str) -> HealthInventory:
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return HealthInventory()
    raw = user.get("health_inventory", {})
    return HealthInventory(**raw) if raw else HealthInventory()


def update_inventory(user_id: str, data: dict[str, Any]) -> HealthInventory:
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return HealthInventory()
    existing = user.get("health_inventory", {})
    existing.update(data)
    user["health_inventory"] = existing
    storage.save_user(user)
    return HealthInventory(**existing)


def add_item(user_id: str, category: str, item: dict[str, Any]) -> HealthInventory:
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return HealthInventory()
    inv = user.setdefault("health_inventory", {})
    inv.setdefault(category, []).append(item)
    storage.save_user(user)
    return HealthInventory(**inv)


def remove_item(user_id: str, category: str, index: int) -> HealthInventory:
    storage = get_storage_adapter()
    user = storage.load_user(user_id)
    if not user:
        return HealthInventory()
    inv = user.get("health_inventory", {})
    items = inv.get(category, [])
    if 0 <= index < len(items):
        items.pop(index)
    storage.save_user(user)
    return HealthInventory(**inv)
