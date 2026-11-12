"""Share routes — QR code generation and public data view."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.auth import AuthenticatedUser, get_current_user
from app.modules.share.schemas import ShareConfig, ShareResponse, SharedData
from app.modules.share.service import create_share_link, get_shared_data

router = APIRouter(tags=["share"])


@router.post("/api/v1/users/me/share", response_model=ShareResponse)
def create_share(
    config: ShareConfig,
    request: Request,
    user: AuthenticatedUser = Depends(get_current_user),
) -> ShareResponse:
    """Generate a shareable link + QR code with selected health data."""
    origin = request.headers.get("origin")
    forwarded_host = request.headers.get("x-forwarded-host")
    forwarded_proto = request.headers.get("x-forwarded-proto", "http")

    if origin:
        base_url = origin
    elif forwarded_host:
        base_url = f"{forwarded_proto}://{forwarded_host}"
    else:
        base_url = str(request.base_url)

    return create_share_link(user.internal_id, config, base_url)


@router.get("/api/v1/share/{token}", response_model=SharedData)
def view_shared_data(token: str) -> SharedData:
    """Public endpoint — view shared health data (no auth required)."""
    data = get_shared_data(token)
    if not data:
        raise HTTPException(status_code=404, detail="Share link not found or expired")
    return data
