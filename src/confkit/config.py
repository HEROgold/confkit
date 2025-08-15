"""Module for a config descriptor.

The Config descriptor is used to read and write config values from a ConfigParser object.
It is used to create a descriptor for config values, preserving type information.
It also provides a way to set default values and to set config values using decorators.
"""
from __future__ import annotations

from functools import wraps
from typing import TYPE_CHECKING, ClassVar, cast, overload

from .data_types import BaseDataType, Boolean, Float, Integer, NoneType, Optional, String
from .exceptions import InvalidConverterError, InvalidDefaultError
from .sentinels import UNSET

if TYPE_CHECKING:
    from collections.abc import Callable
    from configparser import ConfigParser
    from pathlib import Path


class Config[VT]:
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
        @overload
        def __init__(self: Config[str], default: str) -> None: ...
        @overload
        def __init__(self: Config[None], default: None) -> None: ...
        @overload
        def __init__(self: Config[bool], default: bool) -> None: ...  # noqa: FBT001
        @overload
        def __init__(self: Config[int], default: int) -> None: ...
        @overload
        def __init__(self: Config[float], default: float) -> None: ...
        @overload
        def __init__(self: Config[str | None], default: str, *, optional: bool) -> None: ...
        @overload
        def __init__(self: Config[None], default: None, *, optional: bool) -> None: ...
        @overload
        def __init__(self: Config[bool | None], default: bool, *, optional: bool) -> None: ...  # noqa: FBT001
        @overload
        def __init__(self: Config[int | None], default: int, *, optional: bool) -> None: ...
        @overload
        def __init__(self: Config[float | None], default: float, *, optional: bool) -> None: ...
        @overload # Custom data type, like Enum's or custom class.
        def __init__(self, default: BaseDataType[VT]) -> None: ...

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
        self.optional = optional or Config.optional # Be truthy when either one is true.

        if not self.optional and default is UNSET:
            msg = "Default value cannot be None when optional is False."
            raise InvalidDefaultError(msg)

        self._initialize_data_type(default)
        self._validate_init()
        self._read_parser()

    def _initialize_data_type(self, default: VT | None | BaseDataType[VT]) -> None:
        """Initialize the data type based on the default value."""
        if not self.optional and default is not None:
            self._data_type = self._cast_data_type(default)
        else:
            self._data_type = self._cast_optional_data_type(default)

    def _cast_optional_data_type(self, default: VT | None | BaseDataType[VT]) -> BaseDataType[VT | None]:
        """Convert the default value to an Optional data type."""
        if default is None:
            return cast("BaseDataType[VT | None]", NoneType())
        return Optional(self._cast_data_type(default))

    @staticmethod
    def _cast_data_type(default: VT | BaseDataType[VT]) -> BaseDataType[VT]:
        """Convert the default value to a BaseDataType."""
        # We use Cast to shut up type checkers, as we know primitive types will be correct.
        # If a custom type is passed, it should be a BaseDataType subclass, which already has the correct types.
        match default:
            case bool():
                data_type = cast("BaseDataType[VT]", Boolean(default))
            case None:
                data_type = cast("BaseDataType[VT]", NoneType())
            case int():
                data_type = cast("BaseDataType[VT]", Integer(default))
            case float():
                data_type = cast("BaseDataType[VT]", Float(default))
            case str():
                data_type = cast("BaseDataType[VT]", String(default))
            case BaseDataType():
                data_type = default
            case _:
                msg = (
                    f"Unsupported default value type: {type(default).__name__}. "
                    "Use a BaseDataType subclass for custom types."
                )
                raise InvalidDefaultError(msg)
        return data_type

    def _read_parser(self) -> None:
        """Ensure the parser has read the file at initialization. Avoids rewriting the file when settings are already set."""
        if not self._has_read_config:
            Config._parser.read(Config._file)
            Config._has_read_config = True

    def _validate_init(self) -> None:
        """Validate the config descriptor, ensuring it's properly set up."""
        self.validate_file()
        self.validate_parser()

    def convert(self, value: str) -> VT:
        """Convert the value to the desired type using the given converter method."""
        # Ignore the type error of VT, type checkers don't like None as an option
        # We handle it using the `optional` flag. so we can safely ignore it.
        return self._data_type.convert(value) # type: ignore[reportReturnType]

    @staticmethod
    def set_parser(parser: ConfigParser) -> None:
        """Set the parser for ALL descriptors."""
        Config._parser = parser

    @staticmethod
    def set_file(file: Path) -> None:
        """Set the file for ALL descriptors."""
        Config._file = file

    def validate_strict_type(self) -> None:
        """Validate the type of the converter matches the desired type."""
        if not Config.validate_types:
            return
        if self._data_type.convert is UNSET:
            msg = "Converter is not set."
            raise InvalidConverterError(msg)

        config_value = Config._parser.get(self._section, self._setting)
        converted_value = self.convert(config_value)
        converted_type = type(converted_value)

        if not self._data_type.validate():
            msg = f"Invalid value for {self._section}.{self._setting}: {converted_value}"
            raise InvalidConverterError(msg)

        if self.optional and converted_type in (type(self._data_type.default), type(None)):
            # Allow None or the same type as the default value to be returned by the converter when _optional is True.
            return
        if type(converted_value) is not type(self._data_type.default):
            msg = f"Converter does not return the same type as the default value <{type(self._data_type.default)}>."
            raise InvalidConverterError(msg)

    def validate_file(self) -> None:
        """Validate the config file."""
        if Config._file is UNSET:
            msg = f"Config file is not set. use {Config.__name__}.set_file() to set it."
            raise ValueError(msg)

    def validate_parser(self) -> None:
        """Validate the config parser."""
        if Config._parser is UNSET:
            msg = f"Config parser is not set. use {Config.__name__}.set_parser() to set it."
            raise ValueError(msg)

    def __set_name__(self, owner: type, name: str) -> None:
        """Set the name of the attribute to the name of the descriptor."""
        self.name = name
        self._section = owner.__name__
        self._setting = name
        self._ensure_option()
        self._original_value = Config._parser.get(self._section, self._setting) or self._data_type.default
        self.private = f"_{self._section}_{self._setting}_{self.name}"

    def _ensure_section(self) -> None:
        """Ensure the section exists in the config file. Creates one if it doesn't exist."""
        if not self._parser.has_section(self._section):
            self._parser.add_section(self._section)

    def _ensure_option(self) -> None:
        """Ensure the option exists in the config file. Creates one if it doesn't exist."""
        self._ensure_section()
        if not self._parser.has_option(self._section, self._setting):
            Config._set(self._section, self._setting, self._data_type.default)

    def __get__(self, obj: object, obj_type: object) -> VT:
        """Get the value of the attribute."""
        # obj_type is the class in which the variable is defined
        # so it can be different than type of VT
        # but we don't need obj or it's type to get the value from config in our case.
        self.validate_strict_type()
        return self.convert(Config._parser.get(self._section, self._setting))

    def __set__(self, obj: object, value: VT) -> None:
        """Set the value of the attribute."""
        Config._set(self._section, self._setting, value)
        setattr(obj, self.private, value)

    @staticmethod
    def _sanitize_str(value: str) -> str:
        """Escape the percent sign in the value."""
        return value.replace("%", "%%")

    @staticmethod
    def _set(section: str, setting: str, value: VT) -> None:
        """Set a config value, and write it to the file."""
        if not Config._parser.has_section(section):
            Config._parser.add_section(section)
        sanitized_str = Config._sanitize_str(str(value))
        Config._parser.set(section, setting, sanitized_str)
        if Config.write_on_edit:
            with Config._file.open("w") as f:
                Config._parser.write(f)

    @staticmethod
    def set(section: str, setting: str, value: VT):  # noqa: ANN205
        """Set a config value using this descriptor."""

        def wrapper[F, **P](func: Callable[P, F]) -> Callable[P, F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                Config._set(section, setting, value)
                return func(*args, **kwargs)

            return inner
        return wrapper

    @staticmethod
    def with_setting[OVT](setting: Config[OVT]):  # noqa: ANN205
        """Insert a config value into **kwargs to a given method/function using this decorator."""
        def wrapper[F, **P](func: Callable[P, F]) -> Callable[P, F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                kwargs[setting.name] = setting.convert(Config._parser.get(setting._section, setting._setting))
                return func(*args, **kwargs)

            return inner
        return wrapper

    @staticmethod
    def as_kwarg(section: str, setting: str, name: str | None = None, default: VT = UNSET):  # noqa: ANN205
        """Insert a config value into **kwargs to a given method/function using this descriptor.

        Use kwarg.get(`name`) to get the value.
        `name` is the name the kwarg gets if passed, if None, it will be the same as `setting`.
        Section parameter is just for finding the config value.
        """
        if name is None:
            name = setting
        if default is UNSET and not Config._parser.has_option(section, setting):
            msg = f"Config value {section=} {setting=} is not set. and no default value is given."
            raise ValueError(msg)

        def wrapper[F, **P](func: Callable[P, F]) -> Callable[P, F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                if default is not UNSET:
                    Config._set_default(section, setting, default)
                kwargs[name] = Config._parser.get(section, setting) # ty: ignore[invalid-assignment]
                return func(*args, **kwargs)

            return inner
        return wrapper

    @staticmethod
    def _set_default(section: str, setting: str, value: VT) -> None:
        if Config._parser.get(section, setting, fallback=UNSET) is UNSET:
            Config._set(section, setting, value)

    @staticmethod
    def default(section: str, setting: str, value: VT):  # noqa: ANN205
        """Set a default config value if none are set yet using this descriptor."""

        def wrapper[F, **P](func: Callable[P, F]) -> Callable[P, F]:
            @wraps(func)
            def inner(*args: P.args, **kwargs: P.kwargs) -> F:
                Config._set_default(section, setting, value)
                return func(*args, **kwargs)

            return inner
        return wrapper
