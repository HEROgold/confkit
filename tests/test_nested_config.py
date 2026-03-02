"""Tests for nested configuration support."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import pytest

from confkit.config import Config
from confkit.ext.parsers import IniParser, MsgspecParser

if TYPE_CHECKING:
    from pathlib import Path

T = TypeVar("T")


@pytest.fixture
def ini_config_file(tmp_path: Path) -> Path:
    """Create a temporary INI config file."""
    return tmp_path / "nested_test.ini"


@pytest.fixture
def yaml_config_file(tmp_path: Path) -> Path:
    """Create a temporary YAML config file."""
    return tmp_path / "nested_test.yaml"


@pytest.fixture
def json_config_file(tmp_path: Path) -> Path:
    """Create a temporary JSON config file."""
    return tmp_path / "nested_test.json"


@pytest.fixture
def toml_config_file(tmp_path: Path) -> Path:
    """Create a temporary TOML config file."""
    return tmp_path / "nested_test.toml"


def test_nested_ini_config(ini_config_file: Path) -> None:
    """Test nested configuration with INI files using dot notation."""

    class IniConfig(Config[T]): ...

    IniConfig._set_parser(IniParser())
    IniConfig.set_file(ini_config_file)

    class Database:
        host = IniConfig("localhost")
        port = IniConfig(5432)

        class Credentials:
            username = IniConfig("admin")
            password = IniConfig("secret")

    # Test reading nested values
    assert Database.host == "localhost"
    assert Database.port == 5432
    assert Database.Credentials.username == "admin"
    assert Database.Credentials.password == "secret"

    # Read the file and verify INI structure uses dot notation
    parser = IniParser()
    parser.read(ini_config_file)

    # INI files use dot notation for nested sections
    assert parser.has_section("Database")
    assert parser.get("Database", "host") == "localhost"
    assert parser.get("Database", "port") == "5432"
    assert parser.has_section("Database.Credentials")
    assert parser.get("Database.Credentials", "username") == "admin"
    assert parser.get("Database.Credentials", "password") == "secret"


def test_nested_yaml_config(yaml_config_file: Path) -> None:
    """Test nested configuration with YAML files."""

    class YamlConfig(Config[T]): ...

    YamlConfig.set_file(yaml_config_file)

    class Database:
        host = YamlConfig("localhost")
        port = YamlConfig(5432)

        class Credentials:
            username = YamlConfig("admin")
            password = YamlConfig("secret")

    # Test writing nested values
    assert Database.host == "localhost"
    assert Database.port == 5432
    assert Database.Credentials.username == "admin"
    assert Database.Credentials.password == "secret"

    # Read the file and verify structure
    with yaml_config_file.open("r") as f:
        import msgspec.yaml
        data = msgspec.yaml.decode(f.read())

    assert data["Database"]["host"] == "localhost"
    assert data["Database"]["port"] == 5432
    assert data["Database"]["Credentials"]["username"] == "admin"
    assert data["Database"]["Credentials"]["password"] == "secret"


def test_nested_json_config(json_config_file: Path) -> None:
    """Test nested configuration with JSON files."""

    class JsonConfig(Config[T]): ...

    JsonConfig.set_file(json_config_file)

    class Server:
        name = JsonConfig("web-server")

        class Network:
            ip = JsonConfig("127.0.0.1")

            class Ports:
                http = JsonConfig(80)
                https = JsonConfig(443)

    # Test three-level nesting
    assert Server.name == "web-server"
    assert Server.Network.ip == "127.0.0.1"
    assert Server.Network.Ports.http == 80
    assert Server.Network.Ports.https == 443

    # Read and verify JSON structure
    with json_config_file.open("r") as f:
        import msgspec.json
        data = msgspec.json.decode(f.read())

    assert data["Server"]["name"] == "web-server"
    assert data["Server"]["Network"]["ip"] == "127.0.0.1"
    assert data["Server"]["Network"]["Ports"]["http"] == 80
    assert data["Server"]["Network"]["Ports"]["https"] == 443


def test_nested_toml_config(toml_config_file: Path) -> None:
    """Test nested configuration with TOML files."""

    class TomlConfig(Config[T]): ...

    TomlConfig.set_file(toml_config_file)

    class App:
        version = TomlConfig("1.0.0")

        class Settings:
            debug = TomlConfig(True)
            timeout = TomlConfig(30)

    assert App.version == "1.0.0"
    assert App.Settings.debug is True
    assert App.Settings.timeout == 30

    # Read and verify TOML structure
    with toml_config_file.open("r") as f:
        import msgspec.toml
        data = msgspec.toml.decode(f.read())

    assert data["App"]["version"] == "1.0.0"
    assert data["App"]["Settings"]["debug"] is True
    assert data["App"]["Settings"]["timeout"] == 30


def test_msgspec_parser_nested_navigation() -> None:
    """Test the MsgspecParser's ability to navigate nested structures."""
    parser = MsgspecParser()
    parser.data = {}

    # Test creating nested sections
    parser.set("Parent.Child.GrandChild", "setting", "value")

    assert parser.has_section("Parent")
    assert parser.has_section("Parent.Child")
    assert parser.has_section("Parent.Child.GrandChild")
    assert parser.has_option("Parent.Child.GrandChild", "setting")
    assert parser.get("Parent.Child.GrandChild", "setting") == "value"

    # Test setting values at different levels
    parser.set("Parent", "root_setting", "root_value")
    parser.set("Parent.Child", "child_setting", "child_value")

    assert parser.get("Parent", "root_setting") == "root_value"
    assert parser.get("Parent.Child", "child_setting") == "child_value"

    # Verify data structure
    assert parser.data == {
        "Parent": {
            "root_setting": "root_value",
            "Child": {
                "child_setting": "child_value",
                "GrandChild": {
                    "setting": "value",
                },
            },
        },
    }


def test_msgspec_parser_nested_remove_option() -> None:
    """Test removing options from nested sections."""
    parser = MsgspecParser()
    parser.data = {}

    parser.set("Level1.Level2.Level3", "key", "value")
    assert parser.has_option("Level1.Level2.Level3", "key")

    parser.remove_option("Level1.Level2.Level3", "key")
    assert not parser.has_option("Level1.Level2.Level3", "key")


def test_msgspec_parser_nested_section_not_found() -> None:
    """Test behavior when nested section doesn't exist."""
    parser = MsgspecParser()
    parser.data = {}

    assert not parser.has_section("NonExistent.Section")
    assert not parser.has_option("NonExistent.Section", "key")
    assert parser.get("NonExistent.Section", "key", fallback="default") == "default"


def test_mixed_nested_and_flat_sections(json_config_file: Path) -> None:
    """Test mixing nested and flat sections."""

    class JsonConfig(Config[T]): ...

    JsonConfig.set_file(json_config_file)

    class FlatSection:
        setting1 = JsonConfig("value1")

    class NestedSection:
        setting2 = JsonConfig("value2")

        class Inner:
            setting3 = JsonConfig("value3")

    assert FlatSection.setting1 == "value1"
    assert NestedSection.setting2 == "value2"
    assert NestedSection.Inner.setting3 == "value3"

    # Verify structure
    with json_config_file.open("r") as f:
        import msgspec.json
        data = msgspec.json.decode(f.read())

    assert data["FlatSection"]["setting1"] == "value1"
    assert data["NestedSection"]["setting2"] == "value2"
    assert data["NestedSection"]["Inner"]["setting3"] == "value3"
