# confkit

[![Test](https://github.com/HEROgold/confkit/actions/workflows/test.yml/badge.svg)](https://github.com/HEROgold/confkit/actions/workflows/test.yml)
[![Coverage Status](https://coveralls.io/repos/github/HEROgold/confkit/badge.svg?branch=master)](https://coveralls.io/github/HEROgold/confkit?branch=master)

Type-safe configuration manager for Python projects using descriptors and ConfigParser.

Full documentation: [confkit docs](https://HEROgold.github.io/confkit/)

## Supported Python Versions

confkit follows the [Python version support policy](https://devguide.python.org/versions/) as outlined in the Python Developer's Guide:

- We support all active and maintenance releases of Python, starting with 3.11
- End-of-life (EOL) Python versions are **not** supported
- We aim to support Python release candidates to stay ahead of the release cycle

This ensures that confkit remains compatible with current Python versions while allowing us to leverage modern language features.

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

## Getting Started / Usage

For full quickstart, advanced patterns (custom data types, decorators, argparse integration), and runnable examples, visit the documentation site:

👉 [confkit documentation site](https://HEROgold.github.io/confkit/usage)

Direct entry points:

- Quickstart & descriptor patterns: Usage Guide
- All examples: Examples Overview
- Custom datatype tutorial: Custom Data Type example
- API reference: pdoc-generated symbol index

You can still browse example source locally under `examples/`.

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

#### Building Documentation

To build and preview documentation locally:

```bash
# Install documentation dependencies
uv sync --group docs

# Generate API documentation with pdoc
uv run pdoc confkit -o docs/api

# Build documentation site with mkdocs
uv run mkdocs build -d site

# Or serve locally for live preview (with auto-reload)
uv run mkdocs serve
```

Documentation is automatically built and deployed to GitHub Pages when changes are pushed to the `master` branch.

**After updating code that affects documentation:**

1. Update relevant `.md` files in `docs/` directory (examples, reference, etc.)
2. Run `uv run pdoc confkit -o docs/api` to regenerate API documentation
3. Preview changes with `uv run mkdocs serve` and verify at `http://127.0.0.1:8000`
4. Commit both code and documentation changes together
