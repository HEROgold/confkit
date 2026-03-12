"""Tests for automatic enum type conversion in Config descriptors.

Tests that StrEnum, IntEnum, IntFlag, and Enum defaults are automatically
wrapped in their corresponding data type converters when used with Config.
"""

import enum
from enum import IntEnum, IntFlag, StrEnum
from pathlib import Path

from confkit import Config as ConfigBase
from confkit.data_types import Enum as ConfigEnum
from confkit.data_types import IntEnum as ConfigIntEnum
from confkit.data_types import IntFlag as ConfigIntFlag
from confkit.data_types import StrEnum as ConfigStrEnum
from confkit.parsers import IniParser


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
    ALL = READ | WRITE | EXECUTE


class StandardEnum(enum.Enum):
    """Standard enum for testing."""

    OPTION_A = 1
    OPTION_B = 2


class TestStrEnumAutoWrapping:
    """Test that StrEnum instances are automatically wrapped."""

    def test_strenum_auto_wraps_to_config_strenum(self, tmp_path: Path) -> None:
        """Test that Config(StrEnum.value) auto-wraps to Config(ConfigStrEnum(StrEnum.value))."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("")

        class StrEnumConfig(ConfigBase):
            pass

        StrEnumConfig.set_parser(IniParser())
        StrEnumConfig.set_file(config_file)
        StrEnumConfig._has_read_config = False

        class AppConfig:
            log_level = StrEnumConfig(LogLevel.INFO)

        descriptor = AppConfig.__dict__["log_level"]
        assert isinstance(descriptor._data_type, ConfigStrEnum)
        assert descriptor._data_type.value == LogLevel.INFO


class TestIntEnumAutoWrapping:
    """Test that IntEnum instances are automatically wrapped."""

    def test_intenum_auto_wraps_to_config_intenum(self, tmp_path: Path) -> None:
        """Test that Config(IntEnum.value) auto-wraps to Config(ConfigIntEnum(IntEnum.value))."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("")

        class IntEnumConfig(ConfigBase):
            pass

        IntEnumConfig.set_parser(IniParser())
        IntEnumConfig.set_file(config_file)
        IntEnumConfig._has_read_config = False

        class AppConfig:
            priority = IntEnumConfig(Priority.MEDIUM)

        descriptor = AppConfig.__dict__["priority"]
        assert isinstance(descriptor._data_type, ConfigIntEnum)
        assert descriptor._data_type.value == Priority.MEDIUM


class TestIntFlagAutoWrapping:
    """Test that IntFlag instances are automatically wrapped."""

    def test_intflag_auto_wraps_to_config_intflag(self, tmp_path: Path) -> None:
        """Test that Config(IntFlag.value) auto-wraps to Config(ConfigIntFlag(IntFlag.value))."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("")

        class IntFlagConfig(ConfigBase):
            pass

        IntFlagConfig.set_parser(IniParser())
        IntFlagConfig.set_file(config_file)
        IntFlagConfig._has_read_config = False

        class AppConfig:
            perms = IntFlagConfig(Permission.READ)

        descriptor = AppConfig.__dict__["perms"]
        assert isinstance(descriptor._data_type, ConfigIntFlag)
        assert descriptor._data_type.value == Permission.READ


class TestStandardEnumAutoWrapping:
    """Test that standard Enum instances are automatically wrapped."""

    def test_standard_enum_auto_wraps_to_config_enum(self, tmp_path: Path) -> None:
        """Test that Config(Enum.value) auto-wraps to Config(ConfigEnum(Enum.value))."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("")

        class EnumConfig(ConfigBase):
            pass

        EnumConfig.set_parser(IniParser())
        EnumConfig.set_file(config_file)
        EnumConfig._has_read_config = False

        class AppConfig:
            option = EnumConfig(StandardEnum.OPTION_A)

        descriptor = AppConfig.__dict__["option"]
        assert isinstance(descriptor._data_type, ConfigEnum)
        assert descriptor._data_type.value == StandardEnum.OPTION_A
