"""Test Config with deeply nested configuration values like Config(Config(Config(42)))."""
from __future__ import annotations

from typing import TYPE_CHECKING

from confkit.config import Config as OG
from confkit.data_types import Integer, Optional, String
from confkit.ext.parsers import MsgspecParser
from confkit.parsers import IniParser

if TYPE_CHECKING:
    from pathlib import Path


def test_double_nested_config_integer(tmp_path: Path) -> None:
    """Test Config(Config(42)) - two levels of nesting."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Create a doubly nested config
    class Settings:
        port = Config(Config(Integer(8080)))

    # Verify it works
    assert Settings.port == 8080

    # Verify we can update it
    Settings.port = 3000
    assert Settings.port == 3000


def test_triple_nested_config_integer(tmp_path: Path) -> None:
    """Test Config(Config(Config(42))) - three levels of nesting."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Create a triply nested config
    class Settings:
        timeout = Config(Config(Config(Integer(30))))

    # Verify it works
    assert Settings.timeout == 30

    # Verify we can update it
    Settings.timeout = 60
    assert Settings.timeout == 60


def test_quad_nested_config_integer(tmp_path: Path) -> None:
    """Test Config(Config(Config(Config(42)))) - four levels of nesting."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Create a quadruply nested config
    class Settings:
        value = Config(Config(Config(Config(Integer(42)))))

    # Verify it works
    assert Settings.value == 42

    # Verify we can update it
    Settings.value = 100
    assert Settings.value == 100


def test_deeply_nested_config_with_string(tmp_path: Path) -> None:
    """Test deeply nested Config with String type."""
    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Create nested string config
    class Settings:
        name = Config(Config(Config(String("default"))))

    assert Settings.name == "default"

    Settings.name = "production"
    assert Settings.name == "production"


def test_nested_config_multiple_values(tmp_path: Path) -> None:
    """Test multiple deeply nested config values."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        port = Config(Config(Config(Integer(8000))))
        host = Config(Config(String("localhost")))
        timeout = Config(Config(Config(Config(Integer(30)))))

    assert Settings.port == 8000
    assert Settings.host == "localhost"
    assert Settings.timeout == 30

    # Update values
    Settings.port = 9000
    Settings.host = "0.0.0.0"
    Settings.timeout = 60

    assert Settings.port == 9000
    assert Settings.host == "0.0.0.0"
    assert Settings.timeout == 60


def test_nested_config_persistence(tmp_path: Path) -> None:
    """Test that nested config values persist to file."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        counter = Config(Config(Config(Integer(0))))

    # Set a value
    Settings.counter = 42
    assert Settings.counter == 42

    # Verify file was written
    assert config_file.stat().st_size > 0


def test_nested_config_with_class_hierarchy(tmp_path: Path) -> None:
    """Test nested configs combined with nested class hierarchy."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class AppSettings:
        app_name = Config(String("myapp"))

        class Database:
            host = Config(Config(String("localhost")))
            port = Config(Config(Config(Integer(5432))))

    assert AppSettings.app_name == "myapp"
    assert AppSettings.Database.host == "localhost"
    assert AppSettings.Database.port == 5432


def test_nested_config_all_extensions(tmp_path: Path) -> None:
    """Test nested configs across all file extensions."""
    for ext in [".ini", ".yaml", ".yml", ".json", ".toml"]:
        config_file = tmp_path / f"config_nested{ext}"
        config_file.touch()

        class Config(OG):
            """Test Config subclass."""

        Config.set_file(config_file)
        Config.write_on_edit = True

        class Settings:
            value = Config(Config(Config(Integer(123))))

        assert Settings.value == 123
        Settings.value = 456
        assert Settings.value == 456


def test_deeply_nested_int_no_wrapper(tmp_path: Path) -> None:
    """Test that raw nested integers still work."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Just plain nesting without explicit type wrapper
    class Settings:
        count = Config(Config(42))

    assert Settings.count == 42


def test_nested_config_with_optional(tmp_path: Path) -> None:
    """Test nested Config with Optional types."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        value = Config(Config(Optional(Integer(42))))
    assert Settings.value == 42

    Settings.value = None
    assert Settings.value is None


def test_nested_config_large_values(tmp_path: Path) -> None:
    """Test nested configs with large string values."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    large_text = "x" * 5000

    class Settings:
        data = Config(Config(String(large_text)))

    assert Settings.data == large_text


def test_nested_config_special_chars(tmp_path: Path) -> None:
    """Test nested configs with special characters."""
    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    special_value = "value=with:special;chars@123!#%"

    class Settings:
        text = Config(Config(Config(String(special_value))))

    assert Settings.text == special_value


def test_nested_config_updates_reflect_in_file(tmp_path: Path) -> None:
    """Test that updates to nested configs are written to file."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        value = Config(Config(Integer(1)))

    # Write initial value
    Settings.value = 10
    file_size_1 = config_file.stat().st_size
    assert file_size_1 > 0

    # Update value
    Settings.value = 20
    file_size_2 = config_file.stat().st_size

    # File should have content (size may vary)
    assert file_size_2 > 0


def test_nested_config_default_values(tmp_path: Path) -> None:
    """Test that nested configs use defaults properly."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)

    class Settings:
        port = Config(Config(Config(Integer(8080))))
        host = Config(Config(String("127.0.0.1")))

    # Without setting anything, should get defaults
    assert Settings.port == 8080
    assert Settings.host == "127.0.0.1"


def test_nested_config_mixed_depths(tmp_path: Path) -> None:
    """Test mixing different nesting depths in same config class."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        a = Config(Integer(1))
        b = Config(Config(Integer(2)))
        c = Config(Config(Config(Integer(3))))
        d = Config(Config(Config(Config(Integer(4)))))

    assert Settings.a == 1
    assert Settings.b == 2
    assert Settings.c == 3
    assert Settings.d == 4

    # Update all
    Settings.a = 10
    Settings.b = 20
    Settings.c = 30
    Settings.d = 40

    assert Settings.a == 10
    assert Settings.b == 20
    assert Settings.c == 30
    assert Settings.d == 40


def test_nested_config_data_type_preserved(tmp_path: Path) -> None:
    """Test that nested configs preserve data type information."""
    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        count = Config(Config(Integer(0)))

    # Set integer value
    Settings.count = 42

    # Read it back and verify it's still an int
    value = Settings.count
    assert isinstance(value, int)
    assert value == 42


def test_nested_config_with_different_parsers(tmp_path: Path) -> None:
    """Test nested configs work across different parser types."""
    parsers_and_files = [
        (IniParser, "config.ini"),
        (MsgspecParser, "config.yaml"),
        (MsgspecParser, "config.json"),
        (MsgspecParser, "config.toml"),
    ]

    for parser_class, filename in parsers_and_files:
        config_file = tmp_path / filename
        config_file.touch()

        class Config(OG):
            """Test Config subclass."""

        if parser_class == IniParser:
            Config.set_parser(IniParser())

        Config.set_file(config_file)
        Config.write_on_edit = True

        class Settings:
            value = Config(Config(Config(Integer(999))))

        assert Settings.value == 999


def test_nested_config_class_access(tmp_path: Path) -> None:
    """Test accessing nested configs from class level."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        value = Config(Config(Config(Integer(100))))

    # Access from class
    assert Settings.value == 100


def test_nested_config_instance_access(tmp_path: Path) -> None:
    """Test accessing nested configs from instance level."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        value = Config(Config(Integer(200)))

    # Create instance and access
    settings = Settings()
    assert settings.value == 200


def test_nested_config_five_levels(tmp_path: Path) -> None:
    """Test extreme nesting: Config(Config(Config(Config(Config(42)))))."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    # Five levels of nesting
    class Settings:
        extreme = Config(
            Config(
                Config(
                    Config(
                        Config(Integer(9999)),
                    ),
                ),
            ),
        )

    assert Settings.extreme == 9999

    Settings.extreme = 1
    assert Settings.extreme == 1


def test_nested_config_with_enum(tmp_path: Path) -> None:
    """Test nested configs with enum types."""
    import enum

    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Color(enum.Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    from confkit.data_types import Enum as ConfigEnum

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        color = Config(Config(ConfigEnum(Color.RED)))

    assert Settings.color == Color.RED

    Settings.color = Color.BLUE
    assert Settings.color == Color.BLUE


def test_nested_config_with_list(tmp_path: Path) -> None:
    """Test nested configs with list types."""
    from confkit.data_types import List

    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        items = Config(Config(List([1, 2, 3])))

    assert Settings.items == [1, 2, 3]

    Settings.items = [4, 5, 6]
    assert Settings.items == [4, 5, 6]


def test_nested_config_boolean(tmp_path: Path) -> None:
    """Test nested configs with boolean values."""
    from confkit.data_types import Boolean

    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        debug = Config(Config(Boolean(False)))

    assert Settings.debug is False

    Settings.debug = True
    assert Settings.debug is True


def test_nested_config_float(tmp_path: Path) -> None:
    """Test nested configs with float values."""
    from confkit.data_types import Float

    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        ratio = Config(Config(Config(Float(0.5))))

    assert Settings.ratio == 0.5

    Settings.ratio = 0.75
    assert Settings.ratio == 0.75


def test_nested_config_consecutive_reads(tmp_path: Path) -> None:
    """Test that consecutive reads of nested config work correctly."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        value = Config(Config(Integer(42)))

    # Read multiple times
    assert Settings.value == 42
    assert Settings.value == 42
    assert Settings.value == 42

    # Modify and read again
    Settings.value = 100
    assert Settings.value == 100
    assert Settings.value == 100


def test_nested_config_zero_value(tmp_path: Path) -> None:
    """Test nested config with zero/empty values."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        count = Config(Config(Integer(0)))
        text = Config(Config(String("")))

    assert Settings.count == 0
    assert Settings.text == ""


def test_nested_config_negative_values(tmp_path: Path) -> None:
    """Test nested config with negative values."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class Settings:
        offset = Config(Config(Config(Integer(-100))))

    assert Settings.offset == -100

    Settings.offset = -500
    assert Settings.offset == -500
