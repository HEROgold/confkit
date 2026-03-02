"""Module for custom exceptions used in the confkit package."""

class InvalidDefaultError(ValueError):
    """Raised when the default value is not set or invalid."""


class InvalidConverterError(ValueError):
    """Raised when the converter is not set or invalid."""


class ConfigPathConflictError(ValueError):
    """Raised when a configuration path conflicts with an existing scalar value.

    This occurs when attempting to treat a scalar value as a section (dict).
    For example, if "Parent.Value" is a scalar, attempting to set "Parent.Value.Child"
    would cause this error.
    """
