"""Module for a config descriptor.

The Config descriptor is used to read and write config values from a ConfigParser object.
It is used to create a descriptor for config values, preserving type information.
It also provides a way to set default values and to set config values using decorators.
"""
from __future__ import annotations

import warnings
from functools import wraps
from types import NoneType
from typing import TYPE_CHECKING, Any, ClassVar, Generic, Literal, ParamSpec, TypeVar, overload

from .data_types import BaseDataType, Optional
from .exceptions import InvalidConverterError, InvalidDefaultError
from .sentinels import UNSET

if TYPE_CHECKING:
    from collections.abc import Callable
    from configparser import ConfigParser
    from pathlib import Path

# Type variables for Python 3.10+ (pre-PEP 695) compatibility
VT = TypeVar("VT")
OVT = TypeVar("OVT")  # Separate TypeVar for nested generic to avoid scope collision
F = TypeVar("F")
P = ParamSpec("P")

class Config(Generic[VT]):
    """A descriptor for config values, preserving type information.

    the ValueType (VT) is the type you want the config value to be.
    """

    validate_types: ClassVar[bool] = True # Validate that the converter returns the same type as the default value. (not strict)
    write_on_edit: ClassVar[bool] = True # Write to the config file when updating a value.
    optional: bool = False # if True, allows None as an extra type when validating types. (both instance and class variables.)

    _parser: ConfigParser = UNSET
    _file: Path = UNSET
    _has_read_config: bool = False

    if TYPE_CHECKING:
        # Overloads for type checkers to understand the different settings of the Config descriptors.
        @overload # Custom data type, like Enum's or custom class.
        def __init__(self, default: BaseDataType[VT]) -> None: ...
        @overload
        def __init__(self, default: VT) -> None: ...
        # Specify the states of optional explicitly for type checkers.
        @overload
        def __init__(self: Config[VT], default: VT, *, optional: Literal[False]) -> None: ... # pyright: ignore[reportInvalidTypeVarUse]
        @overload
        def __init__(self: Config[VT], default: BaseDataType[VT], *, optional: Literal[False]) -> None: ... # pyright: ignore[reportInvalidTypeVarUse]
        @overload
        def __init__(self: Config[VT | None], default: VT, *, optional: Literal[True]) -> None: ... # pyright: ignore[reportInvalidTypeVarUse]
        @overload
        def __init__(self: Config[VT | None], default: BaseDataType[VT], *, optional: Literal[True]) -> None: ... # pyright: ignore[reportInvalidTypeVarUse]

    # type Complains about the self and default overloads for None and str
    # they are explicitly set for type checkers, the actual representation doesn't matter
    # in runtime, as VT is allowed to be any type.
    def __init__( # type: ignore[reportInconsistentOverload]
        self,
        default: VT | None | BaseDataType[VT] = UNSET,
        *,
        optional: bool = False,
    ) -> None:
        """Initialize the config descriptor with a default value.

        Validate that parser and filepath are present.
        """
        cls = self.__class__
        self.optional = optional or cls.optional # Be truthy when either one is true.

        if not self.optional and default is UNSET:
            msg = "Default value cannot be None when optional is False."
            raise InvalidDefaultError(msg)

        self._initialize_data_type(default)
        self._validate_init()
        self._read_parser()

    def __init_subclass__(cls) -> None:
        """Allow for multiple config files/parsers without conflicts."""
        super().__init_subclass__()

        parent = cls._find_parent()

        cls.validate_types = parent.validate_types
        cls.write_on_edit = parent.write_on_edit
        cls._parser = parent._parser  # noqa: SLF001
        cls._file = parent._file  # noqa: SLF001
        cls._has_read_config = parent._has_read_config  # noqa: SLF001

    @classmethod
    def _find_parent(cls) -> type[Config[Any]]:
        for base in cls.__bases__:
            if issubclass(base, Config):
                parent = base
                break
        else:
            parent = Config
        return parent

    def _initialize_data_type(self, default: VT | None | BaseDataType[VT]) -> None:
        """Initialize the data type based on the default value."""
        if not self.optional and default is not None:
            self._data_type = BaseDataType[VT].cast(default)
        else:
            self._data_type = BaseDataType[VT].cast_optional(default)

    def _read_parser(self) -> None:
        """Ensure the parser has read the file at initialization. Avoids rewriting the file when settings are already set."""
        if not self._has_read_config:
            self._parser.read(self._file)
            self._has_read_config = True

    def _validate_init(self) -> None:
        """Validate the config descriptor, ensuring it's properly set up."""
        self.validate_file()
        self.validate_parser()

    def convert(self, value: str) -> VT:
        """Convert the value to the desired type using the given converter method."""
        # Ignore the type error of VT, type checkers don't like None as an option
        # We handle it using the `optional` flag, or using Optional DataType. so we can safely ignore it.
        return self._data_type.convert(value) # type: ignore[reportReturnType]

    @staticmethod
    def _warn_base_class_usage() -> None:
        """Warn users that setting parser/file on the base class can lead to unexpected behavior."""
        warnings.warn("<Config> is the base class. Subclass <Config> to avoid unexpected behavior.", stacklevel=2)

    @classmethod
    def set_parser(cls, parser: ConfigParser) -> None:
        """Set the parser for ALL descriptors."""
        if cls is Config:
            # Warn users that setting this value on the base class can lead to unexpected behavoir.
            # Tell the user to subclass <Config> first.
            cls._warn_base_class_usage()
        cls._parser = parser

    @classmethod
    def set_file(cls, file: Path) -> None:
        """Set the file for ALL descriptors."""
        if cls is Config:
            # Warn users that setting this value on the base class can lead to unexpected behavoir.
            # Tell the user to subclass <Config> first.
            cls._warn_base_class_usage()
        cls._file = file

    def validate_strict_type(self) -> None:
        """Validate the type of the converter matches the desired type."""
        if self._data_type.convert is UNSET:
            msg = "Converter is not set."
            raise InvalidConverterError(msg)

        cls = self.__class__
        self.__config_value = cls._parser.get(self._section, self._setting)
        self.__converted_value = self.convert(self.__config_value)

        if not cls.validate_types:
            return

        self.__converted_type = type(self.__converted_value)
        default_value_type = type(self._data_type.default)

        is_optional = self.optional or isinstance(self._data_type, Optional)
        if (is_optional) and self.__converted_type in (default_value_type, NoneType):
            # Allow None or the same type as the default value to be returned by the converter when _optional is True.
            return
        if self.__converted_type is not default_value_type:
            msg = f"Converter does not return the same type as the default value <{default_value_type}> got <{self.__converted_type}>."  # noqa: E501
            raise InvalidConverterError(msg)

        # Set the data_type value. ensuring validation works as expected.
        self._data_type.value = self.__converted_value
        if not self._data_type.validate():
            msg = f"Invalid value for {self._section}.{self._setting}: {self.__converted_value}"
            raise InvalidConverterError(msg)

    @classmethod
    def validate_file(cls) -> None:
        """Validate the config file."""
        if cls._file is UNSET:
            msg = f"Config file is not set. use {cls.__name__}.set_file() to set it."
            raise ValueError(msg)

    @classmethod
    def validate_parser(cls) -> None:
        """Validate the config parser."""
        if cls._parser is UNSET:
            msg = f"Config parser is not set. use {cls.__name__}.set_parser() to set it."
            raise ValueError(msg)

    def __set_name__(self, owner: type, name: str) -> None:
        """Set the name of the attribute to the name of the descriptor."""
        self.name = name
        self._section = owner.__name__
        self._setting = name
        self._ensure_option()
        cls = self.__class__
        self._original_value = cls._parser.get(self._section, self._setting) or self._data_type.default
        self.private = f"_{self._section}_{self._setting}_{self.name}"

    def _ensure_section(self) -> None:
        """Ensure the section exists in the config file. Creates one if it doesn't exist."""
        if not self._parser.has_section(self._section):
            self._parser.add_section(self._section)

    def _ensure_option(self) -> None:
        """Ensure the option exists in the config file. Creates one if it doesn't exist."""
        self._ensure_section()
        if not self._parser.has_option(self._section, self._setting):
            cls = self.__class__
            cls._set(self._section, self._setting, self._data_type)

    def __get__(self, obj: object, obj_type: object) -> VT:
        """Get the value of the attribute."""
        # obj_type is the class in which the variable is defined
        # so it can be different than type of VT
        # but we don't need obj or it's type to get the value from config in our case.
        self.validate_strict_type()
        return self.__converted_value

    def __set__(self, obj: object, value: VT) -> None:
        """Set the value of the attribute."""
        self._data_type.value = value
        cls = self.__class__
        cls._set(self._section, self._setting, self._data_type)
        setattr(obj, self.private, value)

    @staticmethod
    def _sanitize_str(value: str) -> str:
        """Escape the percent sign in the value."""
        return value.replace("%", "%%")

    @classmethod
    def _set(cls, section: str, setting: str, value: VT | BaseDataType[VT] | BaseDataType[VT | None]) -> None:
        """Set a config value, and write it to the file."""
        if not cls._parser.has_section(section):
            cls._parser.add_section(section)

        sanitized_str = cls._sanitize_str(str(value))
        cls._parser.set(section, setting, sanitized_str)

        if cls.write_on_edit:
            cls.write()


    @classmethod
    def write(cls) -> None:
        """Write the config parser to the file."""
        cls.validate_file()
        with cls._file.open("w") as f:
            cls._parser.write(f)

    @classmethod
    def set(cls, section: str, setting: str, value: VT):  # noqa: ANN206
        """Set a config value using this descriptor."""

        def wrapper(func: Callable[..., F]) -> Callable[..., F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                cls._set(section, setting, value)
                return func(*args, **kwargs)

            return inner
        return wrapper


    @classmethod
    def with_setting(cls, setting: Config[OVT]):  # noqa: ANN206
        """Insert a config value into **kwargs to the wrapped method/function using this decorator."""
        def wrapper(func: Callable[..., F]) -> Callable[..., F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                kwargs[setting.name] = setting.convert(cls._parser.get(setting._section, setting._setting))
                return func(*args, **kwargs)

            return inner
        return wrapper


    @classmethod
    def with_kwarg(cls, section: str, setting: str, name: str | None = None, default: VT = UNSET):  # noqa: ANN206
        """Insert a config value into **kwargs to the wrapped method/function using this descriptor.

        Use kwarg.get(`name`) to get the value.
        `name` is the name the kwarg gets if passed, if None, it will be the same as `setting`.
        Section parameter is just for finding the config value.
        """
        if name is None:
            name = setting
        if default is UNSET and not cls._parser.has_option(section, setting):
            msg = f"Config value {section=} {setting=} is not set. and no default value is given."
            raise ValueError(msg)

        def wrapper(func: Callable[..., F]) -> Callable[..., F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                if default is not UNSET:
                    cls._set_default(section, setting, default)
                kwargs[name] = cls._parser.get(section, setting) # ty: ignore[invalid-assignment]
                return func(*args, **kwargs)

            return inner
        return wrapper

    @classmethod
    def _set_default(cls, section: str, setting: str, value: VT) -> None:
        if cls._parser.get(section, setting, fallback=UNSET) is UNSET:
            cls._set(section, setting, value)

    @classmethod
    def default(cls, section: str, setting: str, value: VT):  # noqa: ANN206
        """Set a default config value if none are set yet using this descriptor."""
        def wrapper(func: Callable[..., F]) -> Callable[..., F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                cls._set_default(section, setting, value)
                return func(*args, **kwargs)

            return inner
        return wrapper
