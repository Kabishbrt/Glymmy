"""Labs adapter factory."""

from __future__ import annotations

from functools import lru_cache

from loguru import logger

from app.adapters.labs.base import LabAdapter
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_labs_adapter() -> LabAdapter:
    """Return the configured lab adapter as a singleton."""
    settings = get_settings()
    provider = settings.LABS_PROVIDER.lower()

    if provider == "mimic":
        from app.adapters.labs.mimic import MimicLabAdapter

        adapter: LabAdapter = MimicLabAdapter()
    else:
        raise ConfigurationError(
            f"Unknown LABS_PROVIDER={provider!r}. Valid: mimic"
        )

    logger.info(f"Labs adapter resolved: {adapter.provider_name}")
    return adapter
