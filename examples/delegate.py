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
    """Read by both the bot and the dashboard."""

    dashboard_url = AppConfig("http://localhost:8001")

class DashboardSettings:
    """Read by the dashboard only."""

    session_key = DashboardConfig("change-me")
    public_url = Delegate(Settings.dashboard_url)

if __name__ == "__main__":
    print("Dashboard URL:", Settings.dashboard_url)
    print("Public URL:", DashboardSettings.public_url)

    DashboardSettings().public_url = "https://dashboard.example.com"
    print("Dashboard URL after writing the delegate:", Settings.dashboard_url)
    assert Settings.dashboard_url == DashboardSettings.public_url
    assert "public_url" not in Path("dashboard.ini").read_text()
