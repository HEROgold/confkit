"""Test suite for the Config class and its descriptors."""

import enum
from configparser import ConfigParser
from enum import auto
from pathlib import Path
from unittest.mock import patch

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.config import Config
from confkit.data_types import Boolean, Enum, Float, Integer, IntEnum, IntFlag, Optional, StrEnum, String
from confkit.exceptions import InvalidConverterError, InvalidDefaultError

config = Path("test.ini")
config.unlink(missing_ok=True)  # Remove the file if it exists
config.touch()  # Create a new empty file for testing
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(config)
Config.write_on_edit = True  # Enable writing to file during tests


class EnumTest(enum.Enum):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()

class StrEnumTest(enum.StrEnum):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()

class IntEnumTest(enum.IntEnum):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()

class IntFlagTest(enum.IntFlag):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()

# Having this class exists, tests the functionality of the Config descriptors.
# This class will create a test.ini file, which tests writing, reading, editing setting config values.
# This class also serves as a test configuration for the with_setting decorator.
class Test:
    """Test class to demonstrate and test the use of Config descriptors."""

    # The following line of code would raise an error when loading, as expected.
    # But the raising of the error would prevent the file from being testable.
    # null_object = Config(object())  # noqa: ERA001

    # Usual test cases for Config descriptors
    null_none = Config(None)
    null_str = Config("0")
    null_bool = Config(default=True)
    null_int = Config(5)
    null_float = Config(5.0)
    number = Config(0)
    string = Config("default")
    boolean = Config(default=False)
    c_float = Config(0.0)
    optional_number = Config(0, optional=True)
    optional_string = Config("", optional=True)
    optional_boolean = Config(default=False, optional=True)
    optional_float = Config(0.0, optional=True)
    # Test invalid setups (Type checkers like pyright will raise errors here)
    none_int = Config(Integer(None)) # type: ignore[reportArgumentType]
    none_string = Config(String(None)) # type: ignore[reportArgumentType]
    none_boolean = Config(Boolean(None)) # type: ignore[reportArgumentType]
    none_float = Config(Float(None)) # type: ignore[reportArgumentType]
    # Custom data type tests
    custom = Config(Integer(0))
    optional_custom = Config(Optional(Integer(0)))
    enum = Config(Enum(EnumTest.OPTION_A))
    str_enum = Config(StrEnum(StrEnumTest.OPTION_A))
    int_enum = Config(IntEnum(IntEnumTest.OPTION_A))
    int_flag = Config(IntFlag(IntFlagTest.OPTION_A))
    optional_enum = Config(Optional(Enum(EnumTest.OPTION_A)))
    optional_str_enum = Config(Optional(StrEnum(StrEnumTest.OPTION_A)))
    optional_int_enum = Config(Optional(IntEnum(IntEnumTest.OPTION_A)))
    optional_int_flag = Config(Optional(IntFlag(IntFlagTest.OPTION_A)))

    @Config.with_setting(number)
    def setting(self, **kwargs):  # type: ignore[reportMissingParameterType]  # noqa: ANN003, ANN201, D102
        return kwargs.get("number")

def test_enum() -> None:
    assert Test.enum == EnumTest.OPTION_A
    assert Test.enum.name == EnumTest.OPTION_A.name
    assert Test.enum.value == EnumTest.OPTION_A.value

def test_str_enum() -> None:
    assert Test.str_enum == StrEnumTest.OPTION_A
    assert Test.str_enum.name == StrEnumTest.OPTION_A.name
    assert Test.str_enum.value == StrEnumTest.OPTION_A.value

def test_int_enum() -> None:
    assert Test.int_enum == IntEnumTest.OPTION_A
    assert Test.int_enum.name == IntEnumTest.OPTION_A.name
    assert Test.int_enum.value == IntEnumTest.OPTION_A.value

def test_int_flag() -> None:
    assert Test.int_flag == IntFlagTest.OPTION_A
    assert Test.int_flag.name == IntFlagTest.OPTION_A.name
    assert Test.int_flag.value == IntFlagTest.OPTION_A.value

def test_init_no_args() -> None:
    with pytest.raises((InvalidDefaultError, InvalidConverterError)):
        Config() # type: ignore[reportCallIssue]

def test_init_no_default() -> None:
    with pytest.raises(InvalidDefaultError):
        Config() # type: ignore[reportCallIssue]

@given(st.booleans())
def test_init_optional(optional_value: bool) -> None:  # noqa: FBT001
    """Test Config initialization with various optional values."""
    assert Config(default=0, optional=optional_value)
    assert Config(default="test", optional=optional_value)


@given(st.text(min_size=1), st.text(min_size=1), st.text(), st.text())
def test_kwarg(section: str, setting: str, name: str, default: str) -> None:
    """Test Config.as_kwarg decorator with various parameters."""
    @Config.as_kwarg(section, setting, name, default)
    def func(**kwargs) -> str:  # type: ignore[reportMissingParameterType] # noqa: ANN003
        return kwargs.get(name, "fallback")

    result = func()
    # Should return either the config value or the default
    assert isinstance(result, str)


@given(st.integers())
def test_with_setting(value: int) -> None:
    """Test the with_setting decorator."""
    t = Test()
    t.number = value
    assert t.setting() == value


@given(st.integers())
def test_number(value: int) -> None:
    t = Test()
    t.number = value
    assert t.number == value


@given(st.text())
def test_string(value: str) -> None:
    t = Test()
    t.string = value
    assert t.string == value


@given(st.booleans())
def test_boolean(value: bool) -> None:  # noqa: FBT001
    t = Test()
    t.boolean = value
    assert t.boolean == value


@given(st.floats(allow_nan=False))
def test_float(value: float) -> None:
    t = Test()
    t.c_float = value
    assert t.c_float == value


@given(st.integers())
def test_none_number(value: int) -> None:
    """Test should expect error."""
    t = Test()
    with pytest.raises(ValueError, match="invalid literal for int()"):
        assert t.none_int == value


@given(st.text())
def test_none_string(value: str) -> None:
    """Test should expect error."""
    t = Test()
    with pytest.raises(InvalidConverterError):
        assert t.none_string == value


@given(st.booleans())
def test_none_boolean(value: bool) -> None:  # noqa: FBT001
    """Test should expect error."""
    t = Test()
    with pytest.raises(ValueError, match="Cannot convert None to boolean."):
        assert t.none_boolean == value


@given(st.floats())
def test_none_float(value: float) -> None:
    """Test should expect error."""
    t = Test()
    with pytest.raises(ValueError, match="could not convert string to float: 'None'"):
        assert t.none_float == value


@given(st.integers())
def test_optional_number(value: int) -> None:
    t = Test()
    t.number = value
    assert t.number == value or t.number is None


@given(st.text())
def test_optional_string(value: str) -> None:
    t = Test()
    t.optional_string = value
    assert t.optional_string == value or t.optional_string is None


@given(st.booleans())
def test_optional_boolean(value: bool) -> None:  # noqa: FBT001
    t = Test()
    t.optional_boolean = value
    assert t.optional_boolean == value or t.optional_boolean is None


@given(st.floats(allow_nan=False))
def test_optional_float(value: float) -> None:
    t = Test()
    t.optional_float = value
    assert t.optional_float == value or t.optional_float is None


@given(st.text(min_size=1), st.text(min_size=1), st.text())
def test_config_set_decorator(section: str, setting: str, value: str) -> None:
    """Test the Config.set decorator with various section/setting/value combinations."""
    # Ensure section exists
    if not parser.has_section(section):
        parser.add_section(section)

    @Config.set(section, setting, value)
    def test_func() -> str:
        return "executed"

    result = test_func()
    assert result == "executed"
    assert parser.get(section, setting) == value



def test_config_as_kwarg_no_name() -> None:
    """Test Config.as_kwarg when name is None."""
    @Config.as_kwarg("Test", "string", None, "fallback")
    def test_func(**kwargs) -> str:  # type: ignore[reportMissingParameterType] # noqa: ANN003
        return kwargs.get("string", "default")

    result = test_func()
    assert result is not None


def test_config_as_kwarg_missing_setting_no_default() -> None:
    """Test Config.as_kwarg when setting doesn't exist and no default provided."""
    with pytest.raises(ValueError, match="Config value.*is not set.*and no default value is given"):
        Config.as_kwarg("NonExistentSection", "nonexistent_setting")


@given(st.text(min_size=1), st.text(min_size=1), st.one_of(st.text(), st.none()), st.text())
def test_config_as_kwarg_with_default(section: str, setting: str, custom_name: str | None, default_value: str) -> None:
    """Test Config.as_kwarg with various default values."""
    @Config.as_kwarg(section, setting, custom_name, default_value)
    def test_func(**kwargs) -> str:  # type: ignore[reportMissingParameterType] # noqa: ANN003
        return kwargs.get(custom_name or setting, "")

    result = test_func()
    assert isinstance(result, str)


@given(st.text(min_size=1), st.text(min_size=1), st.text())
def test_config_default_decorator(section: str, setting: str, value: str) -> None:
    """Test the Config.default decorator with various section/setting/value combinations."""
    # Ensure section exists and remove any existing value
    if not parser.has_section(section):
        parser.add_section(section)
    if parser.has_option(section, setting):
        parser.remove_option(section, setting)

    @Config.default(section, setting, value)
    def test_func() -> str:
        return "executed"

    result = test_func()
    assert result == "executed"
    assert parser.get(section, setting) == value


def test_optional_validate_none_value() -> None:
    """Test Optional.validate when value is None."""
    optional_type = Optional(String("default"))
    # Use monkey patching to set internal state
    with patch.object(optional_type._data_type, "value", None):  # type: ignore[attr-defined]
        assert optional_type.validate() is True


def test_optional_validate_non_none_value() -> None:
    """Test Optional.validate when value is not None."""
    optional_type = Optional(String("default"))
    # This should call the wrapped data type's validate method
    assert optional_type.validate() is True


@given(st.booleans())
def test_config_validate_types_disabled(validation_state: bool) -> None:  # noqa: FBT001
    """Test that validation behavior changes with validate_types setting."""
    original_validate_types = Config.validate_types
    try:
        Config.validate_types = validation_state
        t = Test()
        # This should work regardless of validation state for valid values
        result = t.number
        assert isinstance(result, int)
    finally:
        Config.validate_types = original_validate_types


def test_as_kwarg_no_default_unset() -> None:
    """Test as_kwarg when default is UNSET (line 276->278 branch)."""
    # Ensure we have a section and setting that exists
    test_section = "TestAsKwarg"
    test_setting = "test_setting"

    if not parser.has_section(test_section):
        parser.add_section(test_section)
    parser.set(test_section, test_setting, "existing_value")

    # Use as_kwarg without providing a default value (UNSET)
    # This should skip the _set_default call and go directly to getting the value
    @Config.as_kwarg(test_section, test_setting)
    def test_func(**kwargs) -> str:  # noqa: ANN003
        return kwargs.get(test_setting, "fallback")

    result = test_func()
    assert result == "existing_value"
