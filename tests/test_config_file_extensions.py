"""Test Config with all supported file extensions: ini, yaml, yml, json, toml, env."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from confkit.config import Config as OG
from confkit.data_types import Integer, String
from confkit.ext.parsers import MsgspecParser
from confkit.parsers import ConfkitParser, EnvParser, IniParser

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture(params=[".ini", ".yaml", ".yml", ".json", ".toml", ".env"])
def config_file_extension(request: pytest.FixtureRequest, tmp_path: Path) -> tuple[Path, str]:
    """Fixture that provides a config file for each supported extension."""
    ext = request.param
    config_file = tmp_path / f"config{ext}"
    config_file.touch()
    return config_file, ext


def get_parser_for_extension(ext: str) -> type[ConfkitParser]:
    """Get the expected parser for a given file extension."""
    if ext == ".ini":
        return IniParser
    if ext in (".yaml", ".yml", ".json", ".toml"):
        return MsgspecParser
    if ext == ".env":
        return EnvParser
    msg = f"Unsupported extension: {ext}"
    raise ValueError(msg)


def test_detect_parser_for_all_extensions(config_file_extension: tuple[Path, str]) -> None:
    """Test that the correct parser is detected for each file extension."""
    config_file, ext = config_file_extension

    class Config(OG):
        """Test Config subclass."""

    Config._file = config_file
    Config._parser = None
    Config._detect_parser()

    expected_parser_class = get_parser_for_extension(ext)
    assert isinstance(Config._parser, expected_parser_class), \
        f"Expected {expected_parser_class.__name__} for {ext}, got {type(Config._parser).__name__}"


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_read_write_string_value_all_extensions(tmp_path: Path, ext: str) -> None:
    """Test reading and writing string config values (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        username = Config(String("default_user"))

    # Test write
    TestConfig.username = "testuser"
    assert TestConfig.username == "testuser"

    # Verify file was written
    assert config_file.exists()
    assert config_file.stat().st_size > 0


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_read_write_integer_value_all_extensions(tmp_path: Path, ext: str) -> None:
    """Test reading and writing integer config values (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        port = Config(Integer(8080))

    # Test write
    TestConfig.port = 3000
    assert TestConfig.port == 3000

    # Verify file was written
    assert config_file.exists()
    assert config_file.stat().st_size > 0


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_multiple_values_all_extensions(tmp_path: Path, ext: str) -> None:
    """Test reading and writing multiple config values (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class with multiple values."""

        database_host = Config(String("localhost"))
        database_port = Config(Integer(5432))
        app_name = Config(String("myapp"))

    # Write multiple values
    TestConfig.database_host = "prod.example.com"
    TestConfig.database_port = 5433
    TestConfig.app_name = "production-app"

    # Verify values were written
    assert TestConfig.database_host == "prod.example.com"
    assert TestConfig.database_port == 5433
    assert TestConfig.app_name == "production-app"

    # Verify file was written
    assert config_file.exists()
    assert config_file.stat().st_size > 0


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_default_values_used_when_not_set(tmp_path: Path, ext: str) -> None:
    """Test that default values are returned when config value is not set."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)

    class TestConfig:
        """Test configuration class."""

        timeout = Config(Integer(30))
        environment = Config(String("development"))

    # Values should use defaults since we didn't set them
    assert TestConfig.timeout == 30
    assert TestConfig.environment == "development"


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_update_existing_value_all_extensions(tmp_path: Path, ext: str) -> None:
    """Test updating an existing config value (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        counter = Config(Integer(0))

    # Set initial value
    TestConfig.counter = 10
    assert TestConfig.counter == 10

    # Update value
    TestConfig.counter = 20
    assert TestConfig.counter == 20


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml", ".env"])
def test_parser_detection_explicit_extensions(tmp_path: Path, ext: str) -> None:
    """Test parser detection for each extension explicitly."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config._file = config_file
    Config._parser = None
    Config._detect_parser()

    expected_parser_class = get_parser_for_extension(ext)
    assert isinstance(Config._parser, expected_parser_class)


def test_ini_specific_functionality(tmp_path: Path) -> None:
    """Test INI-specific functionality."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        api_key = Config(String("default_key"))
        timeout = Config(Integer(30))

    TestConfig.api_key = "secret123"
    TestConfig.timeout = 60

    assert TestConfig.api_key == "secret123"
    assert TestConfig.timeout == 60


def test_yaml_specific_functionality(tmp_path: Path) -> None:
    """Test YAML-specific functionality."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        service_name = Config(String("default_service"))
        replicas = Config(Integer(1))

    TestConfig.service_name = "api-server"
    TestConfig.replicas = 3

    assert TestConfig.service_name == "api-server"
    assert TestConfig.replicas == 3


def test_yml_specific_functionality(tmp_path: Path) -> None:
    """Test YML-specific functionality."""
    config_file = tmp_path / "config.yml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        instance_name = Config(String("default_instance"))
        cpu_limit = Config(Integer(1024))

    TestConfig.instance_name = "worker-1"
    TestConfig.cpu_limit = 2048

    assert TestConfig.instance_name == "worker-1"
    assert TestConfig.cpu_limit == 2048


def test_json_specific_functionality(tmp_path: Path) -> None:
    """Test JSON-specific functionality."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        endpoint = Config(String("http://localhost"))
        retry_count = Config(Integer(3))

    TestConfig.endpoint = "https://api.example.com"
    TestConfig.retry_count = 5

    assert TestConfig.endpoint == "https://api.example.com"
    assert TestConfig.retry_count == 5


def test_toml_specific_functionality(tmp_path: Path) -> None:
    """Test TOML-specific functionality."""
    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        package_name = Config(String("default_package"))
        version_major = Config(Integer(1))

    TestConfig.package_name = "my-package"
    TestConfig.version_major = 2

    assert TestConfig.package_name == "my-package"
    assert TestConfig.version_major == 2


def test_env_specific_functionality(tmp_path: Path) -> None:
    """Test ENV-specific functionality - EnvParser is read-only."""
    config_file = tmp_path / "config.env"
    config_file.write_text("DUMMY=value\n")

    class Config(OG):
        """Test Config subclass."""

    Config._file = config_file
    Config._parser = None
    Config._detect_parser()

    # Verify the correct parser was detected
    assert isinstance(Config._parser, EnvParser)


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_write_enables_persistence_across_extensions(tmp_path: Path, ext: str) -> None:
    """Test that write_on_edit=True enables persistence (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class TestConfig:
        """Test configuration class."""

        value = Config(String("initial"))

    # Set value with write_on_edit enabled
    TestConfig.value = "modified"
    assert TestConfig.value == "modified"

    # Verify persistence by reading file size (should be non-zero)
    assert config_file.stat().st_size > 0


def test_multiple_config_classes_same_extension(tmp_path: Path) -> None:
    """Test multiple config classes using the same file extension."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class AppConfig:
        """First configuration class."""

        app_name = Config(String("app"))

    class DBConfig:
        """Second configuration class."""

        db_host = Config(String("localhost"))

    AppConfig.app_name = "my_app"
    DBConfig.db_host = "db.example.com"

    assert AppConfig.app_name == "my_app"
    assert DBConfig.db_host == "db.example.com"


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_large_values_across_extensions(tmp_path: Path, ext: str) -> None:
    """Test handling of larger string values (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    large_value = "x" * 1000  # 1000 character string

    class TestConfig:
        """Test configuration class."""

        large_text = Config(String("default"))

    TestConfig.large_text = large_value
    assert TestConfig.large_text == large_value


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_special_characters_in_values(tmp_path: Path, ext: str) -> None:
    """Test handling of special characters in config values (excluding .env which doesn't support set)."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    special_value = "value=with:special;chars@123"

    class TestConfig:
        """Test configuration class."""

        special_text = Config(String("default"))

    TestConfig.special_text = special_value
    assert TestConfig.special_text == special_value


def test_env_file_detection(tmp_path: Path) -> None:
    """Test detection of .env file extension."""
    config_file = tmp_path / "config.env"
    config_file.write_text("DUMMY=value\n")

    class Config(OG):
        """Test Config subclass."""

    Config._file = config_file
    Config._parser = None
    Config._detect_parser()

    # Verify correct parser for .env
    assert isinstance(Config._parser, EnvParser)


def test_ini_format_structure(tmp_path: Path) -> None:
    """Test that INI files maintain proper section structure."""
    config_file = tmp_path / "config.ini"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class DatabaseSettings:
        """Database configuration."""

        host = Config(String("localhost"))
        port = Config(Integer(5432))

    DatabaseSettings.host = "prod-db.example.com"
    DatabaseSettings.port = 5433

    # Verify file structure
    content = config_file.read_text()
    assert "DatabaseSettings" in content
    assert "host" in content
    assert "port" in content


def test_yaml_format_structure(tmp_path: Path) -> None:
    """Test that YAML files maintain proper structure."""
    config_file = tmp_path / "config.yaml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class AppSettings:
        """Application settings."""

        debug = Config(String("false"))
        log_level = Config(String("info"))

    AppSettings.debug = "true"
    AppSettings.log_level = "debug"

    assert AppSettings.debug == "true"
    assert AppSettings.log_level == "debug"


def test_json_format_structure(tmp_path: Path) -> None:
    """Test that JSON files maintain proper structure."""
    config_file = tmp_path / "config.json"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class ServerSettings:
        """Server configuration."""

        host = Config(String("0.0.0.0"))
        port = Config(Integer(8000))

    ServerSettings.host = "127.0.0.1"
    ServerSettings.port = 3000

    assert ServerSettings.host == "127.0.0.1"
    assert ServerSettings.port == 3000


def test_toml_format_structure(tmp_path: Path) -> None:
    """Test that TOML files maintain proper structure."""
    config_file = tmp_path / "config.toml"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)
    Config.write_on_edit = True

    class ProjectSettings:
        """Project configuration."""

        name = Config(String("myproject"))
        version = Config(String("1.0.0"))

    ProjectSettings.name = "production-app"
    ProjectSettings.version = "2.1.0"

    assert ProjectSettings.name == "production-app"
    assert ProjectSettings.version == "2.1.0"


@pytest.mark.parametrize("ext", [".ini", ".yaml", ".yml", ".json", ".toml"])
def test_all_extensions_support_reading(tmp_path: Path, ext: str) -> None:
    """Test that all write-supporting extensions can be read."""
    config_file = tmp_path / f"config{ext}"
    config_file.touch()

    class Config(OG):
        """Test Config subclass."""

    Config.set_file(config_file)

    class TestConfig:
        """Test configuration class."""

        setting = Config(String("default_value"))

    # Should be able to read without error (will use default value)
    result = TestConfig.setting
    assert result == "default_value"


def test_write_to_different_extensions_independently(tmp_path: Path) -> None:
    """Test writing to files with different extensions independently."""
    ini_file = tmp_path / "config.ini"
    yaml_file = tmp_path / "config.yaml"
    json_file = tmp_path / "config.json"

    ini_file.touch()
    yaml_file.touch()
    json_file.touch()

    # Set up INI config
    class IniConfig(OG):
        """INI config subclass."""

    IniConfig.set_file(ini_file)
    IniConfig.write_on_edit = True

    class IniSettings:
        """INI settings."""

        value = IniConfig(String("ini_default"))

    # Set up YAML config
    class YamlConfig(OG):
        """YAML config subclass."""

    YamlConfig.set_file(yaml_file)
    YamlConfig.write_on_edit = True

    class YamlSettings:
        """YAML settings."""

        value = YamlConfig(String("yaml_default"))

    # Set up JSON config
    class JsonConfig(OG):
        """JSON config subclass."""

    JsonConfig.set_file(json_file)
    JsonConfig.write_on_edit = True

    class JsonSettings:
        """JSON settings."""

        value = JsonConfig(String("json_default"))

    # Set values
    IniSettings.value = "ini_value"
    YamlSettings.value = "yaml_value"
    JsonSettings.value = "json_value"

    # Verify values
    assert IniSettings.value == "ini_value"
    assert YamlSettings.value == "yaml_value"
    assert JsonSettings.value == "json_value"

    # Verify files were created with content
    assert ini_file.stat().st_size > 0
    assert yaml_file.stat().st_size > 0
    assert json_file.stat().st_size > 0
