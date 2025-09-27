"""Module for custom exceptions used in the confkit package."""

class InvalidDefaultError(ValueError):
    """Raised when the default value is not set or invalid."""


class InvalidConverterError(ValueError):
    """Raised when the converter is not set or invalid."""
