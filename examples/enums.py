
"""
Examples demonstrating enum support in confkit.

This example shows:
1. Using standard Python Enum classes with confkit
2. Using StrEnum, IntEnum, and IntFlag with confkit
3. Type-safe configuration with enums
4. Optional enum configurations

Run with: python enums.py
"""

from configparser import ConfigParser
from enum import IntEnum, IntFlag, StrEnum, auto
from pathlib import Path

from confkit import Config
from confkit.data_types import Enum, IntEnum as ConfigIntEnum
from confkit.data_types import IntFlag as ConfigIntFlag
from confkit.data_types import Optional, StrEnum as ConfigStrEnum

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


# Define enum classes for configuration
class LogLevel(StrEnum):
    """String-based enum for log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Priority(IntEnum):
    """Integer-based enum for task priorities."""
    LOW = 0
    MEDIUM = 5
    HIGH = 10


class Permission(IntFlag):
    """Integer flag enum for permission bits."""
    NONE = 0
    READ = 1
    WRITE = 2
    EXECUTE = 4
    ALL = READ | WRITE | EXECUTE  # 7


class ServerConfig:
    """Server configuration using various enum types."""
    
    # String enum configuration
    log_level = Config(ConfigStrEnum(LogLevel.INFO))
    
    # Integer enum configuration
    default_priority = Config(ConfigIntEnum(Priority.MEDIUM))
    
    # Integer flag configuration
    default_permission = Config(ConfigIntFlag(Permission.READ))
    
    # Optional enum configuration (can be None)
    fallback_level = Config(Optional(ConfigStrEnum(LogLevel.ERROR)))
    
    # Standard enum configuration
    environment = Config(Enum(LogLevel.INFO))
