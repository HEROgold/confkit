"""Tests for the Delegate extension."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from confkit.config import Config
from confkit.ext.delegate import Delegate


class AppConfig(Config[str]): ...


class DashboardConfig(Config[str]): ...


app_file = Path("delegate_app_test.ini")
dashboard_file = Path("delegate_dashboard_test.ini")
app_file.unlink(missing_ok=True)
dashboard_file.unlink(missing_ok=True)
AppConfig.set_file(app_file)
DashboardConfig.set_file(dashboard_file)


class Settings:
    dashboard_url = AppConfig("http://localhost:8001")


class DashboardSettings:
    secret = DashboardConfig("hunter2")
    public_url = Delegate(Settings.dashboard_url)


class Chained:
    url = Delegate(DashboardSettings.public_url)


class Explicit:
    url = Delegate[str](Settings.dashboard_url)


class Slotted:
    __slots__ = ()
    url = Delegate(Settings.dashboard_url)


module = SimpleNamespace(Settings=Settings)


class Dotted:
    url = Delegate(module.Settings.dashboard_url)


def test_delegate_reads_target_value() -> None:
    """The delegate returns the target's current value."""
    assert DashboardSettings.public_url == Settings.dashboard_url
    assert DashboardSettings().public_url == Settings.dashboard_url


def test_target_write_shows_through_delegate() -> None:
    """Writing the target changes what the delegate reads."""
    Settings().dashboard_url = "https://target.example.com"
    assert DashboardSettings.public_url == "https://target.example.com"


def test_delegate_write_goes_to_target() -> None:
    """Writing the delegate writes the target's file, not the delegate's."""
    DashboardSettings().public_url = "https://delegate.example.com"
    assert Settings.dashboard_url == "https://delegate.example.com"
    assert "https://delegate.example.com" in app_file.read_text()
    assert "public_url" not in dashboard_file.read_text()


def test_delegate_of_delegate_passes_through() -> None:
    """A delegate of a delegate reads and writes the original setting."""
    Chained().url = "https://chained.example.com"
    assert Settings.dashboard_url == "https://chained.example.com"
    assert DashboardSettings.public_url == "https://chained.example.com"


def test_delegate_in_function_scope() -> None:
    """The target can be named through a local variable."""
    owner = Settings

    class Local:
        url = Delegate(owner.dashboard_url)

    Settings().dashboard_url = "https://local.example.com"
    assert Local.url == "https://local.example.com"


def test_delegate_rejects_derived_value() -> None:
    """A value computed from a setting isn't a setting, so it raises."""
    with pytest.raises(TypeError, match="only argument"):
        Delegate(Settings.dashboard_url + "/callback")


def test_delegate_rejects_literal() -> None:
    """A literal isn't a setting, so it raises."""
    with pytest.raises(TypeError, match="only argument"):
        Delegate("http://not-a-setting")


def test_delegate_rejects_non_config_attribute() -> None:
    """An attribute that isn't a Config descriptor raises and names it."""

    class Plain:
        url = "http://plain"

    with pytest.raises(TypeError, match=r"Plain\.url is not a Config setting"):
        Delegate(Plain.url)


def test_delegate_with_explicit_type_parameter() -> None:
    """`Delegate[str](...)` finds the caller's frame past typing's generic alias."""
    Settings().dashboard_url = "https://explicit.example.com"
    assert Explicit.url == "https://explicit.example.com"


def test_delegate_rejects_keyword_argument() -> None:
    """The target is positional-only, so Python itself rejects the keyword form."""
    untyped: Any = Delegate  # The type checker rejects this call too; check Python's own error.
    with pytest.raises(TypeError, match="positional-only"):
        untyped(target=Settings.dashboard_url)


def test_delegate_in_class_nested_in_class_in_function() -> None:
    """A free variable is resolved through every enclosing class body."""
    owner = Settings

    class Outer:
        class Inner:
            url = Delegate(owner.dashboard_url)

    Settings().dashboard_url = "https://nested.example.com"
    assert Outer.Inner.url == "https://nested.example.com"


def test_delegate_write_leaves_delegating_instance_alone() -> None:
    """Writing through a delegate sets nothing on the delegating instance, so __slots__ classes work."""
    Slotted().url = "https://slotted.example.com"
    assert Settings.dashboard_url == "https://slotted.example.com"

    instance = DashboardSettings()
    instance.public_url = "https://instance.example.com"
    assert vars(instance) == {}


def test_delegate_through_attribute_chain() -> None:
    """`module.Settings.dashboard_url` follows every attribute in the chain."""
    Dotted().url = "https://dotted.example.com"
    assert Settings.dashboard_url == "https://dotted.example.com"
    assert Dotted.url == "https://dotted.example.com"


def test_delegate_read_runs_target_file_change_hook(monkeypatch: pytest.MonkeyPatch) -> None:
    """A read through the delegate runs the target's file-change check, the same as a direct read."""
    descriptor = vars(Settings)["dashboard_url"]
    events: list[str] = []
    monkeypatch.setattr(AppConfig._watcher, "has_changed", lambda: True)
    monkeypatch.setattr(descriptor, "on_file_change", lambda origin, _old, _new: events.append(origin))

    assert DashboardSettings.public_url == Settings.dashboard_url
    assert events == ["get", "get"]
