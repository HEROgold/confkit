"""Module that contains the base data types used in the config system."""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, TypeVar, cast

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
