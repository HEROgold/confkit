# confkit - AI Coding Agent Instructions

## Project Overview

confkit is a Python library for type-safe configuration management using descriptors. It provides automatic type conversion, validation, and persistence of configuration values. Supports multiple file formats including INI, JSON, YAML, TOML, and .env files.

## Core Architecture

### Key Components

- `Config` descriptor (`config.py`): The main descriptor class that handles getting/setting values in config files
- `ConfigContainerMeta` (`config.py`): Metaclass that enables setting Config descriptors on class variables
- `BaseDataType` and implementations (`data_types.py`): Type converters for different data types
- `ConfkitParser` protocol (`ext/parsers.py`): Protocol defining the parser interface
- `MsgspecParser` (`ext/parsers.py`): Parser for JSON, YAML, and TOML files
- `EnvParser` (`ext/parsers.py`): Parser for environment variables and .env files
- `sentinels.py`: Provides the `UNSET` sentinel value for representing unset values
- `exceptions.py`: Custom exceptions for configuration errors
- `watcher.py`: File watching functionality to detect config file changes

### Data Flow

1. `Config` descriptors are defined as class variables in user-defined config classes
1. On first access, the parser automatically reads from the config file (cached with `_has_read_config` flag)
1. The descriptor reads the value and converts it to the appropriate type using the assigned `BaseDataType`
1. On assignment, the descriptor validates the value and writes it back to the config file (if `write_on_edit=True`)
1. File changes are detected via `FileWatcher` and trigger `on_file_change` callbacks

## Development Workflow

### Setup

```bash
# Clone the repo
git clone https://github.com/HEROgold/confkit.git
cd confkit

# Install dependencies with uv
uv sync --group test
```

### Testing

```bash
# Run linting
ruff check .
# Update dependencies and run tests
uv sync --upgrade --group dev; uv run pytest .
```

### Key Patterns

#### Defining Config Types

Config descriptors can be defined in three ways:

1. Simple types: `name = Config(default_value)`
1. Custom data types: `name = Config(CustomType(default_value))`
1. Optional values: `name = Config(default_value, optional=True)` or `name = Config(Optional(CustomType(default_value)))`

For complete examples, see the `examples/` directory which includes:
- `basic.py` - Basic configuration setup with INI files
- `other_file_types.py` - Using JSON, YAML, and TOML files
- `decorators.py` - Using decorator patterns for config management
- `data_types.py` - Custom data type examples
- `list_types.py` - Working with list configurations
- `optional_values.py` - Handling optional configuration values
- `enums.py` - Using enums for configuration
- `custom_data_type.py` - Creating custom data types
- `multiple_configs.py` - Managing multiple configuration classes
- `file_change_event.py` - Handling file change events
- `pydantic_example.py` - Integration with Pydantic models
- `references.py` - Using configuration references
- `argparse_example.py` - Integration with argparse
- `url_example.py` - URL configuration examples

#### Type Converters

The library uses a pattern of type converters to handle different data types:

```python
# From src/confkit/data_types.py
class String(BaseDataType[str]):
    def convert(self, value: str) -> str:
        return value

    def __str__(self, value: str):
        # Apropriatly modified string representation of the used datatype.
        return value
```

#### Decorator Pattern

There are several decorators available for working with config values:

```python
# From examples/decorators.py
# Injects the retry_count config value into kwargs
@Config.with_setting(retry_count)
def process(self, data, **kwargs):
    retries = kwargs.get("retry_count")
    return f"Processing with {retries} retries"


# Injects the config value with a custom kwarg name
@Config.with_kwarg("ServiceConfig", "timeout", "request_timeout", 60)
def request(self, url, **kwargs):
    timeout = kwargs.get("request_timeout")
    return f"Request timeout: {timeout}s"


# Sets a config value when the function is called
@Config.set("AppConfig", "debug", True)
def enable_debug_mode():
    print("Debug mode enabled")


# Sets a default config value if none exists yet
@Config.default("AppConfig", "timeout", 30)
def initialize_timeout():
    print("Timeout initialized")
```

#### Alternative Methods vs Descriptor Approach

While the descriptor approach is the preferred method for simplicity and type safety, there are alternative ways to access configuration:

| Method                | Use Case                                        | Example                                                |
| --------------------- | ----------------------------------------------- | ------------------------------------------------------ |
| Descriptor            | Primary, type-safe approach                     | `config = AppConfig(); config.debug = True`            |
| `Config.set`          | Imperatively setting values                     | `@Config.set("Section", "setting", value)`             |
| `Config.default`      | Setting values only if not set                  | `@Config.default("Section", "setting", default_value)` |
| `Config.with_setting` | Injecting existing configs into function kwargs | `@Config.with_setting(retry_count)`                    |
| `Config.with_kwarg`     | Injecting configs with custom names             | `@Config.with_kwarg("Section", "setting", "kwarg_name")` |

**IMPORTANT**: The descriptor approach is strongly preferred for its type safety and simplicity.

#### Method Differences Explained

**Config.set vs Config.default**:

- `Config.set`: Always sets the specified value, overwriting any existing value
- `Config.default`: Only sets the value if it doesn't already exist in the config file
- Use `Config.set` when you need to enforce a specific value
- Use `Config.default` for providing initial values without overriding user settings

**Config.with_setting vs Config.with_kwarg**:

- `Config.with_setting`: Takes an existing Config descriptor and injects its value
  ```python
  # Must reference an existing Config descriptor
  class Processor:
      retry_count = Config(5)

      @staticmethod
      @Config.with_setting(retry_count)
      def process(data, **kwargs):
          retries = kwargs.get("retry_count")  # Name matches descriptor name
  ```
- `Config.with_kwarg`: References a config by section/setting and can rename the kwarg
  ```python
  # References by string names, can set a custom kwarg name
  # Section, Option, kwargName, value
  @Config.with_kwarg("AppConfig", "timeout", "request_timeout", 60)
  def request(url, **kwargs):
      timeout = kwargs.get("request_timeout")  # Custom name in kwargs
  ```

The `with_setting` approach is more type-safe as it references an actual descriptor, while `with_kwarg` allows more flexibility with naming and providing fallback values.

## Critical Information

### Required Initialization

Always initialize Config with a file path before use. The parser can be set explicitly or will be auto-detected based on file extension:

```python
from pathlib import Path
from confkit import Config

# Option 1: Auto-detect parser based on file extension
Config.set_file(Path("config.ini"))  # Uses ConfigParser
Config.set_file(Path("config.json"))  # Uses MsgspecParser
Config.set_file(Path("config.yaml"))  # Uses MsgspecParser
Config.set_file(Path("config.toml"))  # Uses MsgspecParser
Config.set_file(Path(".env"))  # Uses EnvParser

# Option 2: Explicitly set parser (not recommended unless it's absolutely required.)
from configparser import ConfigParser
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))
```

### Supported File Formats

- **INI files** (`.ini`): Uses Python's `ConfigParser`, supports sections
- **JSON files** (`.json`): Uses `MsgspecParser`, requires `msgspec` extra
- **YAML files** (`.yaml`, `.yml`): Uses `MsgspecParser`, requires `msgspec` extra
- **TOML files** (`.toml`): Uses `MsgspecParser`, requires `msgspec` extra
- **Environment files** (`.env`): Uses `EnvParser`, no sections (flat key-value pairs)

### List Type Handling

List types require special handling for escaping and separators:

```python
# From examples/list_types.py
List.escape_char = "\\"  # Default
List.separator = ","  # Default
```

### Project Conventions

1. Type-safety is enforced by default (`Config.validate_types = True`)
1. Automatic writing to config file is enabled by default (`Config.write_on_edit = True`)
1. Python 3.11+ is required (3.12+ recommended for native type syntax)
1. File changes are monitored via `FileWatcher` for automatic reloading

## Common Tasks

### Creating New Data Types

1. Subclass `BaseDataType[T]` where T is the target type
1. Implement the `convert` method to handle string-to-type conversion
1. Optionally override `__str__` for custom string representation

### Testing

Test files follow a pattern:

- Use `hypothesis` strategies for property-based testing
- Test with various input types and edge cases
- Test custom data types separately from the main Config class

## External Dependencies

This library has no external runtime dependencies, making it lightweight and suitable for many projects.
