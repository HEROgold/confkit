"""Test file for testing Config decorators.

These are usually not safe enough to test using a single file, at the same time.ArithmeticError
These get their own test file.
"""

from collections.abc import Callable
from configparser import ConfigParser
from pathlib import Path
from typing import ParamSpec, TypeVar

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.config import Config
from confkit.sentinels import UNSET

F = TypeVar("F")
P = ParamSpec("P")


def config_new(func: Callable[P, F]) -> Callable[P, F]:
    """Save and restore the _file and _parser attributes for the Config."""
    def inner(*args: P.args, **kwargs: P.kwargs) -> F:
        restores = (getattr(Config, "_file", UNSET), getattr(Config, "_parser", UNSET))
        new_file = Path(f"{func.__name__}.ini")  # ty: ignore[unresolved-attribute]
        new_file.touch(exist_ok=True)
        Config._file = new_file
        Config._parser = ConfigParser()
        result = func(*args, **kwargs)
        Config._file = restores[0]
        Config._parser = restores[1]
        new_file.unlink(missing_ok=True)
        return result
    return inner

@config_new
@given(st.text(min_size=1), st.text(min_size=1), st.text())
def test_config_set_decorator(section: str, setting: str, value: str) -> None:
    """Test the Config.set decorator with various section/setting/value combinations."""
    # Ensure section exists
    if not Config._parser.has_section(section):
        Config._parser.add_section(section)

    @Config.set(section, setting, value)
    def test_func() -> str:
        return "executed"

    result = test_func()
    assert result == "executed"
    assert Config._parser.get(section, setting) == value

@config_new
@given(st.text(min_size=1), st.text(min_size=1), st.one_of(st.text(), st.none()), st.text())
def test_config_with_kwarg_with_default(section: str, setting: str, custom_name: str | None, default_value: str) -> None:
    """Test Config.with_kwarg with various default values."""
    @Config.with_kwarg(section, setting, custom_name, default_value)
    def test_func(**kwargs) -> str:  # noqa: ANN003
        return kwargs.get(custom_name or setting, "")

    result = test_func()
    assert isinstance(result, str)


@config_new
@given(st.text(min_size=1), st.text(min_size=1), st.text())
def test_config_default_decorator(section: str, setting: str, value: str) -> None:
    """Test the Config.default decorator with various section/setting/value combinations."""
    # Ensure section exists and remove any existing value
    if not Config._parser.has_section(section):
        Config._parser.add_section(section)
    if Config._parser.has_option(section, setting):
        Config._parser.remove_option(section, setting)

    @Config.default(section, setting, value)
    def test_func() -> str:
        return "executed"

    result = test_func()
    assert result == "executed"
    assert Config._parser.get(section, setting) == value

@config_new
def test_with_kwarg_no_default_unset() -> None:
    """Test with_kwarg when default is UNSET (line 276->278 branch)."""
    # Ensure we have a section and setting that exists
    test_section = "TestAsKwarg"
    test_setting = "test_setting"

    if not Config._parser.has_section(test_section):
        Config._parser.add_section(test_section)
    Config._parser.set(test_section, test_setting, "existing_value")

    # Use with_kwarg without providing a default value (UNSET)
    # This should skip the _set_default call and go directly to getting the value
    @Config.with_kwarg(test_section, test_setting)
    def test_func(**kwargs) -> str:  # noqa: ANN003
        return kwargs.get(test_setting, "fallback")

    result = test_func()
    assert result == "existing_value"

@config_new
def test_config_with_kwarg_no_name() -> None:
    """Test Config.with_kwarg when name is None."""
    @Config.with_kwarg("Test", "string", None, "fallback")
    def test_func(**kwargs) -> str:  # noqa: ANN003
        return kwargs.get("string", "default")

    result = test_func()
    assert result is not None

@config_new
@given(st.text(min_size=1), st.text(min_size=1), st.text(), st.text())
def test_kwarg(section: str, setting: str, name: str, default: str) -> None:
    """Test Config.with_kwarg decorator with various parameters."""
    @Config.with_kwarg(section, setting, name, default)
    def func(**kwargs) -> str:  # noqa: ANN003
        return kwargs.get(name, "fallback")

    result = func()
    # Should return either the config value or the default
    assert isinstance(result, str)

@config_new
def test_with_kwarg_no_default_no_section() -> None:
    """Test Config.with_kwarg decorator without any section or default value."""
    with pytest.raises(ValueError, match=r"Config value section='' setting='' is not set. and no default value is given."):
        Config.with_kwarg("", "", "", UNSET)
