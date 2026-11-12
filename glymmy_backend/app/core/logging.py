"""Loguru configuration for the whole app."""

from __future__ import annotations

import sys

from loguru import logger

from app.core.config import get_settings


def setup_logging() -> None:
    """Configure loguru sinks. Call once at startup."""
    settings = get_settings()
    logger.remove()
    logger.add(
        sys.stdout,
        level="DEBUG" if settings.DEBUG else "INFO",
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    logger.info(f"Logging configured | debug={settings.DEBUG}")
