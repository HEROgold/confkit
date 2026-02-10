"""Parsers for Confkit configuration files."""

from __future__ import annotations

import os
import sys
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
else:
    from typing_extensions import Protocol, override

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

    @override
    def has_section(self, section: str) -> bool:
        return section in self.data

    @override
    def set_section(self, section: str) -> None:
        if section not in self.data:
            self.data[section] = {}

    @override
    def has_option(self, section: str, option: str) -> bool:
        return section in self.data and option in self.data[section]

    @override
    def add_section(self, section: str) -> None:
        self.set_section(section)

    @override
    def get(self, section: str, option: str, fallback: str = UNSET) -> str:
        try:
            return self.data[section][option]
        except KeyError:
            return str(fallback)

    @override
    def set(self, section: str, option: str, value: str) -> None:
        self.set_section(section)
        self.data[section][option] = value

    @override
    def remove_option(self, section: str, option: str) -> None:
        if self.has_option(section, option):
            del self.data[section][option]
