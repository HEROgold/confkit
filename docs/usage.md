---
title: Usage Guide
---

# Usage

This page explains how to work with confkit and how the documentation is generated.

## Descriptor Quickstart

```python
from configparser import ConfigParser
from pathlib import Path
from confkit import Config

# 1. Configure confkit parser/file (normally app bootstrap)
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

# 2. Define your (class)variables with their default values
class AppConfig:
    debug = Config(False)
    port = Config(8080)

# 3. use them!
# (this value came from the .ini file!) 
print(AppConfig.port)
```

## Adding a New Data Type

1. Subclass `BaseDataType[T]`
2. Implement `convert(self, value: str) -> T`
3. (Optional) override `__str__` for serialization
4. Use via `Config(CustomType(default_value))`

```python
from configparser import ConfigParser
from pathlib import Path
from confkit import Config
from confkit.data_types import BaseDataType

# 1. Configure confkit parser/file (normally app bootstrap)
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

# 2. Define the custom converter, with a convert method (from str -> your_type)
class UpperString(BaseDataType[str]):
    def convert(self, value: str) -> str:  # str from INI -> normalized value
        return str(value).upper()

    def __str__(self, value: str):  # value -> string for INI
        return value.upper()

# 3. Use the custom datatype inside a config class
class CustomCfg:
    shout_name = Config(UpperString("confkit"))

print(CustomCfg.shout_name)  # -> CONFKIT
CustomCfg.shout_name = "mixedCase"
print(CustomCfg.shout_name)  # -> MIXEDCASE
```

Full runnable example: [`examples/custom_data_type.py`](https://github.com/HEROgold/confkit/blob/master/examples/custom_data_type.py).

## Optional Values

Either pass `optional=True` to `Config(...)` or wrap a data type in `Optional(...)`.

```python
from confkit.data_types import Optional, String

class Service:
    api_key = Config("", optional=True)                    # primitive optional
    token = Config(Optional(String("")))                   # wrapped optional
```

## Decorators Overview

- `Config.set(section, option, value)` – always sets before call
- `Config.default(section, option, value)` – sets only when missing
- `Config.with_setting(descriptor)` – injects descriptor value by name
- `Config.with_kwarg(section, option, name?, default?)` – inject by strings

See also: the dedicated reference pages for cross-linked signatures.

## Regenerating API Docs (pdoc + mkdocs)

The documentation is using both `mkdocstrings` and the `mkdocs-pdoc-plugin` for deep API symbol cross-references.
The `api/` directory inside `docs-mkdocs/` is produced by `pdoc`. Regenerate it after changing code-level docstrings or adding new public classes/functions.

```bash
uv run pdoc confkit -o docs-mkdocs/api --force
```

Key points:

1. `--force` overwrites existing output
2. The MkDocs plugin (configured in `mkdocs.yml` as `pdoc: { api_path: api }`) enables links like `(pdoc:confkit.config.Config)` inside Markdown
3. Reference pages in `reference/` intentionally use those links for stable deep-links
