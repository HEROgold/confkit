# Decorators Example ([`decorators.py`](https://github.com/HEROgold/confkit/blob/master/examples/decorators.py))

## Purpose

Shows how to inject configuration values into functions using decorators:

- [`@Config.with_setting(descriptor)`](pdoc:confkit.Config.with_setting) — injects kwarg named after descriptor
- [`@Config.with_kwarg(section, option, kwarg_name, default)`](pdoc:confkit.Config.with_kwarg) — inject by strings + custom kwarg name

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

- Replace `with_kwarg` with `with_setting` referencing a different descriptor.
