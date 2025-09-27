# Enums Example ([`enums.py`](https://github.com/HEROgold/confkit/blob/master/examples/enums.py))

## Purpose

Demonstrates enum support:

- [`StrEnum`](pdoc:confkit.StrEnum), [`IntEnum`](pdoc:confkit.IntEnum), [`IntFlag`](pdoc:confkit.IntFlag), usage via dedicated data types
- Optional enum values
- Bitwise flag composition (`Permission`)

## Running

```bash
uv run python examples/enums.py
```

## Generated `config.ini` (Excerpt)

```ini
[ServerConfig]
log_level = info
default_priority = 5
default_permission = 1
fallback_level = error
environment = info
```

If values are changed in code (or by assignment at runtime) they persist accordingly.

## Notes

- `IntFlag` values are stored as their integer bitfield representation.
- Optional enum fields removed (set to `None`) disappear from the file.

## Try Variations

- Manually set `default_permission = 7` (READ|WRITE|EXECUTE) and re-run.
- Set `fallback_level =` (blank) then inspect its loaded value (`None`).
