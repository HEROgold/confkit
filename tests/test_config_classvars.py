"""Test suite for testing Config class variables and edge cases.

This also contains the test cases where specific settings are expected.
"""

import tempfile
from collections.abc import Callable
from configparser import ConfigParser
from pathlib import Path
from typing import Never, ParamSpec, TypeVar

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.config import Config
from confkit.data_types import BaseDataType, Optional, String
from confkit.exceptions import InvalidConverterError, InvalidDefaultError
from confkit.sentinels import UNSET

F = TypeVar("F")
P = ParamSpec("P")


def config_restore(func: Callable[P, F]) -> Callable[P, F]:
    """Save and restore the _file and _parser attributes for the Config."""
    def inner(*args: P.args, **kwargs: P.kwargs) -> F:
        restores = (getattr(Config, "_file", UNSET), getattr(Config, "_parser", UNSET))
        result = func(*args, **kwargs)
        Config._file = restores[0]
        Config._parser = restores[1]
        return result
    return inner

@config_restore
def test_config_validate_file_unset() -> None:
    """Test Config.validate_file when _file is UNSET - Line 175 in config.py."""
    Config._file = UNSET
    config_instance = Config.__new__(Config)
    config_instance.optional = False
    with pytest.raises(ValueError, match=r"Config file is not set"):
        config_instance.validate_file()


@config_restore
def test_config_validate_parser_unset() -> None:
    """Test Config.validate_parser when _parser is UNSET - Line 181 in config.py."""
    Config._parser = UNSET
    config_instance = Config.__new__(Config)
    config_instance.optional = False
    with pytest.raises(ValueError, match=r"Config parser is not set"):
        config_instance.validate_parser()


@config_restore
def test_config_converter_is_unset() -> None:
    """Test validate_strict_type when converter is UNSET - Line 154 in config.py."""
    class MockDataType(BaseDataType[str]):
        def convert(self, value: str) -> Never: # ty: ignore[invalid-return-type]
            ...

    # Create a temporary isolated environment
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write("[Test]\nstring = test_value\n")

    # Set up isolated environment
    test_parser = ConfigParser()
    test_parser.read(tmp_path)
    Config.set_parser(test_parser)
    Config.set_file(tmp_path)

    config_instance = Config.__new__(Config)
    config_instance.optional = False
    config_instance._section = "Test"
    config_instance._setting = "string"
    mock_data_type = MockDataType("default")
    mock_data_type.convert = UNSET
    config_instance._data_type = mock_data_type

    with pytest.raises(InvalidConverterError, match=r"Converter is not set"):
        config_instance.validate_strict_type()
    tmp_path.unlink(missing_ok=True)

@config_restore
def test_config_validation_fails() -> None:
    """Test validate_strict_type when data_type.validate() returns False - Line 162 in config.py."""
    class FailingDataType(BaseDataType[str]):
        def convert(self, value: str) -> str:
            return value
        def validate(self) -> bool:
            return False

    # Create a temporary isolated environment
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write("[Test]\nstring = test_value\n")

    # Set up isolated environment
    test_parser = ConfigParser()
    test_parser.read(tmp_path)
    Config.set_parser(test_parser)
    Config.set_file(tmp_path)

    config_instance = Config.__new__(Config)
    config_instance.optional = False
    config_instance._section = "Test"
    config_instance._setting = "string"
    config_instance._data_type = FailingDataType("default")

    with pytest.raises(InvalidConverterError, match=r"Invalid value for Test.string"):
        config_instance.validate_strict_type()

    tmp_path.unlink(missing_ok=True)


@config_restore
def test_config_optional_type_validation_success() -> None:
    """Test optional type validation when types match - Line 165-167 in config.py."""
    # Create a temporary isolated environment
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write("[Test]\nstring = test_value\n")

    # Set up isolated environment
    test_parser = ConfigParser()
    test_parser.read(tmp_path)
    Config.set_parser(test_parser)
    Config.set_file(tmp_path)

    config_instance = Config.__new__(Config)
    config_instance.optional = True
    setattr(config_instance, "_section", "Test")  # noqa: B010
    setattr(config_instance, "_setting", "string")  # noqa: B010
    setattr(config_instance, "_data_type", String("default"))  # noqa: B010

    # Should pass validation without raising an exception
    config_instance.validate_strict_type()
    tmp_path.unlink(missing_ok=True)

@config_restore
def test_config_type_mismatch_error() -> None:
    """Test type mismatch validation error - Line 169 in config.py."""
    class WrongTypeDataType(BaseDataType[str]):
        def __init__(self, default: str) -> None:
            super().__init__(default)
        def convert(self, value: str) -> int:  # type: ignore[override]
            return int(value)

    # Create a temporary isolated environment
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write("[Test]\nnull_int = 123\n")

    # Set up isolated environment
    test_parser = ConfigParser()
    test_parser.read(tmp_path)
    Config.set_parser(test_parser)
    Config.set_file(tmp_path)

    config_instance = Config.__new__(Config)
    config_instance.optional = False
    config_instance._section = "Test"
    config_instance._setting = "null_int"
    config_instance._data_type = WrongTypeDataType("default")

    with pytest.raises(InvalidConverterError, match=r"Converter does not return the same type"):
        config_instance.validate_strict_type()

    tmp_path.unlink(missing_ok=True)


def test_config_none_type_cast() -> None:
    """Test None type casting in _cast_data_type - Line 105 in config.py."""
    config_instance = Config.__new__(Config)
    config_instance.optional = False
    result = BaseDataType.cast(None)
    assert result.default is None


def test_data_type_validate_no_orig_bases() -> None:
    """Test BaseDataType.validate when no __orig_bases__ - Line 28-29 in data_types.py."""
    class NoOrigBasesDataType:
        def __init__(self, default: str) -> None:
            self.default = default
            self.value = default
        def validate(self) -> bool:
            return BaseDataType.validate(self) # pyright: ignore[reportArgumentType]

    data_type = NoOrigBasesDataType("test")
    with pytest.raises(InvalidConverterError, match=r"No type information available for validation"):
        data_type.validate()


@given(st.text(min_size=1), st.text())
def test_optional_data_type_value_property_hypothesis(default_value: str, new_value: str) -> None:
    """Test Optional.value property with various string values using Hypothesis."""
    string_type = String(default_value)
    optional_type = Optional(string_type)
    assert optional_type.value == default_value

    string_type.value = new_value
    assert optional_type.value == new_value


def test_optional_data_type_value_property() -> None:
    """Test Optional.value property - Line 141 in data_types.py."""
    string_type = String("default_value")
    optional_type = Optional(string_type)
    assert optional_type.value == "default_value"

    string_type.value = "new_value"
    assert optional_type.value == "new_value"

def test_invalid_default_error() -> None:
    with pytest.raises(
        InvalidDefaultError,
        match=r"Unsupported default value type: object. Use a BaseDataType subclass for custom types.",
    ):
        BaseDataType.cast(object())

@config_restore
def test_ensure_option_existing_option() -> None:
    """Test _ensure_option when option already exists (line 202->exit branch)."""
    test_parser = ConfigParser()
    test_parser.add_section("TestExistingOption")
    test_parser.set("TestExistingOption", "existing_setting", "existing_value")

    test_config = Path("test_existing_option.ini")
    test_config.unlink(missing_ok=True)
    test_config.touch()

    Config.set_parser(test_parser)
    Config.set_file(test_config)

    class TestExistingOption:
        existing_setting = Config("default_value")

    # Access the setting to trigger the descriptor setup
    _ = TestExistingOption()
    # Verify the option wasn't overwritten with the default value
    assert test_parser.get("TestExistingOption", "existing_setting") == "existing_value"
    test_config.unlink(missing_ok=True)

@config_restore
def test_set_write_on_edit_disabled() -> None:
    """Test _set method when write_on_edit is False (line 230->exit branch)."""
    original_write_on_edit = Config.write_on_edit
    test_parser = ConfigParser()
    test_config = Path("test_no_write.ini")
    test_config.unlink(missing_ok=True)
    test_config.touch()

    with test_config.open("w") as f:
        f.write("[TestSection]\ntest_setting = initial_value\n")

    try:
        Config.write_on_edit = False
        Config.set_file(test_config)
        Config.set_parser(test_parser)

        initial_content = test_config.read_text()
        Config._set("TestSection", "test_setting", "new_value")
        final_content = test_config.read_text()
        # Call _set which should not write to file when write_on_edit is False
        assert initial_content == final_content
        # But the parser should have the new value in memory
        assert Config._parser.get("TestSection", "test_setting") == "new_value"
    finally:
        Config.write_on_edit = original_write_on_edit
        test_config.unlink(missing_ok=True)
