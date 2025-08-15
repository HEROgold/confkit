# confkit

[![Test](https://github.com/HEROgold/confkit/actions/workflows/test.yml/badge.svg)](https://github.com/HEROgold/confkit/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/HEROgold/confkit/badge.svg?branch=master)](https://coveralls.io/github/HEROgold/confkit?branch=master)

Type-safe configuration manager for Python projects using descriptors and ConfigParser.

## What is it?

confkit is a Python library that provides type-safe configuration management with automatic type conversion and validation.
It uses descriptors to define configuration values as class attributes that automatically read from and write to INI files.

## What does it do?

- Type-safe configuration with automatic type conversion
- Automatic INI file management
- Default value handling with file persistence
- Optional value support
- Enum support (Enum, StrEnum, IntEnum, IntFlag)
- Method decorators for injecting configuration values
- Runtime type validation

## How to use it?

### Setup

```python
from configparser import ConfigParser
from pathlib import Path
from confkit import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))
```

### Basic Usage

- Note: imports have been left out. see [examples/basic.py](basic.py) for the entire example.

```python
class AppConfig:
    debug = Config(False)
    port = Config(8080)
    host = Config("localhost")
    timeout = Config(30.5)
    api_key = Config("", optional=True)

config = AppConfig()
print(config.debug)  # False
config.port = 9000   # Automatically saves to config.ini if write_on_edit is true (default).
```

### Enums and Custom Types

- Note: imports have been left out. see [examples/enums.py](enums.py) for the entire example.

```python
class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    ERROR = "error"

class ServerConfig:
    log_level = Config(ConfigEnum(LogLevel.INFO))
    db_url = Config(String("sqlite:///app.db"))
    fallback_level = Config(Optional(ConfigEnum(LogLevel.ERROR)))

config = ServerConfig()
config.log_level = LogLevel.DEBUG  # Type-safe
```

### Method Decorators

- Note: imports have been left out. see [examples/decorators.py](decorators.py) for the entire example.

```python
class ServiceConfig:
    retry_count = Config(3)
    timeout = Config(30)

    @Config.with_setting(retry_count)
    def process(self, data, **kwargs):
        retries = kwargs.get('retry_count')
        return f"Processing with {retries} retries"

    @Config.as_kwarg("ServiceConfig", "timeout", "request_timeout", 60)
    def request(self, url, **kwargs):
        timeout = kwargs.get('request_timeout')
        return f"Request timeout: {timeout}s"

service = ServiceConfig()
result = service.process("data")  # Uses current retry_count
```

### Configuration File

Generated INI file structure see [examples/config.ini](config.ini) for the entire example.:

```ini
[AppConfig]
debug = False
port = 9000
host = localhost
timeout = 30.5
api_key = 

[ServiceConfig]
retry_count = 3
timeout = 30

[ServerConfig]
log_level = debug
db_url = sqlite:///app.db
fallback_level = error
```

## How to contribute?

1. Fork the repository and clone locally
2. Install dependencies: `uv sync --group test`
3. Run tests: `pytest .`
4. Run linting: `ruff check .`
5. Make changes following existing patterns
6. Add tests for new functionality
7. Submit a pull request

### Development

```bash
git clone https://github.com/HEROgold/confkit.git
cd confkit
uv sync --group test
pytest .
ruff check .
```
