"""Tests for EnvParser."""

from __future__ import annotations

import os

import pytest

from confkit.ext.parsers import EnvParser


@pytest.fixture
def env_parser():
    """Create an EnvParser instance."""
    return EnvParser()


@pytest.fixture
def temp_env_file(tmp_path):
    """Create a temporary .env file."""
    return tmp_path / ".env"


def test_env_parser_init(env_parser) -> None:
    """Test EnvParser initialization."""
    assert isinstance(env_parser.data, dict)


def test_env_parser_read_nonexistent_file(env_parser, temp_env_file) -> None:
    """Test reading from a nonexistent file loads environment variables."""
    # Set a test env var
    test_key = "TEST_CONFKIT_VAR"
    test_value = "test_value"
    os.environ[test_key] = test_value

    try:
        env_parser.read(temp_env_file)
        assert test_key in env_parser.data
        assert env_parser.data[test_key] == test_value
    finally:
        del os.environ[test_key]


def test_env_parser_read_env_file(env_parser, temp_env_file) -> None:
    """Test reading from a .env file."""
    # Create a .env file
    temp_env_file.write_text("KEY1=value1\nKEY2=value2\nKEY3=value with spaces\n")

    env_parser.read(temp_env_file)

    assert "KEY1" in env_parser.data
    assert env_parser.data["KEY1"] == "value1"
    assert env_parser.data["KEY2"] == "value2"
    assert env_parser.data["KEY3"] == "value with spaces"


def test_env_parser_read_env_file_with_comments(env_parser, temp_env_file) -> None:
    """Test reading .env file with comments and empty lines."""
    content = """
# This is a comment
KEY1=value1

# Another comment
KEY2=value2
    """
    temp_env_file.write_text(content)

    env_parser.read(temp_env_file)

    assert "KEY1" in env_parser.data
    assert "KEY2" in env_parser.data
    assert env_parser.data["KEY1"] == "value1"
    assert env_parser.data["KEY2"] == "value2"


def test_env_parser_read_env_file_with_quotes(env_parser, temp_env_file) -> None:
    """Test reading .env file with quoted values."""
    content = 'KEY1="quoted value"\nKEY2=\'single quoted\'\nKEY3=unquoted\n'
    temp_env_file.write_text(content)

    env_parser.read(temp_env_file)

    assert env_parser.data["KEY1"] == "quoted value"
    assert env_parser.data["KEY2"] == "single quoted"
    assert env_parser.data["KEY3"] == "unquoted"


def test_env_parser_env_vars_take_precedence(env_parser, temp_env_file) -> None:
    """Test that environment variables take precedence over .env file."""
    # Create a .env file
    temp_env_file.write_text("CONFKIT_TEST=from_file\n")

    # Set environment variable with same key
    os.environ["CONFKIT_TEST"] = "from_env"

    try:
        env_parser.read(temp_env_file)
        assert env_parser.data["CONFKIT_TEST"] == "from_env"
    finally:
        del os.environ["CONFKIT_TEST"]


def test_env_parser_write(env_parser, temp_env_file) -> None:
    """Test that writing raises NotImplementedError for readonly parser."""
    env_parser.data = {
        "KEY1": "value1",
        "KEY2": "value2",
        "KEY3": "value with spaces",
    }

    with temp_env_file.open("w") as f:
        with pytest.raises(NotImplementedError):
            env_parser.write(f)


def test_env_parser_has_section(env_parser) -> None:
    """Test has_section always returns True."""
    assert env_parser.has_section("any_section")
    assert env_parser.has_section("")


def test_env_parser_has_option(env_parser) -> None:
    """Test has_option checks for key existence."""
    env_parser.data = {"KEY1": "value1"}

    assert env_parser.has_option("any_section", "KEY1")
    assert not env_parser.has_option("any_section", "KEY2")


def test_env_parser_get(env_parser) -> None:
    """Test getting values."""
    env_parser.data = {"KEY1": "value1"}

    assert env_parser.get("any_section", "KEY1") == "value1"
    assert env_parser.get("any_section", "KEY2") == ""
    assert env_parser.get("any_section", "KEY2", fallback="default") == "default"


def test_env_parser_set(env_parser) -> None:
    """Test that setting values raises NotImplementedError for readonly parser."""
    with pytest.raises(NotImplementedError):
        env_parser.set("any_section", "KEY1", "value1")


def test_env_parser_remove_option(env_parser) -> None:
    """Test removing options."""
    env_parser.data = {"KEY1": "value1", "KEY2": "value2"}

    env_parser.remove_option("any_section", "KEY1")

    assert "KEY1" not in env_parser.data
    assert "KEY2" in env_parser.data


def test_env_parser_add_section(env_parser) -> None:
    """Test add_section is a no-op."""
    env_parser.add_section("section")  # Should not raise


def test_env_parser_set_section(env_parser) -> None:
    """Test set_section is a no-op."""
    env_parser.set_section("section")  # Should not raise


def test_env_parser_integration(env_parser, temp_env_file) -> None:
    """Test full read cycle for readonly parser."""
    # Create a .env file
    content = """DATABASE_URL=postgresql://localhost/db
API_KEY=secret123
DEBUG=true"""
    temp_env_file.write_text(content)

    # Read from file
    env_parser.read(temp_env_file)

    assert env_parser.data["DATABASE_URL"] == "postgresql://localhost/db"
    assert env_parser.data["API_KEY"] == "secret123"
    assert env_parser.data["DEBUG"] == "true"
