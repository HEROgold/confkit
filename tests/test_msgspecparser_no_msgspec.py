"""Test MsgspecParser behavior when msgspec is not installed."""
import re
import sys

import pytest


@pytest.mark.order("last")
def test_msgspecparser_import_error(monkeypatch: pytest.MonkeyPatch) -> None:
    expected_msg = (
        "confkit.ext.parsers requires the optional 'msgspec' extra. "
        "Install it via 'pip install "
        "confkit[msgspec]' or 'uv add confkit[msgspec]'."
        "This is required for json, toml and yaml parsing."
    )
    # Simulate msgspec not installed
    monkeypatch.setitem(sys.modules, "msgspec", None)
    monkeypatch.setitem(sys.modules, "msgspec.json", None)
    monkeypatch.setitem(sys.modules, "msgspec.toml", None)
    monkeypatch.setitem(sys.modules, "msgspec.yaml", None)
    sys.modules.pop("confkit.ext.parsers", None)
    with pytest.raises(ImportError, match=re.escape(expected_msg)):
        import confkit.ext.parsers  # noqa: F401, PLC0415

