# Examples Overview

This section provides runnable examples demonstrating how to use **confkit** in different scenarios. Each example page includes:

- Purpose & concepts demonstrated
- Required setup (if any)
- How to run the example
- Expected / generated `.ini` configuration contents
- Notes & variations you can try

## Quick Start: Running Examples

All examples assume you are in the project root and have dependencies installed (only the library itself is needed for runtime examples):

```bash
uv run python examples/basic.py
```

> If you are editing examples and want immediate persistence, remember that [`Config.write_on_edit`](pdoc:confkit.Config.write_on_edit) defaults to `True` unless explicitly disabled.

## Example Categories

| Category | Examples | Concepts |
|----------|----------|----------|
| Core Usage | [Basic](basic.md) | Descriptor access, automatic type handling |
| Data Types | [Data Types](data_types.md) | Explicit + formatted numeric types, custom bases |
| Optional & Fallbacks | [Optional Values](optional_values.md) | Nullable values, fallbacks, cascading configs |
| Lists | [List Types](list_types.md) | Escaping, separators, heterogeneous-like usage |
| Enums | [Enums](enums.md) | StrEnum, IntEnum, IntFlag, optional enum values |
| Decorators | [Decorators](decorators.md) | Injecting config into functions |
| argparse Integration | [Argparse](argparse.md) | CLI defaults + config separation |

Select an example in the navigation to dive in.
