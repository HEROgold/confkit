# confkit - AI Coding Agent Instructions

## Project Overview

confkit is a Python library for type-safe configuration management using descriptors and ConfigParser. It provides automatic type conversion, validation, and persistence of configuration values in INI files.

## Core Architecture

### Key Components

- `Config` descriptor (`config.py`): The main descriptor class that handles getting/setting values in INI files
- `BaseDataType` and implementations (`data_types.py`): Type converters for different data types
- `sentinels.py`: Provides the `UNSET` sentinel value for representing unset values
- `exceptions.py`: Custom exceptions for configuration errors

### Data Flow

1. `Config` descriptors are defined as class variables in user-defined config classes
1. On access, the descriptor reads from the INI file and converts to the appropriate type
1. On assignment, the descriptor validates and writes values back to the INI file

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

```python
# Example from examples/basic.py


class AppConfig:
    debug = Config(False)
    port = Config(8080)
    host = Config("localhost")
    timeout = Config(30.5)
    api_key = Config("", optional=True)


def main():
    # Read values from config
    print(f"Debug mode: {Config.debug}")
    print(f"Server port: {Config.port}")
    print(f"Host: {Config.host}")
    print(f"Timeout: {Config.timeout}s")
```

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

Always initialize Config with parser and file before use:

```python
# file: config.py

from configparser import ConfigParser
from pathlib import Path
from confkit import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))
```

### List Type Handling

List types require special handling for escaping and separators:

```python
# From examples/list_types.py
List.escape_char = "\\"  # Default
List.separator = ","  # Default
```

### Project Conventions

1. Type-safety is enforced by default (`Config.validate_types = True`)
1. Automatic writing to INI file is enabled by default (`Config.write_on_edit = True`)
1. Python 3.12+ is required for the type syntax used

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
