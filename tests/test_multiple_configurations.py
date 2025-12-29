"""Tests for multiple configurations."""

from configparser import ConfigParser
from pathlib import Path

import hypothesis
from hypothesis import strategies as st

from confkit.config import Config


class Config1(Config): ...
class Config2(Config): ...

config_1 = Path("config1_test.ini")
Config1.set_file(config_1)
Config1.set_parser(ConfigParser())

config_2 = Path("config2_test.ini")
Config2.set_file(config_2)
Config2.set_parser(ConfigParser())


class Config3(Config1): ...
class Config4(Config2): ...

class TestEnv:
    a = Config1(1)
    b = Config2(2)
    c = Config3(3)
    d = Config4(4)

@hypothesis.given(st.integers(), st.integers(), st.integers(), st.integers())
def test_parsers_inherit_between_subclasses(a: int, b: int, c: int, d: int) -> None:
    """Config subclasses should share the parser when they inherit from the same base."""
    # Set values in different configurations (self-contained setup)
    TestEnv.a = a
    TestEnv.b = b
    TestEnv.c = c
    TestEnv.d = d

    # Check parser inheritance
    assert Config1._parser == Config3._parser
    assert Config2._parser == Config4._parser


@hypothesis.given(st.integers(), st.integers(), st.integers(), st.integers())
def test_files_inherit_between_subclasses(a: int, b: int, c: int, d: int) -> None:
    """Config subclasses should share the file when they inherit from the same base."""
    # Self-contained setup
    TestEnv.a = a
    TestEnv.b = b
    TestEnv.c = c
    TestEnv.d = d

    # Check file inheritance
    assert Config1._file == Config3._file
    assert Config2._file == Config4._file


@hypothesis.given(st.integers(), st.integers(), st.integers(), st.integers())
def test_setting_values_are_independent(a: int, b: int, c: int, d: int) -> None:
    """Setting values in different Config types shouldn't interfere with each other."""
    TestEnv.a = a
    TestEnv.b = b
    TestEnv.c = c
    TestEnv.d = d

    # Basic independence checks
    assert TestEnv.a == a
    assert TestEnv.c == c


@hypothesis.given(st.integers(), st.integers())
def test_updating_a_does_not_change_c(a: int, c: int) -> None:
    """Mutating a value for Config1 shouldn't change the Config3 value (same-named but different section/file)."""
    TestEnv.a = a
    TestEnv.c = c

    TestEnv.a = a * 2

    assert TestEnv.a == a * 2
    assert TestEnv.c == c


@hypothesis.given(st.integers(), st.integers())
def test_updating_c_does_not_change_a(a: int, c: int) -> None:
    """Mutating a value for Config3 shouldn't change the Config1 value."""
    TestEnv.a = a
    TestEnv.c = c

    TestEnv.c = c * 3

    assert TestEnv.a == a
    assert TestEnv.c == c * 3
