# Basic Example ([`basic.py`](https://github.com/HEROgold/confkit/blob/master/examples/basic.py))

## Purpose

Demonstrates the foundational usage of `confkit`:

- Setting a parser + backing file
- Defining a config class with different primitive types
- Automatic persistence via `Config.write_on_edit`
- Accessing & mutating values via descriptor access

## Code Summary

[`examples/basic.py`](https://github.com/HEROgold/confkit/blob/master/examples/basic.py) defines `AppConfig` with boolean, int, string, float, and optional string fields.

## Running

```bash
uv run python examples/basic.py
```

If `config.ini` does not yet exist it will be created automatically.

## Generated / Updated `config.ini`

A first run typically produces something like:

```ini
[AppConfig]
debug = False
port = 8080
host = localhost
timeout = 30.5
api_key = 
```

After the script executes (it changes `port` and sets `api_key`), the file becomes:

```ini
[AppConfig]
debug = False
port = 9000
host = localhost
timeout = 30.5
api_key = my-secret-key
```

## Try Variations

- Set `Config.write_on_edit = False` and observe that changes are not written.
- Manually edit `config.ini` then re-run to see those values picked up.

## Key Takeaways

The descriptor interface gives you type-safe access. Mutations immediately persist (when enabled) without needing manual write calls.
