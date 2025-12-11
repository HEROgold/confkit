"""Module that contains the base data types used in the config system."""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta, tzinfo
from typing import ClassVar, Generic, NotRequired, Required, TypedDict, TypeVar, Unpack, cast, overload

from confkit.sentinels import UNSET

from .exceptions import InvalidConverterError, InvalidDefaultError

T = TypeVar("T")


class BaseDataType(ABC, Generic[T]):
    """Base class used for Config descriptors to define a data type."""

    def __init__(self, default: T) -> None:
        """Initialize the base data type."""
        self.default = default
        self.value = default
        self.type = type(default)

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
                        elif isinstance(self.value, (self.type, type_arg)):
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


class _EnumBase(BaseDataType[T]):
    """Base class for enum types with common functionality."""

    @staticmethod
    def _strip_comment(value: str) -> str:
        """Strip inline comments from value.

        Since hex values use 0x prefix (not #), we can safely strip everything after #.
        """
        if "#" in value:
            return value.split("#")[0].strip()
        return value

    @abstractmethod
    def _format_allowed_values(self) -> str:
        """Format the allowed values string. Override in subclasses."""
        raise NotImplementedError

    def __str__(self) -> str:
        """Return the string representation with allowed values."""
        if self.value is None:
            return str(self.value)
        return f"{self._get_value_str()}  # allowed: {self._format_allowed_values()}"

    @abstractmethod
    def _get_value_str(self) -> str:
        """Get the string representation of the current value. Override in subclasses."""
        raise NotImplementedError


EnumType = TypeVar("EnumType", bound=enum.Enum)
class Enum(_EnumBase[EnumType]):
    """A config value that is an enum."""

    def convert(self, value: str) -> EnumType:
        """Convert a string value to an enum."""
        value = self._strip_comment(value)
        parsed_enum_name = value.split(".")[-1]
        return self.value.__class__[parsed_enum_name]

    def _format_allowed_values(self) -> str:
        """Format allowed values as comma-separated member names."""
        enum_class = self.value.__class__
        return ", ".join(member.name for member in enum_class)

    def _get_value_str(self) -> str:
        """Get the member name."""
        return self.value.name

StrEnumType = TypeVar("StrEnumType", bound=enum.StrEnum)
class StrEnum(_EnumBase[StrEnumType]):
    """A config value that is an enum."""

    def convert(self, value: str) -> StrEnumType:
        """Convert a string value to an enum."""
        value = self._strip_comment(value)
        return self.value.__class__(value) # ty: ignore[invalid-return-type] # this is correct. ty says "Unknown | StrEnum"

    def _format_allowed_values(self) -> str:
        """Format allowed values as comma-separated member values."""
        enum_class = self.value.__class__
        return ", ".join(member.value for member in enum_class)

    def _get_value_str(self) -> str:
        """Get the member value."""
        return self.value.value

IntEnumType = TypeVar("IntEnumType", bound=enum.IntEnum)
class IntEnum(_EnumBase[IntEnumType]):
    """A config value that is an enum."""

    def convert(self, value: str) -> IntEnumType:
        """Convert a string value to an enum."""
        value = self._strip_comment(value)
        return self.value.__class__(int(value)) # ty: ignore[invalid-return-type] # ty says "Unknown | IntEnum"

    def _format_allowed_values(self) -> str:
        """Format allowed values as comma-separated name(value) pairs."""
        enum_class = self.value.__class__
        return ", ".join(f"{member.name}({member.value})" for member in enum_class)

    def _get_value_str(self) -> str:
        """Get the member value as string."""
        return str(self.value.value)

IntFlagType = TypeVar("IntFlagType", bound=enum.IntFlag)
class IntFlag(_EnumBase[IntFlagType]):
    """A config value that is an enum."""

    def convert(self, value: str) -> IntFlagType:
        """Convert a string value to an enum."""
        value = self._strip_comment(value)
        return self.value.__class__(int(value)) # ty: ignore[invalid-return-type] # ty says "Unknown | IntFlag"

    def _format_allowed_values(self) -> str:
        """Format allowed values as comma-separated name(value) pairs."""
        enum_class = self.value.__class__
        return ", ".join(f"{member.name}({member.value})" for member in enum_class)

    def _get_value_str(self) -> str:
        """Get the member value as string."""
        return str(self.value.value)

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

    def __init__(self, default: int = 0, base: int = HEXADECIMAL) -> None:  # noqa: D107
        super().__init__(default, base)

    def __str__(self) -> str:  # noqa: D105
        return f"0x{self.value:x}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer. from hexadecimal."""
        return int(value.removeprefix("0x"), 16)

class Octal(Integer):
    """A config value that represents octal."""

    def __init__(self, default: int = 0, base: int = OCTAL) -> None:  # noqa: D107
        super().__init__(default, base)

    def __str__(self) -> str:  # noqa: D105
        return f"0o{self.value:o}"

    def convert(self, value: str) -> int:
        """Convert a string value to an integer from octal."""
        return int(value.removeprefix("0o"), 8)

class Binary(BaseDataType[bytes | int]):
    """A config value that represents binary."""

    def __init__(self, default: bytes | int = 0) -> None:  # noqa: D107
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

    def __str__(self) -> str:
        """Return the string representation of the wrapped data type."""
        return str(self._data_type)

class _SequenceType(BaseDataType[Sequence[T]], Generic[T]):
    """A ABC for sequence types like List and Tuples."""

    separator = ","
    escape_char = "\\"

    @overload
    def __init__(self, default: Sequence[T]) -> None: ...
    @overload
    def __init__(self, *, data_type: BaseDataType[T]) -> None: ...
    @overload
    def __init__(
        self,
        default: Sequence[T],
        *,
        data_type: BaseDataType[T] = ...,
    ) -> None: ...

    def __init__(self, default: Sequence[T] = UNSET, *, data_type: BaseDataType[T] = UNSET) -> None:
        """Initialize the sequence data type."""
        if default is UNSET and data_type is UNSET:
            msg = "Sequence requires either a default with at least one element, or data_type to be specified."
            raise InvalidDefaultError(msg)
        if default is UNSET:
            default = []
        super().__init__(default)
        self._infer_type(default, data_type)

    def _infer_type(self, default: Sequence[T], data_type: BaseDataType[T]) -> None:
        if len(default) <= 0 and data_type is UNSET:
            msg = "Sequence default must have at least one element to infer type. or specify `data_type=<BaseDataType>`"
            raise InvalidDefaultError(msg)
        if data_type is UNSET:
            self._data_type = BaseDataType[T].cast(default[0])
        else:
            self._data_type = data_type

    def _convert(self, value: str) -> Sequence[T]:
        """Convert a string to a Sequence."""
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

class List(_SequenceType[T], Generic[T]):
    """A config value that is a list of values."""

    def convert(self, value: str) -> list[T]:
        """Convert a string to a list."""
        return list(super()._convert(value))

class Tuple(_SequenceType[T], Generic[T]):
    """A config value that is a tuple of values."""

    def convert(self, value: str) -> tuple[T, ...]:
        """Convert a string to a tuple."""
        return tuple(super()._convert(value))

class Set(BaseDataType[set[T]], Generic[T]):
    """A config value that is a set of values."""

    @overload
    def __init__(self, default: set[T]) -> None: ...
    @overload
    def __init__(self, *, data_type: BaseDataType[T]) -> None: ...
    @overload
    def __init__(
        self,
        default: set[T],
        *,
        data_type: BaseDataType[T] = ...,
    ) -> None: ...

    def __init__(self, default: set[T] = UNSET, *, data_type: BaseDataType[T] = UNSET) -> None:
        """Initialize the set data type."""
        if default is UNSET and data_type is UNSET:
            msg = "Set requires either a default with at least one element, or data_type to be specified."
            raise InvalidDefaultError(msg)
        if default is UNSET:
            default = set()
        super().__init__(default)
        self._infer_type(default, data_type)

    def _infer_type(self, default: set[T], data_type: BaseDataType[T]) -> None:
        if len(default) <= 0 and data_type is UNSET:
            msg = "Set default must have at least one element to infer type. or specify `data_type=<BaseDataType>`"
            raise InvalidDefaultError(msg)
        if data_type is UNSET:
            sample_element = default.pop()
            default.add(sample_element)
            self._data_type = BaseDataType[T].cast(sample_element)
        else:
            self._data_type = data_type

    def convert(self, value: str) -> set[T]:
        """Convert a string to a set."""
        if not value:
            return set()
        parts = value.split(",")
        return {self._data_type.convert(item.strip()) for item in parts}

    def __str__(self) -> str:
        """Return a string representation of the set."""
        return ",".join(str(item) for item in self.value)

KT = TypeVar("KT")
VT = TypeVar("VT")
class Dict(BaseDataType[dict[KT, VT]], Generic[KT, VT]):
    """A config value that is a dictionary of string keys and values of type T."""

    @overload
    def __init__(self, default: dict[KT, VT]) -> None: ...
    @overload
    def __init__(self, *, key_type: BaseDataType[KT], value_type: BaseDataType[VT]) -> None: ...
    @overload
    def __init__(
        self,
        default: dict[KT, VT],
        *,
        key_type: BaseDataType[KT] = ...,
        value_type: BaseDataType[VT] = ...,
    ) -> None: ...

    def __init__(
        self,
        default: dict[KT, VT] = UNSET,
        *,
        key_type: BaseDataType[KT] = UNSET,
        value_type: BaseDataType[VT] = UNSET,
    ) -> None:
        """Initialize the dict data type."""
        if default is UNSET and (key_type is UNSET or value_type is UNSET):
            msg = "Dict requires either a default with at least one key/value pair, or both key_type and value_type to be specified."  # noqa: E501
            raise InvalidDefaultError(msg)
        if default is UNSET:
            default = {}
        super().__init__(default)

        self._infer_key_type(default, key_type)
        self._infer_value_type(default, value_type)

    def _infer_key_type(self, default: dict[KT, VT], key_type: BaseDataType[KT]) -> None:
        """Infer the key type from the default dictionary if not provided."""
        if len(default.keys()) <= 0 and key_type is UNSET:
            msg = "Dict default must have at least one key element to infer type. or specify `key_type=<BaseDataType>`"
            raise InvalidDefaultError(msg)
        if key_type is UNSET:
            for key in default:
                self._key_data_type = BaseDataType[KT].cast(key)
                break
        else:
            self._key_data_type = key_type

    def _infer_value_type(self, default: dict[KT, VT], value_type: BaseDataType[VT]) -> None:
        """Infer the value type from the default dictionary if not provided."""
        if len(default.values()) <= 0 and value_type is UNSET:
            msg = "Dict default must have at least one value element to infer type. or specify `value_type=<BaseDataType>`"
            raise InvalidDefaultError(msg)
        if value_type is UNSET:
            for value in default.values():
                self._value_data_type = BaseDataType[VT].cast(value)
                break
        else:
            self._value_data_type = value_type

    def convert(self, value: str) -> dict[KT, VT]:
        """Convert a string to a dictionary."""
        if not value:
            return {}

        parts = value.split(",")
        result: dict[KT, VT] = {}
        for part in parts:
            if "=" not in part:
                msg = f"Invalid dictionary entry: {part}. Expected format key=value."
                raise ValueError(msg)
            key_str, val_str = part.split("=", 1)
            key = self._key_data_type.convert(key_str.strip())
            val = self._value_data_type.convert(val_str.strip())
            result[key] = val
        return result

    def __str__(self) -> str:
        """Return a string representation of the dictionary."""
        items = [
            f"{self._key_data_type.convert(str(k))}={self._value_data_type.convert(str(v))}"
            for k, v in self.value.items()
        ]
        return ",".join(items)

class _DateTimeKwargs(TypedDict, total=False):
    year: Required[int]
    month: Required[int]
    day: Required[int]
    hour: int
    minute: int
    second: int
    microsecond: int
    tzinfo: tzinfo | None
    fold: int

class DateTime(BaseDataType[datetime]):
    """A config value that is a datetime."""

    @overload
    def __init__(self, default: datetime = UNSET) -> None: ...
    @overload
    def __init__(self, **kwargs: Unpack[_DateTimeKwargs]) -> None: ...

    def __init__(self, default: datetime = UNSET, **kwargs: Unpack[_DateTimeKwargs]) -> None: # pyright: ignore[reportInconsistentOverload]
        """Initialize the datetime data type. Defaults to current datetime (datetime.now) if not provided."""
        if default is UNSET:
            try:
                default = datetime(**kwargs)  # ty: ignore[missing-argument]  # noqa: DTZ001
            except TypeError:
                default = datetime.now(tz=UTC)
        super().__init__(default)

    def convert(self, value: str) -> datetime:
        """Convert a string value to a datetime."""
        return datetime.fromisoformat(value)

    def __str__(self) -> str:
        """Return the string representation of the stored value."""
        return self.value.isoformat()

class _DateKwargs(TypedDict):
    year: int
    month: int
    day: int

class Date(BaseDataType[date]):
    """A config value that is a date."""

    @overload
    def __init__(self, default: date = UNSET) -> None: ...
    @overload
    def __init__(self, **kwargs: Unpack[_DateKwargs]) -> None: ...

    def __init__(self, default: date = UNSET, **kwargs: Unpack[_DateKwargs]) -> None: # pyright: ignore[reportInconsistentOverload]
        """Initialize the date data type. Defaults to current date if not provided."""
        if default is UNSET:
            default = date(**kwargs)
        super().__init__(default)

    def convert(self, value: str) -> date:
        """Convert a string value to a date."""
        return date.fromisoformat(value)

    def __str__(self) -> str:  # noqa: D105
        return self.value.isoformat()

class _TimeKwargs(TypedDict, total=False):
    hour: NotRequired[int]
    minute: NotRequired[int]
    second: NotRequired[int]
    microsecond: NotRequired[int]
    tzinfo: tzinfo | None
    fold: NotRequired[int]

class Time(BaseDataType[time]):
    """A config value that is a time."""

    @overload
    def __init__(self, default: time = UNSET) -> None: ...
    @overload
    def __init__(self, **kwargs: Unpack[_TimeKwargs]) -> None: ...

    def __init__(self, default: time = UNSET, **kwargs: Unpack[_TimeKwargs]) -> None:
        """Initialize the time data type. Defaults to current time if not provided."""
        if default is UNSET:
            default = time(**kwargs) # ty: ignore[missing-argument]
        super().__init__(default)

    def convert(self, value: str) -> time:
        """Convert a string value to a time."""
        return time.fromisoformat(value)

    def __str__(self) -> str:  # noqa: D105
        return self.value.isoformat()

class _TimeDeltaKwargs(TypedDict, total=False):
    days: NotRequired[float]
    seconds: NotRequired[float]
    microseconds: NotRequired[float]
    milliseconds: NotRequired[float]
    minutes: NotRequired[float]
    hours: NotRequired[float]
    weeks: NotRequired[float]

class TimeDelta(BaseDataType[timedelta]):
    """A config value that is a timedelta."""

    def __init__(
        self,
        default: timedelta = UNSET,
        **kwargs: Unpack[_TimeDeltaKwargs],
    ) -> None:
        """Initialize the timedelta data type. Defaults to 0 if not provided."""
        if default is UNSET:
            default = timedelta(**kwargs)
        super().__init__(default)

    def convert(self, value: str) -> timedelta:
        """Convert a string value to a timedelta."""
        return timedelta(seconds=float(value))

    def __str__(self) -> str:  # noqa: D105
        return str(self.value.total_seconds())
