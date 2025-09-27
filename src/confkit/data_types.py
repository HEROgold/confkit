"""Module that contains the base data types used in the config system."""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import ClassVar, Generic, TypeVar, cast
from urllib.parse import urlparse, urlunparse

from confkit.sentinels import UNSET

from .exceptions import InvalidConverterError, InvalidDefaultError

T = TypeVar("T")


class BaseDataType(ABC, Generic[T]):
    """Base class used for Config descriptors to define a data type."""

    def __init__(self, default: T) -> None:
        """Initialize the base data type."""
        self.default = default
        self.value = default

    def __str__(self) -> str:
        """Return the string representation of the stored value."""
        return str(self.value)

    @abstractmethod
    def convert(self, value: str) -> T:
        """Convert a string value to the desired type."""

    def validate(self) -> bool:
        """Validate that the value matches the expected type."""
        orig_bases: tuple[type, ...] | None = getattr(self.__class__, "__orig_bases__", None)

        if not orig_bases:
            msg = "No type information available for validation."
            raise InvalidConverterError(msg)

        # Extract type arguments from the generic base
        for base in orig_bases:
            if hasattr(base, "__args__"):
                type_args = base.__args__
                if type_args:
                    for type_arg in type_args:
                        if hasattr(type_arg, "__origin__"):
                            # For parameterized generics, check against the origin type
                            if isinstance(self.value, type_arg.__origin__):
                                return True
                        elif isinstance(self.value, type_arg):
                            return True
                    msg = f"Value {self.value} is not any of {type_args}."
                    raise InvalidConverterError(msg)
        msg = "This should not have raised. Report to the library maintainers with code: `DTBDT`"
        raise TypeError(msg)

    @staticmethod
    def cast_optional(default: T | None | BaseDataType[T]) -> BaseDataType[T | None]:
        """Convert the default value to an Optional data type."""
        if default is None:
            return cast("BaseDataType[T | None]", NoneType())
        return Optional(BaseDataType.cast(default))

    @staticmethod
    def cast(default: T | BaseDataType[T]) -> BaseDataType[T]:
        """Convert the default value to a BaseDataType."""
        # We use Cast to shut up type checkers, as we know primitive types will be correct.
        # If a custom type is passed, it should be a BaseDataType subclass, which already has the correct types.
        match default:
            case bool():
                data_type = cast("BaseDataType[T]", Boolean(default))
            case None:
                data_type = cast("BaseDataType[T]", NoneType())
            case int():
                data_type = cast("BaseDataType[T]", Integer(default))
            case float():
                data_type = cast("BaseDataType[T]", Float(default))
            case str():
                data_type = cast("BaseDataType[T]", String(default))
            case BaseDataType():
                data_type = default
            case _:
                msg = (
                    f"Unsupported default value type: {type(default).__name__}. "
                    "Use a BaseDataType subclass for custom types."
                )
                raise InvalidDefaultError(msg)
        return data_type

class Enum(BaseDataType[enum.Enum]):
    """A config value that is an enum."""

    def convert(self, value: str) -> enum.Enum:
        """Convert a string value to an enum."""
        parsed_enum_name = value.split(".")[-1]
        return self.value.__class__[parsed_enum_name]

class StrEnum(BaseDataType[enum.StrEnum]):
    """A config value that is an enum."""

    def convert(self, value: str) -> enum.StrEnum:
        """Convert a string value to an enum."""
        return self.value.__class__(value)

class IntEnum(BaseDataType[enum.IntEnum]):
    """A config value that is an enum."""

    def convert(self, value: str) -> enum.IntEnum:
        """Convert a string value to an enum."""
        return self.value.__class__(int(value))

class IntFlag(BaseDataType[enum.IntFlag]):
    """A config value that is an enum."""

    def convert(self, value: str) -> enum.IntFlag:
        """Convert a string value to an enum."""
        return self.value.__class__(int(value))

class NoneType(BaseDataType[None]):
    """A config value that is None."""

    null_values: ClassVar[set[str]] = {"none", "null", "nil"}

    def __init__(self) -> None:
        """Initialize the NoneType data type."""
        super().__init__(None)

    def convert(self, value: str) -> bool: # type: ignore[reportIncompatibleMethodOverride]
        """Convert a string value to None."""
        # Ignore type exception as convert should return True/False for NoneType
        # to determine if we have a valid null value or not.
        return value.casefold().strip() in NoneType.null_values


class String(BaseDataType[str]):
    """A config value that is a string."""

    def __init__(self, default: str = "") -> None:  # noqa: D107
        super().__init__(default)

    def convert(self, value: str) -> str:
        """Convert a string value to a string."""
        return value


class Float(BaseDataType[float]):
    """A config value that is a float."""

    def __init__(self, default: float = 0.0) -> None:  # noqa: D107
        super().__init__(default)

    def convert(self, value: str) -> float:
        """Convert a string value to a float."""
        return float(value)


class Boolean(BaseDataType[bool]):
    """A config value that is a boolean."""

    def __init__(self, default: bool = False) -> None:  # noqa: D107, FBT001, FBT002
        super().__init__(default)

    def convert(self, value: str) -> bool:
        """Convert a string value to a boolean."""
        if value.lower() in {"true", "1", "yes"}:
            return True
        if value.lower() in {"false", "0", "no"}:
            return False
        msg = f"Cannot convert {value} to boolean."
        raise ValueError(msg)

DECIMAL = 10
HEXADECIMAL = 16
OCTAL = 8
BINARY = 2

class Integer(BaseDataType[int]):
    """A config value that is an integer."""

    # Define constants for common bases

    def __init__(self, default: int = 0, base: int = DECIMAL) -> None:  # noqa: D107
        super().__init__(default)
        self.base = base

    @staticmethod
    def int_to_base(number: int, base: int) -> int:
        """Convert an integer to a string representation in a given base."""
        if number == 0:
            return 0
        digits = []
        while number:
            digits.append(str(number % base))
            number //= base
        return int("".join(reversed(digits)))

    def __str__(self) -> str:  # noqa: D105
        if self.base == DECIMAL:
            return str(self.value)
        # Convert the base 10 int to base 5
        self.value = self.int_to_base(int(self.value), self.base)
        return f"{self.base}c{self.value}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer."""
        if "c" in value:
            base_str, val_str = value.split("c")
            base = int(base_str)
            if base != self.base:
                msg = "Base in string does not match base in Integer while converting."
                raise ValueError(msg)
            return int(val_str, self.base)
        return int(value, self.base)

class Hex(Integer):
    """A config value that represents hexadecimal."""

    def __init__(self, default: int, base: int = HEXADECIMAL) -> None:  # noqa: D107
        super().__init__(default, base)

    def __str__(self) -> str:  # noqa: D105
        return f"0x{self.value:x}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer. from hexadecimal."""
        return int(value.removeprefix("0x"), 16)

class Octal(Integer):
    """A config value that represents octal."""

    def __init__(self, default: int, base: int = OCTAL) -> None:  # noqa: D107
        super().__init__(default, base)

    def __str__(self) -> str:  # noqa: D105
        return f"0o{self.value:o}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer from octal."""
        return int(value.removeprefix("0o"), 8)

class Binary(BaseDataType[bytes | int]):
    """A config value that represents binary."""

    def __init__(self, default: bytes | int) -> None:  # noqa: D107
        if isinstance(default, bytes):
            default = int.from_bytes(default)
        super().__init__(default)

    def __str__(self) -> str:  # noqa: D105
        if isinstance(self.value, bytes):
            self.value = int.from_bytes(self.value)
        return f"0b{self.value:b}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer from binary."""
        return int(value.removeprefix("0b"), 2)

class Optional(BaseDataType[T | None], Generic[T]):
    """A config value that is optional, can be None or a specific type."""

    _none_type = NoneType()

    def __init__(self, data_type: BaseDataType[T]) -> None:
        """Initialize the optional data type. Wrapping the provided data type."""
        self._data_type = data_type

    @property
    def default(self) -> T | None:
        """Get the default value of the wrapped data type."""
        return self._data_type.default

    @property
    def value(self) -> T | None:
        """Get the current value of the wrapped data type."""
        return self._data_type.value

    @value.setter
    def value(self, value: T | None) -> None:
        """Set the current value of the wrapped data type."""
        self._data_type.value = value # type: ignore[reportAttributeAccessIssue]

    def convert(self, value: str) -> T | None:
        """Convert a string value to the optional type."""
        if self._none_type.convert(value):
            return None
        return self._data_type.convert(value)

    def validate(self) -> bool:
        """Validate that the value is of the wrapped data type or None."""
        if self._data_type.value is None:
            return True
        return self._data_type.validate()

class List(BaseDataType[list[T]], Generic[T]):
    """A config value that is a list of values."""

    separator = ","
    escape_char = "\\"

    def __init__(self, default: list[T], *, data_type: BaseDataType[T] = UNSET) -> None:
        """Initialize the list data type."""
        super().__init__(default)
        if len(default) <= 0 and data_type is UNSET:
            msg = "List default must have at least one element to infer type. or specify `data_type=<BaseDataType>`"
            raise InvalidDefaultError(msg)
        if data_type is UNSET:
            self._data_type = BaseDataType[T].cast(default[0])
        else:
            self._data_type = data_type

    def convert(self, value: str) -> list[T]:
        """Convert a string to a list."""
        # Handle empty string as empty list
        if not value:
            return []

        # Split string but respect escaped separators
        result: list[T] = []
        current = ""
        i = 0
        while i < len(value):
            # Check for escaped separator
            if i < len(value) - 1 and value[i] == self.escape_char and value[i + 1] == self.separator:
                current += self.separator
                i += 2  # Skip both the escape char and the separator
            # Check for escaped escape char
            elif i < len(value) - 1 and value[i] == self.escape_char and value[i + 1] == self.escape_char:
                current += self.escape_char
                i += 2  # Skip both escape chars
            # Handle separator
            elif value[i] == self.separator:
                c = self._data_type.convert(current)
                result.append(c)
                current = ""
                i += 1
            # Handle regular character
            else:
                current += value[i]
                i += 1

        # Add the last element
        result.append(self._data_type.convert(current))

        return result

    def __str__(self) -> str:
        """Return a string representation of the list."""
        values: list[str] = []
        for item in self.value:
            # Escape escape char
            escaped_item = str(item).replace(self.escape_char, self.escape_char*2)
            # Escape separator
            escaped_item = escaped_item.replace(self.separator, f"{self.escape_char}{self.separator}")
            values.append(escaped_item)

        return self.separator.join(values)


class URL(BaseDataType[str]):
    """A config value that represents a URL with validation."""

    def __init__(self, default: str) -> None:
        """Initialize the URL data type."""
        # Validate the default URL
        parsed = urlparse(default)
        if not all([parsed.scheme, parsed.netloc]):
            msg = f"Invalid default URL: {default}. URL must have scheme and netloc."
            raise ValueError(msg)
        super().__init__(default)

    def convert(self, value: str) -> str:
        """Convert a string value to a validated URL."""
        if not value.strip():
            msg = "URL cannot be empty"
            raise ValueError(msg)
        
        parsed = urlparse(value)
        if not all([parsed.scheme, parsed.netloc]):
            msg = f"Invalid URL: {value}. URL must have scheme and netloc."
            raise ValueError(msg)
        
        # Return normalized URL
        return urlunparse(parsed)

    def __str__(self) -> str:
        """Return the string representation of the URL."""
        return str(self.value)


class DateTime(BaseDataType[datetime]):
    """A config value that represents a datetime with ISO 8601 format support."""

    def __init__(self, default: datetime) -> None:
        """Initialize the DateTime data type."""
        if not isinstance(default, datetime):
            msg = f"Default value must be a datetime object, got {type(default).__name__}"
            raise TypeError(msg)
        super().__init__(default)

    def convert(self, value: str) -> datetime:
        """Convert a string value to a datetime object.
        
        Supports ISO 8601 format: YYYY-MM-DDTHH:MM:SS[.ffffff][+HH:MM]
        """
        if not value.strip():
            msg = "DateTime string cannot be empty"
            raise ValueError(msg)
        
        try:
            # Try parsing with fromisoformat (Python 3.7+)
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError as e:
            msg = f"Invalid datetime format: {value}. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SS)"
            raise ValueError(msg) from e

    def __str__(self) -> str:
        """Return the ISO 8601 string representation of the datetime."""
        return self.value.isoformat()


class TimeDelta(BaseDataType[timedelta]):
    """A config value that represents a time duration with ISO 8601 duration format support."""

    def __init__(self, default: timedelta) -> None:
        """Initialize the TimeDelta data type."""
        if not isinstance(default, timedelta):
            msg = f"Default value must be a timedelta object, got {type(default).__name__}"
            raise TypeError(msg)
        super().__init__(default)

    def convert(self, value: str) -> timedelta:
        """Convert a string value to a timedelta object.
        
        Supports ISO 8601 duration format: P[n]Y[n]M[n]DT[n]H[n]M[n]S
        And flexible formats like: "1h 30m", "90 minutes", "1:30:00"
        """
        if not value.strip():
            msg = "TimeDelta string cannot be empty"
            raise ValueError(msg)
        
        value = value.strip()
        
        # Try ISO 8601 duration format first
        if value.upper().startswith('P'):
            return self._parse_iso8601_duration(value)
        
        # Try flexible formats
        return self._parse_flexible_duration(value)

    def _parse_iso8601_duration(self, value: str) -> timedelta:
        """Parse ISO 8601 duration format: P[n]Y[n]M[n]DT[n]H[n]M[n]S"""
        import re
        
        # ISO 8601 duration regex - allow decimals in all time units
        iso_regex = re.compile(
            r'^P(?:(\d+(?:\.\d+)?)Y)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)D)?(?:T(?:(\d+(?:\.\d+)?)H)?(?:(\d+(?:\.\d+)?)M)?(?:(\d+(?:\.\d+)?)S)?)?$'
        )
        
        match = iso_regex.match(value.upper())
        if not match:
            msg = f"Invalid ISO 8601 duration format: {value}"
            raise ValueError(msg)
        
        years, months, days, hours, minutes, seconds = match.groups()
        
        # Convert to timedelta (approximate for years and months)
        total_days = 0
        if years:
            total_days += float(years) * 365  # Approximate
        if months:
            total_days += float(months) * 30  # Approximate
        if days:
            total_days += float(days)
            
        total_seconds = 0
        if hours:
            total_seconds += float(hours) * 3600
        if minutes:
            total_seconds += float(minutes) * 60
        if seconds:
            total_seconds += float(seconds)
            
        return timedelta(days=total_days, seconds=total_seconds)

    def _parse_flexible_duration(self, value: str) -> timedelta:
        """Parse flexible duration formats like '1h 30m', '90 minutes', '1:30:00'"""
        import re
        
        value = value.lower().strip()
        
        # Try HH:MM:SS format first
        time_regex = re.compile(r'^(\d+):(\d+):(\d+)(?:\.(\d+))?$')
        match = time_regex.match(value)
        if match:
            hours, minutes, seconds, microseconds = match.groups()
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + int(seconds)
            if microseconds:
                total_seconds += float(f"0.{microseconds}")
            return timedelta(seconds=total_seconds)
        
        # Try MM:SS format
        time_regex = re.compile(r'^(\d+):(\d+)(?:\.(\d+))?$')
        match = time_regex.match(value)
        if match:
            minutes, seconds, microseconds = match.groups()
            total_seconds = int(minutes) * 60 + int(seconds)
            if microseconds:
                total_seconds += float(f"0.{microseconds}")
            return timedelta(seconds=total_seconds)
        
        # Parse flexible text format (e.g., "1h 30m", "90 minutes")
        total_seconds = 0
        
        # Define unit multipliers
        units = {
            'w': 604800, 'week': 604800, 'weeks': 604800,
            'd': 86400, 'day': 86400, 'days': 86400,
            'h': 3600, 'hour': 3600, 'hours': 3600, 'hr': 3600, 'hrs': 3600,
            'm': 60, 'min': 60, 'mins': 60, 'minute': 60, 'minutes': 60,
            's': 1, 'sec': 1, 'secs': 1, 'second': 1, 'seconds': 1,
        }
        
        # Find all number-unit pairs
        pattern = re.compile(r'(\d+(?:\.\d+)?)\s*([a-z]+)')
        matches = pattern.findall(value)
        
        if not matches:
            # Try parsing as pure number (assume seconds)
            try:
                return timedelta(seconds=float(value))
            except ValueError:
                msg = f"Invalid duration format: {value}"
                raise ValueError(msg)
        
        for num_str, unit in matches:
            if unit not in units:
                msg = f"Unknown time unit: {unit}"
                raise ValueError(msg)
            total_seconds += float(num_str) * units[unit]
        
        return timedelta(seconds=total_seconds)

    def __str__(self) -> str:
        """Return the ISO 8601 duration string representation."""
        td = self.value
        
        if td.total_seconds() == 0:
            return "PT0S"
        
        # Handle negative durations
        sign = "-" if td.total_seconds() < 0 else ""
        td = abs(td)
        
        days = td.days
        seconds = td.seconds
        microseconds = td.microseconds
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        # Build ISO 8601 duration string
        result = f"{sign}P"
        
        if days:
            result += f"{days}D"
        
        if hours or minutes or secs or microseconds:
            result += "T"
            if hours:
                result += f"{hours}H"
            if minutes:
                result += f"{minutes}M"
            if secs or microseconds:
                if microseconds:
                    total_secs = secs + microseconds / 1_000_000
                    result += f"{total_secs:g}S"
                else:
                    result += f"{secs}S"
        
        return result
