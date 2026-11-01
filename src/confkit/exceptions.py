"""Module for custom exceptions used in the confkit package."""
from __future__ import annotations


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


class InvalidKeyError(ValueError):
    """Raised when a key can't be stored in the config file format, such as an INI key containing `=`, `:` or a line break."""
