"""Optional msgspec-based parsers for Confkit configuration files.

This module requires the ``msgspec`` optional extra:

    pip install confkit[msgspec]
    uv add confkit[msgspec]

Importing this module without ``msgspec`` installed will raise an
``ImportError`` immediately.  Built-in parsers (``IniParser``,
``EnvParser``, ``ConfkitParser``) that have no optional dependencies
live in ``confkit.parsers``.
"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any, ClassVar, Generic, TypeVar

from confkit.data_types import BaseDataType
from confkit.exceptions import ConfigPathConflictError
from confkit.parsers import ConfkitParser

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
    from typing import override
    # TD: Use nested types when Python 3.11 is EOL and we can drop support for it
    # otherwise this gets syntax errors.
    # type NestedDict = dict[str, NestedDict | str | int | float | bool | None]  # noqa: ERA001
    NestedDict = dict[str, Any]
else:
    from typing_extensions import override
    NestedDict = dict[str, Any]

from confkit.sentinels import UNSET

if TYPE_CHECKING:
    from io import TextIOWrapper, _WrappedBuffer
    from pathlib import Path
    from types import ModuleType


T = TypeVar("T")


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
            create: If True, create missing intermediate sections and raise an error
                    if any path element is a scalar instead of a dict.

        Returns:
            The nested dict at the section path, or None if not found and create=False

        Raises:
            ConfigPathConflictError: When create=True and any path element (including
                                     the final one) is a scalar value instead of a dict.
                                     This prevents silent data loss from overwriting scalars.

        """
        if not section:
            return self.data

        parts = section.split(".")
        current = self.data

        for i, part in enumerate(parts):
            if not isinstance(current, dict):
                if create:
                    path_so_far = ".".join(parts[:i])
                    msg = (
                        f"Cannot navigate to section '{section}': "
                        f"'{path_so_far}' is a scalar value, not a section. "
                        f"Path conflict at '{part}'."
                    )
                    raise ConfigPathConflictError(msg)
                return None
            if part not in current:
                if create:
                    current[part] = {}
                else:
                    return None
            current = current[part]
            # Check if we hit a scalar anywhere in the path (including final element when create=True)
            if not isinstance(current, dict):
                if create:
                    path_so_far = ".".join(parts[: i + 1])
                    is_final = i == len(parts) - 1
                    if is_final:
                        msg = (
                            f"Cannot navigate to section '{section}': "
                            f"'{path_so_far}' is a scalar value, not a section."
                        )
                    else:
                        msg = (
                            f"Cannot navigate to section '{section}': "
                            f"'{path_so_far}' is a scalar value, not a section. "
                            f"Path conflict at '{parts[i + 1]}'."
                        )
                    raise ConfigPathConflictError(msg)
                return None

        return current  # guaranteed to be a dict here

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
            return str(fallback) if fallback is not UNSET else UNSET
        return str(section_data[option])

    @override
    def set(self, section: str, option: str, value: object) -> None:
        # Raises ConfigPathConflictError if any path element is a scalar.
        section_data = self._navigate_to_section(section, create=True)
        # _navigate_to_section always raises ConfigPathConflictError when create=True
        # and the path is blocked, so section_data is guaranteed to be a dict here.
        assert section_data is not None  # noqa: S101
        if isinstance(value, BaseDataType):
            native = value.value
            # BaseDataType.__str__ returns str(self.value) by default.
            # Subclasses with custom string representations (e.g. Hex returns "0xa",
            # Octal returns "0o10") override __str__, causing str(native) != str(value).
            # In those cases, store the custom string so convert() can round-trip
            # correctly on the next read. For standard types the native Python value
            # is stored directly, preserving native JSON/YAML/TOML types.
            stored = native if str(native) == str(value) else str(value)
        else:
            stored = value
        section_data[option] = stored

    @override
    def remove_option(self, section: str, option: str) -> None:
        section_data = self._navigate_to_section(section, create=False)
        if section_data is not None and option in section_data:
            del section_data[option]
