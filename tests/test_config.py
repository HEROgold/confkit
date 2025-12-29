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
from confkit.data_types import (
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
    OPTION_B = auto()
    OPTION_C = OPTION_A | OPTION_B
    OPTION_D = OPTION_A & OPTION_B
    OPTION_E = OPTION_A ^ OPTION_B

class StrEnumTest(enum.StrEnum):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = auto()
    OPTION_D = auto()
    OPTION_E = auto()
    OPTION_F = auto()
    OPTION_G = auto()

class IntEnumTest(enum.IntEnum):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = OPTION_A | OPTION_B
    OPTION_D = OPTION_A & OPTION_B
    OPTION_E = OPTION_A ^ OPTION_B

class IntFlagTest(enum.IntFlag):
    """A test enum for ConfigEnumType."""

    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = OPTION_A | OPTION_B
    OPTION_D = OPTION_A & OPTION_B
    OPTION_E = OPTION_A ^ OPTION_B

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
    hex_value = Config(Hex(0xFF))
    octal_value = Config(Octal(0o77))
    binary_value = Config(Binary(0b101010))
    binary_value_2 = Config(Binary(b"101010"))
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
    custom_int_base_9 = Config(Integer(99, base=9))
    custom_int_base_7 = Config(Integer(99, base=7))
    custom_int_base_5 = Config(Integer(99, base=5))
    custom_int_base_3 = Config(Integer(99, base=3))
    # Test optional
    optional_number = Config(0, optional=True)
    optional_string = Config("", optional=True)
    optional_boolean = Config(default=False, optional=True)
    optional_float = Config(0.0, optional=True)
    optional_number2 = Config(0, optional=True)
    optional_string2 = Config("", optional=True)
    optional_boolean2 = Config(default=False, optional=True)
    optional_float2 = Config(0.0, optional=True)
    optional_number3 = Config(Optional(Integer()))
    optional_string3 = Config(Optional(String()))
    optional_boolean3 = Config(Optional(Boolean()))
    optional_float3 = Config(Optional(Float()))
    optional_number4 = Config(Integer(), optional=True)
    optional_string4 = Config(String(), optional=True)
    optional_boolean4 = Config(Boolean(), optional=True)
    optional_float4 = Config(Float(), optional=True)
    optional_enum = Config(Optional(Enum(EnumTest.OPTION_A)))
    optional_str_enum = Config(Optional(StrEnum(StrEnumTest.OPTION_A)))
    optional_int_enum = Config(Optional(IntEnum(IntEnumTest.OPTION_A)))
    optional_int_flag = Config(Optional(IntFlag(IntFlagTest.OPTION_A)))
    optional_enum2 = Config(Enum(EnumTest.OPTION_A), optional=True)
    optional_str_enum2 = Config(StrEnum(StrEnumTest.OPTION_A), optional=True)
    optional_int_enum2 = Config(IntEnum(IntEnumTest.OPTION_A), optional=True)
    optional_int_flag2 = Config(IntFlag(IntFlagTest.OPTION_A), optional=True)
    # Test list types
    list_of_strings = Config(List(["a", "b", "c"]))
    list_of_integers = Config(List([1, 2, 3, 4]))
    list_of_floats = Config(List([1.0, 2.0, 3.0, 4.0]))
    list_of_booleans = Config(List([True, False, True]))
    list_of_paths = Config(List(["/path/to/file1", "/path/to/file2"]))

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


def test_optional_string_null_values() -> None:
    """Test that all null values from NoneType.null_values convert to None."""
    t = Test()

    # Ensure all null values from NoneType.null_values are always tested
    for null_value in NoneType.null_values:
        t.optional_string = null_value
        t.optional_string2 = null_value
        t.optional_string3 = null_value

        assert t.optional_string is None
        assert t.optional_string2 is None
        assert t.optional_string3 is None


## Hypothesis tests:


@given(st.booleans())
def test_init_optional(optional_value: bool) -> None:  # noqa: FBT001
    """Test Config initialization with various optional values."""
    assert Config(default=0, optional=optional_value)
    assert Config(default="test", optional=optional_value)


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
    with pytest.raises(ValueError, match=r"invalid literal for int()"):
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
    with pytest.raises(ValueError, match=r"Cannot convert None to boolean."):
        assert t.none_boolean == value


@given(st.floats())
def test_none_float(value: float) -> None:
    """Test should expect error."""
    t = Test()
    with pytest.raises(ValueError, match=r"could not convert string to float: 'None'"):
        assert t.none_float == value


@given(st.one_of(st.none(), st.integers()))
def test_optional_number(value: int | None) -> None:
    t = Test()
    t.optional_number = value
    t.optional_number2 = value
    t.optional_number3 = value
    t.optional_number4 = value
    assert t.optional_number == value or t.optional_number is None
    assert t.optional_number2 == value or t.optional_number2 is None
    assert t.optional_number3 == value or t.optional_number3 is None
    assert t.optional_number4 == value or t.optional_number4 is None


@given(st.one_of(st.none(), st.text()))
def test_optional_string(value: str | None) -> None:
    t = Test()
    t.optional_string = value
    t.optional_string2 = value
    t.optional_string3 = value
    t.optional_string4 = value

    # Convert value to expected None types. after setting it in file.
    if value and value.casefold() in NoneType.null_values:
        value = None

    assert t.optional_string == value
    assert t.optional_string2 == value
    assert t.optional_string3 == value
    assert t.optional_string4 == value


def test_class_access_runs_custom_validation() -> None:
    class UpperCaseString(BaseDataType[str]):
        def convert(self, value: str) -> str:
            return value

        def validate(self) -> bool:
            super().validate()
            if self.value != self.value.upper():
                msg = "Value must be upper case"
                raise InvalidConverterError(msg)
            return True

    class UpperCaseConfig:
        shout = Config(UpperCaseString("DEFAULT"))

    Config._parser.set("UpperCaseConfig", "shout", "lowercase")
    with pytest.raises(InvalidConverterError, match="Value must be upper case"):
        _ = UpperCaseConfig.shout


@given(st.one_of(st.none(), st.booleans()))
def test_optional_boolean(value: bool | None) -> None:  # noqa: FBT001
    t = Test()
    t.optional_boolean = value
    t.optional_boolean2 = value
    t.optional_boolean3 = value
    t.optional_boolean4 = value
    assert t.optional_boolean == value or t.optional_boolean is None
    assert t.optional_boolean2 == value or t.optional_boolean2 is None
    assert t.optional_boolean3 == value or t.optional_boolean3 is None
    assert t.optional_boolean4 == value or t.optional_boolean4 is None


@given(st.one_of(st.none(), st.floats(allow_nan=False)))
def test_optional_float(value: float | None) -> None:
    t = Test()
    t.optional_float = value
    t.optional_float2 = value
    t.optional_float3 = value
    t.optional_float4 = value
    assert t.optional_float == value or t.optional_float is None
    assert t.optional_float2 == value or t.optional_float2 is None
    assert t.optional_float3 == value or t.optional_float3 is None
    assert t.optional_float4 == value or t.optional_float4 is None


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


@given(st.integers())
def test_hex(value: int) -> None:
    """Test setting and getting hex values."""
    t = Test()
    t.hex_value = value
    assert t.hex_value == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "hex_value")
    expected_format = f"0x{value:x}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers())
def test_octal(value: int) -> None:
    """Test setting and getting octal values."""
    t = Test()
    t.octal_value = value
    assert t.octal_value == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "octal_value")
    expected_format = f"0o{value:o}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers())
def test_binary_int(value: int) -> None:
    """Test setting and getting binary values."""
    t = Test()
    t.binary_value = value
    assert t.binary_value == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "binary_value")
    expected_format = f"0b{value:b}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.binary())
def test_binary_bytes(value: bytes) -> None:
    """Test setting and getting binary values."""
    t = Test()
    t.binary_value = value
    int_value = int.from_bytes(value)
    assert t.binary_value == int_value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "binary_value")
    expected_format = f"0b{int_value:b}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers(min_value=0, max_value=4))
def test_custom_int_base_5(value: int) -> None:
    """Test setting and getting integers with custom base."""
    t = Test()
    t.custom_int_base_5 = value
    assert t.custom_int_base_5 == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "custom_int_base_5")
    expected_format = f"5c{value}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers(min_value=0, max_value=2))
def test_custom_int_base_3(value: int) -> None:
    """Test setting and getting integers with custom base."""
    t = Test()
    t.custom_int_base_3 = value
    assert t.custom_int_base_3 == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "custom_int_base_3")
    expected_format = f"3c{value}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers(min_value=0, max_value=6))
def test_custom_int_base_7(value: int) -> None:
    """Test setting and getting integers with custom base."""
    t = Test()
    t.custom_int_base_7 = value
    assert t.custom_int_base_7 == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "custom_int_base_7")
    expected_format = f"7c{value}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers(min_value=0, max_value=6))
def test_custom_int_base_9(value: int) -> None:
    """Test setting and getting integers with custom base."""
    t = Test()
    t.custom_int_base_9 = value
    assert t.custom_int_base_9 == value

    Config._parser.read(Config._file)
    stored_value = Config._parser.get("Test", "custom_int_base_9")
    expected_format = f"9c{value}"
    pred = stored_value == expected_format
    assert pred, f"Expected config file to contain value {expected_format}, but found {stored_value}"


@given(st.integers(min_value=0, max_value=6))
def test_custom_int_non_matching_base(value: int) -> None:
    """Test setting and getting integers with custom base."""
    t = Test()
    t.custom_int_base_9 = value
    Config._parser.set("Test", "custom_int_base_9", "0c0")
    with pytest.raises(ValueError, match=r"Base in string does not match base in Integer while converting."):
        assert t.custom_int_base_9


@given(st.lists(st.text()))
def test_list_of_strings(value: list[str]) -> None:
    t = Test()
    value = [i for i in value if i]  # Remove empty strings to avoid [] != [""] assert
    t.list_of_strings = value
    assert t.list_of_strings == value


@given(st.lists(st.booleans()))
def test_list_of_booleans(value: list[bool]) -> None:
    t = Test()
    t.list_of_booleans = value
    assert t.list_of_booleans == value


@given(st.lists(st.integers()))
def test_list_of_integers(value: list[int]) -> None:
    t = Test()
    t.list_of_integers = value
    assert t.list_of_integers == value


@given(st.lists(st.floats(allow_nan=False)))
def test_list_of_floats(value: list[float]) -> None:
    t = Test()
    t.list_of_floats = value
    assert t.list_of_floats == value

@given(st.sampled_from(StrEnumTest))
def test_str_enum_types(value: StrEnumTest) -> None:
    t = Test()
    t.str_enum = value
    assert t.str_enum == value


@given(st.sampled_from(IntEnumTest))
def test_int_enum_types(value: IntEnumTest) -> None:
    t = Test()
    t.int_enum = value
    assert t.int_enum == value


@given(st.sampled_from(IntFlagTest))
def test_int_flag_enum_types(value: IntFlagTest) -> None:
    t = Test()
    t.int_flag = value
    assert t.int_flag == value


@given(st.one_of(st.none(), st.sampled_from(StrEnumTest)))
def test_optional_str_enum_types(value: StrEnumTest) -> None:
    t = Test()
    t.optional_str_enum = value
    assert t.optional_str_enum == value


@given(st.one_of(st.none(), st.sampled_from(IntEnumTest)))
def test_optional_int_enum_types(value: IntEnumTest) -> None:
    t = Test()
    t.optional_int_enum = value
    assert t.optional_int_enum == value


@given(st.one_of(st.none(), st.sampled_from(IntFlagTest)))
def test_optional_int_flag_enum_types(value: IntFlagTest) -> None:
    t = Test()
    t.optional_int_flag = value
    assert t.optional_int_flag == value
