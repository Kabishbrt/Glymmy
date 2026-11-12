"""Health inventory routes — personal health record CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.inventory.schemas import HealthInventory
from app.modules.inventory.service import add_item, get_inventory, remove_item, update_inventory

router = APIRouter(prefix="/api/v1/users/me/inventory", tags=["inventory"])


@router.get("", response_model=HealthInventory)
def read_inventory(user: AuthenticatedUser = Depends(get_current_user)) -> HealthInventory:
    return get_inventory(user.internal_id)


@router.patch("")
def patch_inventory(body: dict, user: AuthenticatedUser = Depends(get_current_user)) -> HealthInventory:
    return update_inventory(user.internal_id, body)


@router.post("/{category}")
def add_inventory_item(category: str, body: dict, user: AuthenticatedUser = Depends(get_current_user)) -> HealthInventory:
    return add_item(user.internal_id, category, body)


@router.delete("/{category}/{index}")
def remove_inventory_item(category: str, index: int, user: AuthenticatedUser = Depends(get_current_user)) -> HealthInventory:
    return remove_item(user.internal_id, category, index)
