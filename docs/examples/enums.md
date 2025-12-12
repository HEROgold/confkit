# Enums Example ([`enums.py`](https://github.com/HEROgold/confkit/blob/master/examples/enums.py))

## Purpose

Demonstrates enum support:

- [`StrEnum`](pdoc:confkit.StrEnum), [`IntEnum`](pdoc:confkit.IntEnum), [`IntFlag`](pdoc:confkit.IntFlag), usage via dedicated data types
- Optional enum values
- Bitwise flag composition (`Permission`)
- **Self-documenting config files** with inline comments showing all allowed enum values

## Running

```bash
uv run python examples/enums.py
```

## Generated `config.ini` (Excerpt)

```ini
[ServerConfig]
log_level = info  # allowed: debug, info, warning, error
default_priority = 5  # allowed: LOW(0), MEDIUM(5), HIGH(10)
default_permission = 1  # allowed: READ(1), WRITE(2), EXECUTE(4)
fallback_level = error  # allowed: debug, info, warning, error
environment = INFO  # allowed: DEBUG, INFO, WARNING, ERROR
```

Notice how each enum value now includes an inline comment listing all possible values. This makes configuration files self-documenting for end-users who may not be familiar with the codebase.

If values are changed in code (or by assignment at runtime) they persist accordingly, and the allowed values comment is automatically maintained.

## Notes

- **Allowed values are automatically displayed**: Enum values include inline comments showing all valid options
- **Format varies by enum type**:
  - `StrEnum`: Shows member values (e.g., `debug, info, warning, error`)
  - `IntEnum`/`IntFlag`: Shows member names with values (e.g., `LOW(0), MEDIUM(5), HIGH(10)`)
  - `Enum`: Shows member names (e.g., `DEBUG, INFO, WARNING, ERROR`)
- `IntFlag` values are stored as their integer bitfield representation
- Optional enum fields removed (set to `None`) disappear from the file
- Comments are automatically stripped when reading values, so they don't interfere with parsing

## Try Variations

- Manually set `default_permission = 7` (READ|WRITE|EXECUTE) and re-run - the allowed values comment will be preserved.
- Set `fallback_level =` (blank) then inspect its loaded value (`None`).
