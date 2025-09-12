"""Module for a config descriptor.

The Config descriptor is used to read and write config values from a ConfigParser object.
It is used to create a descriptor for config values, preserving type information.
It also provides a way to set default values and to set config values using decorators.
"""
from __future__ import annotations

import inspect
from configparser import ConfigParser as ConfigParserType
from functools import wraps
from pathlib import Path as PathType
from types import NoneType
from typing import TYPE_CHECKING, ClassVar, overload

from .data_types import BaseDataType, Optional
from .exceptions import InvalidConverterError, InvalidDefaultError
from .sentinels import UNSET

if TYPE_CHECKING:
    from collections.abc import Callable
    from configparser import ConfigParser
    from pathlib import Path


class Config[VT]:
    """A descriptor for config values, preserving type information.

    the ValueType (VT) is the type you want the config value to be.
    
    Supports automatic instance-level configuration files for classes using Config descriptors.
    When Config descriptors are used in a class, that class automatically gets its own 
    config file based on the class location in the source code.
    """

    validate_types: ClassVar[bool] = True # Validate that the converter returns the same type as the default value. (not strict)
    write_on_edit: ClassVar[bool] = True # Write to the config file when updating a value.
    optional: bool = False # if True, allows None as an extra type when validating types. (both instance and class variables.)

    # Class-level settings (global fallback)
    _parser: ConfigParser = UNSET
    _file: Path = UNSET
    _has_read_config: bool = False
    
    # Instance-level settings (per class that uses Config descriptors)
    _instance_parsers: ClassVar[dict[type, ConfigParser]] = {}
    _instance_files: ClassVar[dict[type, Path]] = {}
    _instance_read_configs: ClassVar[dict[type, bool]] = {}

    @classmethod
    def _setup_instance_config(cls, owner_class: type) -> None:
        """Set up instance-level config for a class that uses Config descriptors.
        
        Automatically generates a unique config file for the class based on 
        the source file location and class name.
        """
        if owner_class in cls._instance_parsers:
            # Already set up
            return
            
        # Generate unique filename based on AST location
        frame = inspect.currentframe()
        filename = "unknown"
        lineno = 0
        
        # Walk up the call stack to find the frame where the class was defined
        current_frame = frame
        while current_frame:
            code = current_frame.f_code
            # Look for a frame that's not in this module
            if not code.co_filename.endswith('config.py'):
                filename = code.co_filename
                lineno = current_frame.f_lineno
                break
            current_frame = current_frame.f_back
            
        # Create unique but reproducible filename
        base_name = f"{owner_class.__name__}_{PathType(filename).stem}_{lineno}.ini"
        instance_file = PathType(base_name)
        
        # Initialize instance-level parser and file
        instance_parser = ConfigParserType()
        cls._instance_parsers[owner_class] = instance_parser
        cls._instance_files[owner_class] = instance_file  
        cls._instance_read_configs[owner_class] = False

    def _get_parser(self) -> ConfigParser:
        """Get the appropriate parser (instance-level or class-level)."""
        if hasattr(self, '_section') and self._section:
            # Try to find the class that owns this descriptor
            for cls, parser in Config._instance_parsers.items():
                if cls.__name__ == self._section:
                    return parser
        # Fall back to class-level parser
        return Config._parser
        
    def _get_file(self) -> Path:
        """Get the appropriate file path (instance-level or class-level)."""
        if hasattr(self, '_section') and self._section:
            # Try to find the class that owns this descriptor
            for cls, file_path in Config._instance_files.items():
                if cls.__name__ == self._section:
                    return file_path
        # Fall back to class-level file
        return Config._file

    def _get_read_config_state(self) -> bool:
        """Get the read config state (instance-level or class-level)."""
        if hasattr(self, '_section') and self._section:
            # Try to find the class that owns this descriptor
            for cls in Config._instance_read_configs:
                if cls.__name__ == self._section:
                    return Config._instance_read_configs[cls]
        # Fall back to class-level state
        return Config._has_read_config
        
    def _set_read_config_state(self, state: bool) -> None:
        """Set the read config state (instance-level or class-level)."""
        if hasattr(self, '_section') and self._section:
            # Try to find the class that owns this descriptor
            for cls in Config._instance_read_configs:
                if cls.__name__ == self._section:
                    Config._instance_read_configs[cls] = state
                    return
        # Fall back to class-level state
        Config._has_read_config = state

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
            self._data_type = BaseDataType[VT].cast(default)
        else:
            self._data_type = BaseDataType[VT].cast_optional(default)

    def _read_parser(self) -> None:
        """Ensure the parser has read the file at initialization. Avoids rewriting the file when settings are already set."""
        if not self._get_read_config_state():
            parser = self._get_parser()
            file_path = self._get_file()
            parser.read(file_path)
            self._set_read_config_state(True)

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
    def set_parser(parser: ConfigParser) -> None:
        """Set the parser for ALL descriptors."""
        Config._parser = parser

    @staticmethod
    def set_file(file: Path) -> None:
        """Set the file for ALL descriptors."""
        Config._file = file

    def validate_strict_type(self) -> None:
        """Validate the type of the converter matches the desired type."""
        if self._data_type.convert is UNSET:
            msg = "Converter is not set."
            raise InvalidConverterError(msg)

        self.__config_value = Config._parser.get(self._section, self._setting)
        self.__converted_value = self.convert(self.__config_value)

        if not Config.validate_types:
            return
        if not self._data_type.validate():
            msg = f"Invalid value for {self._section}.{self._setting}: {self.__converted_value}"
            raise InvalidConverterError(msg)

        self.__converted_type = type(self.__converted_value)
        default_value_type = type(self._data_type.default)

        is_optional = self.optional or isinstance(self._data_type, Optional)
        if (is_optional) and self.__converted_type in (default_value_type, NoneType):
            # Allow None or the same type as the default value to be returned by the converter when _optional is True.
            return
        if self.__converted_type is not default_value_type:
            msg = f"Converter does not return the same type as the default value <{default_value_type}> got <{self.__converted_type}>."  # noqa: E501
            raise InvalidConverterError(msg)

    @staticmethod
    def validate_file() -> None:
        """Validate the config file."""
        if Config._file is UNSET:
            msg = f"Config file is not set. use {Config.__name__}.set_file() to set it."
            raise ValueError(msg)

    @staticmethod
    def validate_parser() -> None:
        """Validate the config parser."""
        if Config._parser is UNSET:
            msg = f"Config parser is not set. use {Config.__name__}.set_parser() to set it."
            raise ValueError(msg)

    def __set_name__(self, owner: type, name: str) -> None:
        """Set the name of the attribute to the name of the descriptor."""
        # Set up instance-level config for the owner class
        Config._setup_instance_config(owner)
        
        self.name = name
        self._section = owner.__name__
        self._setting = name
        self._ensure_option()
        parser = self._get_parser()
        self._original_value = parser.get(self._section, self._setting) or self._data_type.default
        self.private = f"_{self._section}_{self._setting}_{self.name}"

    def _ensure_section(self) -> None:
        """Ensure the section exists in the config file. Creates one if it doesn't exist."""
        if not self._parser.has_section(self._section):
            self._parser.add_section(self._section)

    def _ensure_option(self) -> None:
        """Ensure the option exists in the config file. Creates one if it doesn't exist."""
        self._ensure_section()
        if not self._parser.has_option(self._section, self._setting):
            Config._set(self._section, self._setting, str(self._data_type))

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
        Config._set(self._section, self._setting, str(self._data_type))
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
            Config.write()

    @staticmethod
    def write() -> None:
        """Write the config parser to the file."""
        Config.validate_file()
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
