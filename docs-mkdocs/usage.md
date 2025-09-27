---
title: Usage Guide
---

# Usage

This page explains how to work with confkit and how the documentation is generated using both `mkdocstrings` and the `mkdocs-pdoc-plugin` for deep API symbol cross-references.

## Regenerating API Docs (pdoc)

The `api/` directory inside `docs-mkdocs/` is produced by `pdoc`. Regenerate it after changing code-level docstrings or adding new public classes/functions.

```bash
uv run pdoc confkit -o docs-mkdocs/api --force
```

Key points:

1. `--force` overwrites existing output
2. The MkDocs plugin (configured in `mkdocs.yml` as `pdoc: { api_path: api }`) enables links like `(pdoc:confkit.config.Config)` inside Markdown
3. Reference pages in `reference/` intentionally use those links for stable deep-links

## Descriptor Quickstart

```python
from configparser import ConfigParser
from pathlib import Path
from confkit import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

class AppConfig:
	debug = Config(False)
	port = Config(8080)

cfg = AppConfig()
print(cfg.port)
```

## Adding a New Data Type

1. Subclass `BaseDataType[T]`
2. Implement `convert(self, value: str) -> T`
3. (Optional) override `__str__` for serialization
4. Use via `Config(CustomType(default_value))`

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
- `Config.with_kwarg(section, option, name?, default?)` – inject by strings (alias of doc concept "as_kwarg")

See also: the dedicated reference pages for cross-linked signatures.

