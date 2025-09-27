# Optional Values Example ([`optional_values.py`](https://github.com/HEROgold/confkit/blob/master/examples/optional_values.py))

## Purpose

Demonstrates nullable / optional configuration patterns:

- `optional=True` shorthand vs [`Optional(...)`](pdoc:confkit.Optional) wrapper
- Optional enums, strings, integers
- Empty string vs None semantics
- Cascading defaults & fallback logic

## Running

```bash
uv run python examples/optional_values.py
```

## Generated `config.ini` (Excerpt)

First run (only defaults materialize):

```ini
[OptionalConfig]
database_url = sqlite:///app.db
log_file = app.log
worker_count = 4
optional_string = default
optional_int = 42
optional_enum = dev
api_key = 
secret_key = 

[DatabaseConfig]
connection_string = sqlite:///fallback.db
username = 
password = 
port = 5432
```

After code mutates values or sets some to `None`, lines representing `None` are removed (or may remain absent if never set). When assigning new values, those lines reappear.

Example after updates:

```ini
[OptionalConfig]
database_url = 
log_file = 
worker_count = 
optional_string = new value
optional_int = 100
optional_enum = prod
api_key = 
secret_key = 

[DatabaseConfig]
connection_string = postgresql://localhost/mydb
username = admin
password = 
port = 5433
```

## Notes

- Setting a value to `None` for an optional field removes it from the config file.
- Empty string `""` is distinct from `None` (still persisted as a blank value).
- Use fallback logic in application code (see `get_connection_params`).

## Try Variations

- Remove the whole `[DatabaseConfig]` section and re-run.
- Set `worker_count = None` then reassign an integer.
