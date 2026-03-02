"""Built-in parsers for Confkit configuration files.

This module provides parsers that have no optional dependencies:
- ``ConfkitParser``: Protocol defining the unified parser interface
- ``IniParser``: Adapter for Python's built-in ``ConfigParser`` (INI files)
- ``EnvParser``: Adapter for environment variables and ``.env`` files

Parsers that require optional extras (e.g. ``MsgspecParser`` for JSON/YAML/TOML)
live in ``confkit.ext.parsers``.
"""
from __future__ import annotations

import os
import sys
from configparser import ConfigParser
from typing import TYPE_CHECKING

from confkit.sentinels import UNSET

if sys.version_info >= (3, 12):
    from typing import Protocol, override
else:
    from typing_extensions import Protocol, override

if TYPE_CHECKING:
    from io import TextIOWrapper, _WrappedBuffer
    from pathlib import Path


class ConfkitParser(Protocol):
    """A protocol for Confkit parsers."""

    def read(self, file: Path) -> None:
        """Read the configuration from a file."""
    def write(self, io: TextIOWrapper[_WrappedBuffer]) -> None:
        """Write the configuration to a file-like object."""
    def has_section(self, section: str) -> bool:
        """Check if a section exists."""
    def set_section(self, section: str) -> None:
        """Set a section."""
    def set_option(self, option: str) -> None:
        """Set an option."""
    def add_section(self, section: str) -> None:
        """Add a section."""
    def has_option(self, section: str, option: str) -> bool:
        """Check if an option exists within a section."""
    def remove_option(self, section: str, option: str) -> None:
        """Remove an option from a section."""
    def get(self, section: str, option: str, fallback: str = UNSET) -> str:
        """Get the value of an option within a section, with an optional fallback."""
    def set(self, section: str, option: str, value: object) -> None:
        """Set the value of an option within a section."""


class IniParser(ConfkitParser):
    """Adapter for ConfigParser that supports dot notation for nested sections."""

    def __init__(self) -> None:
        """Initialize the IniParser with an internal ConfigParser instance."""
        self.parser = ConfigParser()
        self._file: Path | None = None

    @override
    def read(self, file: Path) -> None:
        self.parser.read(file)

    @override
    def write(self, io: TextIOWrapper) -> None:
        self.parser.write(io)

    @override
    def has_section(self, section: str) -> bool:
        return self.parser.has_section(section)

    @override
    def set_section(self, section: str) -> None:
        if not self.parser.has_section(section):
            self.parser.add_section(section)

    @override
    def set_option(self, option: str) -> None:
        # Not used directly; options are set via set()
        pass

    @override
    def add_section(self, section: str) -> None:
        self.parser.add_section(section)

    @override
    def has_option(self, section: str, option: str) -> bool:
        return self.parser.has_option(section, option)

    @override
    def remove_option(self, section: str, option: str) -> None:
        self.parser.remove_option(section, option)

    @override
    def get(self, section: str, option: str, fallback: str = UNSET) -> str:
        return self.parser.get(section, option, fallback=fallback)

    @override
    def set(self, section: str, option: str, value: object) -> None:
        # ConfigParser requires strings; escape % signs for interpolation
        str_value = str(value).replace("%", "%%")
        self.parser.set(section, option, str_value)


class EnvParser(ConfkitParser):
    """A parser for environment variables and .env files.

    This parser operates without sections - all configuration is stored as flat key-value pairs.
    Values are read from environment variables and optionally persisted to a .env file.
    """

    def __init__(self) -> None:  # noqa: D107
        self.data: dict[str, str] = {}

    @override
    def read(self, file: Path) -> None:
        """Precedence, from lowest to highest.

        - config file
        - environment vars
        """
        self.data = dict(os.environ)

        if not file.exists():
            return

        with file.open("r", encoding="utf-8") as f:
            for i in f:
                line = i.strip()
                if not line or line.startswith("#"):
                    continue

                match line.split("=", 1):
                    case [key, value]:
                        if key not in os.environ:
                            # Strip quotes from values
                            value = value.strip()
                            if (value.startswith('"') and value.endswith('"')) or \
                               (value.startswith("'") and value.endswith("'")):
                                value = value[1:-1]
                            self.data[key.strip()] = value

    @override
    def remove_option(self, section: str, option: str) -> None:
        """Remove an option (section is ignored)."""
        if option in self.data:
            del self.data[option]

    @override
    def get(self, section: str, option: str, fallback: str = UNSET) -> str:
        """Get the value of an option (section is ignored)."""
        if option in self.data:
            return self.data[option]
        if fallback is not UNSET:
            return str(fallback)
        return ""

    @override
    def has_option(self, section: str, option: str) -> bool:
        """Check if an option exists (section is ignored)."""
        return option in self.data

    @override
    def has_section(self, section: str) -> bool:
        """EnvParser has no sections, always returns True for compatibility."""
        return True

    @override
    def write(self, io: TextIOWrapper[_WrappedBuffer]) -> None:
        """Write configuration to a .env file."""
        msg = "EnvParser does not support writing to .env"
        raise NotImplementedError(msg)

    @override
    def set_section(self, section: str) -> None:
        """EnvParser has no sections, this is a no-op."""
        pass  # noqa: PIE790

    @override
    def set_option(self, option: str) -> None:
        """Set an option (not used in EnvParser)."""
        msg = "EnvParser does not support set_option"
        raise NotImplementedError(msg)

    @override
    def add_section(self, section: str) -> None:
        """EnvParser has no sections, this is a no-op."""
        pass  # noqa: PIE790

    @override
    def set(self, section: str, option: str, value: object) -> None:
        """Set the value of an option (section is ignored)."""
        msg = "EnvParser does not support set"
        raise NotImplementedError(msg)
