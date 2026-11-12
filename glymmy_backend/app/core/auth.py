"""Clerk JWT verification for FastAPI.

Verifies Clerk-issued JWTs using Clerk's JWKS endpoint. Returns an
AuthenticatedUser on success and raises 401 otherwise. In dev/demo
mode (when CLERK_SECRET_KEY is not set), auth is bypassed and a
demo user is returned so the dashboard works without a Clerk account.

The module also provides a resolver that maps the Clerk user ID to our
internal user record, auto-creating it on first login.

Usage:

    from fastapi import Depends
    from app.core.auth import get_current_user, AuthenticatedUser

    @router.get("/protected")
    def protected(user: AuthenticatedUser = Depends(get_current_user)):
        return {"user_id": user.internal_id, "clerk_id": user.clerk_id}
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from typing import Any
from uuid import uuid4

import httpx
from fastapi import Depends, HTTPException, Request, status
from loguru import logger


# ── AuthenticatedUser ─────────────────────────────────────────────────────────


@dataclass
class AuthenticatedUser:
    """Represents a verified user — carries both Clerk identity and our internal ID."""

    clerk_id: str
    internal_id: str  # our storage user ID
    email: str | None = None
    name: str | None = None
    is_demo: bool = False


DEMO_CLERK_ID = "demo_user"


# ── Clerk JWKS ────────────────────────────────────────────────────────────────


@lru_cache
def _get_clerk_jwks() -> dict[str, Any] | None:
    """Fetch Clerk's JWKS. Returns None if Clerk is not configured."""
    issuer = os.getenv("CLERK_JWT_ISSUER")
    if not issuer:
        return None
    try:
        resp = httpx.get(f"{issuer}/.well-known/jwks.json", timeout=5.0)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Failed to fetch Clerk JWKS: {exc}")
        return None


def _verify_clerk_jwt(token: str) -> dict[str, Any] | None:
    """Verify a Clerk JWT and return the decoded payload if valid."""
    try:
        import jwt as pyjwt
        from jwt import PyJWKClient
    except ImportError:
        logger.warning("PyJWT not installed; skipping JWT verification")
        return None

    issuer = os.getenv("CLERK_JWT_ISSUER")
    if not issuer:
        return None

    jwks_url = f"{issuer}/.well-known/jwks.json"
    try:
        jwks_client = PyJWKClient(jwks_url, cache_keys=True)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        decoded = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=issuer,
            options={"verify_aud": False},
        )
        return decoded
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"JWT verification failed: {exc}")
        return None


# ── User resolution (Clerk ID → internal user) ───────────────────────────────


def _resolve_internal_user(clerk_id: str, email: str | None, name: str | None) -> str:
    """Map a Clerk user ID to our internal user record, creating one on first login."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()

    # Look up by clerk_id in existing users
    for user in storage.list_users():
        if user.get("clerk_id") == clerk_id:
            return user["id"]

    # First login — auto-create an internal user record
    internal_id = uuid4().hex[:12]
    storage.save_user({
        "id": internal_id,
        "clerk_id": clerk_id,
        "name": name or f"User {internal_id[:6]}",
        "email": email,
        "created_at": datetime.now().isoformat(),
        "devices": [],
    })
    logger.info(f"Auto-created internal user {internal_id} for Clerk user {clerk_id}")
    return internal_id


def _resolve_demo_user() -> str:
    """Ensure a demo user exists and return its internal ID."""
    from app.adapters.storage import get_storage_adapter

    storage = get_storage_adapter()

    for user in storage.list_users():
        if user.get("clerk_id") == DEMO_CLERK_ID:
            return user["id"]

    # If seed data exists, use the first user as the demo user
    users = storage.list_users()
    if users:
        first = users[0]
        first["clerk_id"] = DEMO_CLERK_ID
        storage.save_user(first)
        return first["id"]

    # No users at all — create a minimal demo user
    demo_id = uuid4().hex[:12]
    storage.save_user({
        "id": demo_id,
        "clerk_id": DEMO_CLERK_ID,
        "name": "Demo User",
        "email": "demo@glymmy.dev",
        "created_at": datetime.now().isoformat(),
        "devices": [],
    })
    return demo_id


# ── FastAPI dependencies ──────────────────────────────────────────────────────


async def get_current_user(request: Request) -> AuthenticatedUser:
    """FastAPI dependency — returns the authenticated user.

    - If DEMO_MODE is on or Clerk is not configured: returns a demo user.
    - If the Authorization header is missing or invalid: returns 401.
    """
    from app.core.config import get_settings

    settings = get_settings()
    if settings.DEMO_MODE or not settings.CLERK_SECRET_KEY:
        internal_id = _resolve_demo_user()
        return AuthenticatedUser(
            clerk_id=DEMO_CLERK_ID,
            internal_id=internal_id,
            email="demo@glymmy.dev",
            name="Demo User",
            is_demo=True,
        )

    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Bearer token",
        )
    token = header.split(" ", 1)[1]
    payload = _verify_clerk_jwt(token)
    if not payload or not payload.get("sub"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    clerk_id = payload["sub"]
    email = payload.get("email")
    name = payload.get("name")
    internal_id = _resolve_internal_user(clerk_id, email, name)

    return AuthenticatedUser(
        clerk_id=clerk_id,
        internal_id=internal_id,
        email=email,
        name=name,
    )


async def get_optional_user(request: Request) -> AuthenticatedUser | None:
    """Like get_current_user but returns None for unauthenticated requests.

    Useful for endpoints that work both anonymously and authenticated
    (e.g., food scan — works anonymously but personalizes when logged in).
    """
    from app.core.config import get_settings

    settings = get_settings()
    if settings.DEMO_MODE or not settings.CLERK_SECRET_KEY:
        internal_id = _resolve_demo_user()
        return AuthenticatedUser(
            clerk_id=DEMO_CLERK_ID,
            internal_id=internal_id,
            is_demo=True,
        )

    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return None

    try:
        return await get_current_user(request)
    except HTTPException:
        return None


CurrentUser = Depends(get_current_user)
OptionalUser = Depends(get_optional_user)
