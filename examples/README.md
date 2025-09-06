# Confkit Examples

This directory contains examples showing how to use the `confkit` library for configuration management in Python applications.

## Running the Examples

All examples can be run directly with Python. They use a shared `config.ini` file for configuration.

```bash
python basic.py
```

## Example Files

### Basic Usage

- **basic.py**: Shows the fundamental usage of confkit with basic data types.
  - Setting up the configuration parser and file
  - Defining a configuration class
  - Accessing and modifying configuration values

### Data Types

- **data_types.py**: Demonstrates the various data types available in confkit.
  - Using primitive data types (int, float, bool, str)
  - Using specialized number formats (hex, octal, binary)
  - Custom base integers
  - Type validation and conversion

### List Types

- **list_types.py**: Shows how to work with list configurations.
  - Lists of different data types
  - Handling lists with special characters
  - Escaping in lists
  - Empty lists and list validation

### Enums

- **enums.py**: Demonstrates enum support in confkit.
  - Using standard Python Enum classes with confkit
  - Using StrEnum, IntEnum, and IntFlag with confkit
  - Type-safe configuration with enums
  - Optional enum configurations

### Decorators

- **decorators.py**: Shows how to use the decorator functions provided by confkit.
  - Using the with_setting decorator to inject config values
  - Using the as_kwarg decorator to customize parameter injection
  - Using set and default decorators to set configuration values

### Optional Values

- **optional_values.py**: Demonstrates working with optional values.
  - Working with optional values that can be None
  - Using Optional wrapper with different data types
  - Handling validation and type safety with optional values
  - Creating cascading configurations with fallbacks

### Configuration Management

- **config_management.py**: Shows advanced configuration file management.
  - Managing configuration files and parsers
  - Global settings like write_on_edit and validate_types
  - Handling multiple configuration files
  - Configuration validation and error handling

### Advanced Patterns

- **advanced_patterns.py**: Demonstrates advanced usage patterns.
  - Class-level configuration inheritance
  - Working with complex nested configurations
  - Handling configuration errors gracefully
  - Runtime configuration changes
  - Performance considerations

### Logging Integration

- **logging_integration.py**: Shows how to integrate confkit with Python's logging system.
  - Configuring logging with confkit
  - Dynamic log level changes
  - Handler configuration via confkit
  - Custom formatters with confkit settings

## Configuration File

All examples share the `config.ini` file for storing configuration values. This file is automatically created and updated when you run the examples.
