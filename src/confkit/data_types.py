"""Module that contains the base data types used in the config system."""

from __future__ import annotations

import enum
from abc import ABC, abstractmethod

from .exceptions import InvalidConverterError


class BaseDataType[T](ABC):
    """Base class used for Config descriptors to define a data type."""

    def __init__(self, default: T) -> None:
        """Initialize the base data type."""
        self.default = default
        self.value = default

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
                        if isinstance(self.value, type_arg):
                            return True
                    msg = f"Value {self.value} is not any of {type_args}."
                    raise InvalidConverterError(msg)
        msg = "This should not have raised. Report to the library maintainers with code: `DTBDT38`"
        raise TypeError(msg)

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

    def __init__(self) -> None:
        """Initialize the NoneType data type."""
        super().__init__(None)

    def convert(self, value: str) -> None:
        """Convert a string value to None."""
        if value.lower().strip() in {"none", "null", "nil", ""}:
            return
        msg = f"Cannot convert {value} to None."
        raise ValueError(msg)


class String(BaseDataType[str]):
    """A config value that is a string."""

    def convert(self, value: str) -> str:
        """Convert a string value to a string."""
        return value


class Float(BaseDataType[float]):
    """A config value that is a float."""

    def convert(self, value: str) -> float:
        """Convert a string value to a float."""
        return float(value)


class Boolean(BaseDataType[bool]):
    """A config value that is a boolean."""

    def convert(self, value: str) -> bool:
        """Convert a string value to a boolean."""
        if value.lower() in {"true", "1", "yes"}:
            return True
        if value.lower() in {"false", "0", "no"}:
            return False
        msg = f"Cannot convert {value} to boolean."
        raise ValueError(msg)


class Integer(BaseDataType[int]):
    """A config value that is an integer."""

    def convert(self, value: str) -> int:
        """Convert a string value to an integer."""
        return int(value)

class Optional[T](BaseDataType[T | None]):
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

    def convert(self, value: str) -> T | None:
        """Convert a string value to the optional type."""
        try:
            return self._none_type.convert(value)
        except ValueError:
            return self._data_type.convert(value)

    def validate(self) -> bool:
        """Validate that the value is of the wrapped data type or None."""
        if self._data_type.value is None:
            return True
        return self._data_type.validate()
