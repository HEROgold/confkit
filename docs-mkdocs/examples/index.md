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

> If you are editing examples and want immediate persistence, remember that `Config.write_on_edit` defaults to `True` unless explicitly disabled.

## Example Categories

| Category | Examples | Concepts |
|----------|----------|----------|
| Core Usage | `basic.py` | Descriptor access, automatic type handling |
| Data Types | `data_types.py` | Explicit + formatted numeric types, custom bases |
| Optional & Fallbacks | `optional_values.py` | Nullable values, fallbacks, cascading configs |
| Lists | `list_types.py` | Escaping, separators, heterogeneous-like usage |
| Enums | `enums.py` | StrEnum, IntEnum, IntFlag, optional enum values |
| Decorators | `decorators.py` | Injecting config into functions |
| argparse Integration | `argparse_example.py` | CLI defaults + config separation |

Select an example in the navigation to dive in.
