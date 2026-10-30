# Delegate Example ([`delegate.py`](https://github.com/HEROgold/confkit/blob/master/examples/delegate.py))

## Purpose

Shows how one setting can read and write a setting in another config file, so that file holds the only copy of the value.

## Key Concepts

- `Delegate(Settings.dashboard_url)` passes reads and writes through to `Settings.dashboard_url`
- The delegate stores nothing, so its own file gets no key for it
- Type checkers see the delegate with the target's type

## Running

```bash
uv run python examples/delegate.py
```

## Code

The bot and the dashboard both read `app.ini`. Only the dashboard reads `dashboard.ini`. The dashboard's public address lives in `app.ini`, and `dashboard.ini` refers to it:

```python
from pathlib import Path
from typing import TypeVar

from confkit.config import Config
from confkit.ext.delegate import Delegate

T = TypeVar("T")
class AppConfig(Config[T]): ...
class DashboardConfig(Config[T]): ...

AppConfig.set_file(Path("app.ini"))
DashboardConfig.set_file(Path("dashboard.ini"))

class Settings:
    dashboard_url = AppConfig("http://localhost:8001")

class DashboardSettings:
    session_key = DashboardConfig("change-me")
    public_url = Delegate(Settings.dashboard_url)
```

## Generated Files

`app.ini` holds the value:

```ini
[Settings]
dashboard_url = http://localhost:8001
```

`dashboard.ini` has no `public_url` key:

```ini
[DashboardSettings]
session_key = change-me
```

## Notes

- Reading `DashboardSettings.public_url` reads the `dashboard_url` key in `app.ini`.
- `DashboardSettings().public_url = "https://dashboard.example.com"` writes the `dashboard_url` key in `app.ini`.
- A delegate can point at another delegate. Both read and write the same key.
- Pass a plain attribute read of a `Config` setting, like `Settings.dashboard_url` or `module.Settings.dashboard_url`. A literal or a computed value such as `Settings.dashboard_url + "/callback"` raises `TypeError`.
- `Delegate` finds the target by reading the caller's bytecode, so it runs on CPython only.
