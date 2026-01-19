"""Test MsgspecParser behavior when msgspec is not installed."""
import sys

import pytest


@pytest.mark.order("last")
def test_msgspecparser_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    # Simulate msgspec not installed
    monkeypatch.setitem(sys.modules, "msgspec", None)
    monkeypatch.setitem(sys.modules, "msgspec.json", None)
    monkeypatch.setitem(sys.modules, "msgspec.toml", None)
    monkeypatch.setitem(sys.modules, "msgspec.yaml", None)
    sys.modules.pop("confkit.ext.parsers", None)
    with pytest.raises(ImportError):
        import confkit.ext.parsers  # noqa: F401, PLC0415

