"""Custom exception classes for Glymmy."""

from __future__ import annotations


class GlymmyError(Exception):
    """Base exception for all Glymmy errors."""


class AdapterError(GlymmyError):
    """Raised when an adapter fails."""


class DatasetNotFoundError(AdapterError):
    """Raised when a dataset file cannot be located."""


class PatientNotFoundError(GlymmyError):
    """Raised when a patient ID does not exist."""


class LLMProviderError(AdapterError):
    """Raised when the LLM provider fails."""


class ConfigurationError(GlymmyError):
    """Raised when configuration is invalid."""
