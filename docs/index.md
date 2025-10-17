# Confkit

Lightweight, type-safe configuration via descriptors on plain Python classes.

This landing page orients you quickly:

| Topic | Where to Go |
|-------|-------------|
| Run examples | Examples section (navigation) or [Examples overview](examples/index.md) |
| Create a custom data type | Usage Guide: [Adding a New Data Type](usage.md#adding-a-new-data-type) |
| See all data type converters | [Reference: Data Types](reference/data_types.md) |
| Decorator utilities | [Usage: Decorators Overview](usage.md#decorators-overview) |
| API by symbol | [Generated API (pdoc)](pdoc:confkit) |
| Contribute / issues | GitHub Repo: [HEROgold/confkit](https://github.com/HEROgold/confkit) |

---

## Examples

Explore focused example pages:

- Basic primitives & persistence: [`Basic`](examples/basic.md)
- Data types (hex, octal, binary, bases): [`Data types`](examples/data_types.md)
- Optional & cascading configs: [`Optional values`](examples/optional_values.md)
- Lists & escaping: [`List types`](examples/list_types.md)
- Enums & flags: [`Enums`](examples/enums.md)
- Decorator injection patterns: [`Decorators`](examples/decorators.md)
- Argparse integration: [`Argparse`](examples/argparse.md)
- Custom converter (UpperString): [Custom Data Type](examples/custom_data_type.md)

Need a new scenario? Open an issue or PR (see Contributing below).

---

## Contributing

We welcome:

1. Additional data type converters
2. Validation enhancements and edge-case handling
3. Improved documentation examples / tutorials
4. Bug reports with minimal reproduction scripts

Workflow (after forking or a feature branch):

```bash
uv sync --group dev
uv run pytest -q
uv run ruff check .
uv sync --group docs
uv run pdoc confkit -o docs/api
uv run mkdocs build -d site
```

Before opening a PR, ensure:

- All tests pass (including property-based tests)
- No ruff or type errors (pyright config in project)
- Updated docs where behavior changed

---

## Supported Python Versions

confkit follows the [Python version support policy](https://devguide.python.org/versions/) as outlined in the Python Developer's Guide:

- We support all active and maintenance releases of Python above 3.11
- End-of-life (EOL) Python versions are **not** supported
- We aim to support Python release candidates to stay ahead of the release cycle

This ensures that confkit remains compatible with current Python versions while allowing us to leverage modern language features.

## API Reference

Two complementary views:

### High-level curated reference pages

- [Config](reference/config.md)
- [Data Types](reference/data_types.md)
- [Exceptions](reference/exceptions.md)

### Full symbol index (pdoc)

[confkit API](pdoc:confkit)

Use `(pdoc:qual.name)` style links inside docs for deep, stable symbol links

```md
The [MyClass](pdoc:mypackage.MyClass) class is awesome.
The [do_something](pdoc:mypackage.MyClass.do_something) method is awesome.
The [](mypackage.MyClass) class is awesome.
```

---

## When to Use confkit

Use confkit when you want:

- Simple, configuration management
- Type conversion and validation baked in
- Declarative, descriptor-based definitions instead of manual parsing

If you need hierarchical, nested config trees or schema evolution with migrations, pair confkit with a higher-level orchestrator or consider extending with custom data types.

---

## Next Steps

Head to the [Usage Guide](usage.md) for deeper patterns, or jump straight into an [Example](examples/index.md).
