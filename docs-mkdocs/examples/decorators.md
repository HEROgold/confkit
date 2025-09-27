# Decorators Example (`decorators.py`)

## Purpose
Shows how to inject configuration values into functions using decorators:

- `@Config.with_setting(descriptor)` — injects kwarg named after descriptor
- `@Config.with_kwarg(section, option, kwarg_name, default)` — inject by strings + custom kwarg name

## Running
```bash
uv run python examples/decorators.py
```

## Behavior
`ServiceConfig.retry_count` and `ServiceConfig.timeout` are standard descriptors. The decorators wrap the functions so when called, kwargs contain the current config values.

## Example Output (first run)

```text
Processing with 3 retries
```

## Notes

- The `with_kwarg` variant does not require direct descriptor reference (less type-safe, more flexible).
- You can still override the injected kwarg manually when calling the function; manual kwargs win.

## Try Variations

- Change `retry_count` in `config.ini` then re-run only the function call line in a REPL.
- Replace `with_kwarg` with `with_setting` referencing an actual descriptor.
