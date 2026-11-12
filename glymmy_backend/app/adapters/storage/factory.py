"""Storage adapter factory."""

from __future__ import annotations

from functools import lru_cache

from loguru import logger

from app.adapters.storage.base import StorageAdapter
from app.core.config import get_settings
from app.core.exceptions import ConfigurationError


@lru_cache
def get_storage_adapter() -> StorageAdapter:
    """Return the configured storage adapter as a singleton."""
    settings = get_settings()
    provider = settings.STORAGE_PROVIDER.lower()

    if provider == "memory":
        from app.adapters.storage.memory import MemoryStorageAdapter

        adapter: StorageAdapter = MemoryStorageAdapter()
    elif provider == "neon":
        from app.adapters.storage.neon import NeonStorageAdapter

        adapter = NeonStorageAdapter()
    else:
        raise ConfigurationError(
            f"Unknown STORAGE_PROVIDER={provider!r}. Valid: memory, neon"
        )

    logger.info(f"Storage adapter resolved: {adapter.provider_name}")
    return adapter
