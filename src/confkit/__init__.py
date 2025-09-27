"""Module that provides the main interface for the confkit package.

It includes the Config class and various data types used for configuration values.
"""

from .config import Config
from .data_types import (
    BaseDataType,
    Binary,
    Boolean,
    Enum,
    Float,
    Hex,
    Integer,
    IntEnum,
    IntFlag,
    List,
    NoneType,
    Octal,
    Optional,
    StrEnum,
    String,
)
from .exceptions import InvalidConverterError, InvalidDefaultError

__all__ = [
    "BaseDataType",
    "Binary",
    "Boolean",
    "Config",
    "Enum",
    "Float",
    "Hex",
    "IntEnum",
    "IntFlag",
    "Integer",
    "InvalidConverterError",
    "InvalidDefaultError",
    "List",
    "NoneType",
    "Octal",
    "Optional",
    "StrEnum",
    "String",
]
