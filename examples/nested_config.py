"""Example of nested configuration support in confkit.

This example demonstrates how to use nested classes to organize
configuration values hierarchically. This works with:
- JSON files (native nested objects)
- YAML files (native nested mappings)
- TOML files (nested tables)
- INI files (using dot notation in section names)
"""
from confkit.ext.parsers import IniParser

from pathlib import Path
from typing import TypeVar

from confkit import Config

T = TypeVar("T")

# Example 1: Nested configuration with JSON
print("=== Nested JSON Configuration ===")


class JsonConfig(Config[T]):
    ...


JsonConfig.set_file(Path("nested_example.json"))


class DatabaseConfig:
    """Database configuration with nested credentials."""

    host = JsonConfig("localhost")
    port = JsonConfig(5432)
    name = JsonConfig("myapp_db")

    class Credentials:
        """Nested credentials configuration."""

        username = JsonConfig("admin")
        password = JsonConfig("secret123")
        use_ssl = JsonConfig(True)


# Access nested values
print(f"Database host: {DatabaseConfig.host}")
print(f"Database port: {DatabaseConfig.port}")
print(f"Username: {DatabaseConfig.Credentials.username}")
print(f"Password: {DatabaseConfig.Credentials.password}")
print(f"Use SSL: {DatabaseConfig.Credentials.use_ssl}")

# Example 2: Multiple levels of nesting with YAML
print("\n=== Multi-Level Nested YAML Configuration ===")


class YamlConfig(Config[T]):
    ...


YamlConfig.set_file(Path("nested_example.yaml"))


class ServerConfig:
    """Server configuration with multiple nesting levels."""

    name = YamlConfig("web-server-01")

    class Network:
        """Network configuration."""

        interface = YamlConfig("eth0")

        class IPv4:
            """IPv4 settings."""

            address = YamlConfig("192.168.1.100")
            netmask = YamlConfig("255.255.255.0")
            gateway = YamlConfig("192.168.1.1")

        class IPv6:
            """IPv6 settings."""

            address = YamlConfig("fe80::1")
            prefix = YamlConfig(64)


print(f"Server name: {ServerConfig.name}")
print(f"Network interface: {ServerConfig.Network.interface}")
print(f"IPv4 address: {ServerConfig.Network.IPv4.address}")
print(f"IPv4 netmask: {ServerConfig.Network.IPv4.netmask}")
print(f"IPv6 address: {ServerConfig.Network.IPv6.address}")
print(f"IPv6 prefix: {ServerConfig.Network.IPv6.prefix}")

# Example 3: INI files with dot notation
print("\n=== Nested INI Configuration (using dot notation) ===")


class IniConfig(Config[T]):
    ...


IniConfig._set_parser(IniParser())
IniConfig.set_file(Path("nested_example.ini"))


class AppConfig:
    """Application configuration."""

    version = IniConfig("1.0.0")
    debug = IniConfig(False)

    class Logging:
        """Logging configuration."""

        level = IniConfig("INFO")
        file = IniConfig("app.log")

        class Rotation:
            """Log rotation settings."""

            max_size = IniConfig(10)  # MB
            backup_count = IniConfig(5)


print(f"App version: {AppConfig.version}")
print(f"Debug mode: {AppConfig.debug}")
print(f"Log level: {AppConfig.Logging.level}")
print(f"Log file: {AppConfig.Logging.file}")
print(f"Max log size: {AppConfig.Logging.Rotation.max_size} MB")
print(f"Backup count: {AppConfig.Logging.Rotation.backup_count}")

# Example 4: TOML with nested tables
print("\n=== Nested TOML Configuration ===")


class TomlConfig(Config[T]):
    ...


TomlConfig.set_file(Path("nested_example.toml"))


class ServiceConfig:
    """Service configuration."""

    name = TomlConfig("my-service")
    port = TomlConfig(8080)

    class API:
        """API configuration."""

        version = TomlConfig("v1")
        timeout = TomlConfig(30)

        class RateLimit:
            """Rate limiting configuration."""

            enabled = TomlConfig(True)
            requests_per_minute = TomlConfig(60)


print(f"Service name: {ServiceConfig.name}")
print(f"Service port: {ServiceConfig.port}")
print(f"API version: {ServiceConfig.API.version}")
print(f"API timeout: {ServiceConfig.API.timeout}s")
print(f"Rate limit enabled: {ServiceConfig.API.RateLimit.enabled}")
print(f"Requests per minute: {ServiceConfig.API.RateLimit.requests_per_minute}")

print("\n=== Configuration files created successfully! ===")
print("Check the following files to see the structure:")
print("  - nested_example.json")
print("  - nested_example.yaml")
print("  - nested_example.ini")
print("  - nested_example.toml")
