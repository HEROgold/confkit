"""Parsers for Confkit configuration files."""
from __future__ import annotations

import os
import sys
from configparser import ConfigParser
from io import TextIOWrapper
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

try:
    import msgspec
    import msgspec.json
    import msgspec.toml
    import msgspec.yaml
except ImportError as exc:
    msg = (
        "confkit.ext.parsers requires the optional 'msgspec' extra. "
        "Install it via 'pip install "
        "confkit[msgspec]' or 'uv add confkit[msgspec]'."
        "This is required for json, toml and yaml parsing."
    )
    raise ImportError(msg) from exc


if sys.version_info >= (3, 12):
    from typing import Protocol, override
    # TD: Use nested types when Python 3.11 is EOL and we can drop support for it
    # otherwise this gets syntax errors.
    # type NestedDict = dict[str, NestedDict | str | int | float | bool | None]  # noqa: ERA001
    NestedDict = dict[str, Any]
else:
    from typing_extensions import Protocol, override
    NestedDict = dict[str, Any]

from confkit.sentinels import UNSET

if TYPE_CHECKING:
    from io import TextIOWrapper, _WrappedBuffer
    from pathlib import Path
    from types import ModuleType


T = TypeVar("T")

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
    def set(self, section: str, option: str, value: str) -> None:
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
    def set(self, section: str, option: str, value: str) -> None:
        self.parser.set(section, option, value)


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
    def set(self, section: str, option: str, value: str) -> None:
        """Set the value of an option (section is ignored)."""
        msg = "EnvParser does not support set"
        raise NotImplementedError(msg)


class MsgspecParser(ConfkitParser, Generic[T]):
    """Unified msgspec-based parser for YAML, JSON, TOML configuration files."""

    _parsers: ClassVar[dict[str, ModuleType]] = {
        ".yaml": msgspec.yaml,
        ".yml": msgspec.yaml,
        ".json": msgspec.json,
        ".toml": msgspec.toml,
    }

    def __init__(self) -> None:  # noqa: D107
        self.data = {}

    @override
    def read(self, file: Path) -> None:
        if not file.exists():
            file.write_text("{}" if file.suffix.lower() == ".json" else "")
            self.data: dict[Any, Any] = {}
            return

        with file.open("rb") as f:
            ext = file.suffix.lower()
            if parser := self._parsers.get(ext):
                try:
                    self.data = parser.decode(f.read())
                    # Handle None or empty values from YAML/TOML files
                    if self.data is None or not isinstance(self.data, dict):
                        self.data = {}
                except msgspec.DecodeError:
                    self.data = {}
                return
            msg = f"Unsupported file extension for reading: {ext}"
            raise ValueError(msg)

    @override
    def write(self, io: TextIOWrapper[_WrappedBuffer]) -> None:
        ext = io.name.lower().rsplit(".", 1)[-1]
        if parser := self._parsers.get(f".{ext}"):
            encoded = parser.encode(self.data)
            if isinstance(encoded, bytes):
                io.write(encoded.decode("utf-8"))
            else:
                io.write(str(encoded))
            return
        msg = f"Unsupported file extension for writing: {ext}"
        raise ValueError(msg)

    def _navigate_to_section(self, section: str, *, create: bool = False) -> NestedDict | None:
        """Navigate to a nested section using dot notation.

        Args:
            section: Dot-separated section path (e.g., "Parent.Child.GrandChild")
            create: If True, create missing intermediate sections

        Returns:
            The nested dict at the section path, or None if not found and create=False

        """
        if not section:
            return self.data

        parts = section.split(".")
        current = self.data

        for part in parts:
            if not isinstance(current, dict):
                return None
            if part not in current:
                if create:
                    current[part] = {}
                else:
                    return None
            current = current[part]

        return current if isinstance(current, dict) else None

    @override
    def has_section(self, section: str) -> bool:
        return self._navigate_to_section(section, create=False) is not None

    @override
    def set_section(self, section: str) -> None:
        self._navigate_to_section(section, create=True)

    @override
    def has_option(self, section: str, option: str) -> bool:
        section_data = self._navigate_to_section(section, create=False)
        return section_data is not None and option in section_data

    @override
    def add_section(self, section: str) -> None:
        self.set_section(section)

    @override
    def get(self, section: str, option: str, fallback: str = UNSET) -> str:
        section_data = self._navigate_to_section(section, create=False)
        if section_data is None or option not in section_data:
            return str(fallback) if fallback is not UNSET else ""
        return str(section_data[option])

    @override
    def set(self, section: str, option: str, value: str) -> None:
        section_data = self._navigate_to_section(section, create=True)
        if section_data is not None:
            # Try to preserve the original type by parsing the string value
            # This is important for JSON/YAML/TOML which support native types
            parsed_value = self._parse_value(value)
            section_data[option] = parsed_value

    def _parse_value(self, value: str) -> bool | int | float | str:
        """Parse a string value to its appropriate type for structured formats.

        Attempts to convert string values back to their original types:
        - "True"/"False" -> bool
        - Integer strings -> int
        - Float strings -> float
        - Everything else remains a string
        """
        if value == "True":
            return True
        if value == "False":
            return False

        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value

    @override
    def remove_option(self, section: str, option: str) -> None:
        section_data = self._navigate_to_section(section, create=False)
        if section_data is not None and option in section_data:
            del section_data[option]
