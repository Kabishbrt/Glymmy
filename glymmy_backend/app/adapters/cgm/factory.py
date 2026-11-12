"""CGM adapter factory."""

from __future__ import annotations

from functools import lru_cache

from loguru import logger

from app.adapters.cgm.base import CGMAdapter
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_cgm_adapter() -> CGMAdapter:
    """Return the configured CGM adapter as a singleton."""
    settings = get_settings()
    provider = settings.CGM_PROVIDER.lower()

    if provider == "glucobench":
        from app.adapters.cgm.glucobench import GlucoBenchAdapter

        adapter: CGMAdapter = GlucoBenchAdapter()
    elif provider == "nightscout":
        from app.adapters.cgm.nightscout import NightscoutAdapter

        adapter = NightscoutAdapter()
    else:
        raise ConfigurationError(
            f"Unknown CGM_PROVIDER={provider!r}. Valid: glucobench, nightscout"
        )

    logger.info(f"CGM adapter resolved: {adapter.provider_name}")
    return adapter
