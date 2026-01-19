"""Tests for MsgspecParser.read edge cases."""
from pathlib import Path

import msgspec
import pytest

from confkit.ext.parsers import MsgspecParser


def test_read_file_does_not_exist(tmp_path: Path) -> None:
    file = tmp_path / "notfound.json"
    p = MsgspecParser()
    p.read(file)
    assert p.data == {}


def test_read_unsupported_extension(tmp_path: Path) -> None:
    file = tmp_path / "test.unsupported"
    file.write_text("irrelevant")
    p = MsgspecParser()
    with pytest.raises(ValueError, match="Unsupported file extension for reading"):
        p.read(file)


def test_read_decode_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    file = tmp_path / "test.json"
    file.write_text("not valid json")
    p = MsgspecParser()
    # Patch parser.decode to raise DecodeError
    monkeypatch.setattr(msgspec.json, "decode", lambda _: (_ for _ in ()).throw(msgspec.DecodeError("fail")))
    p.read(file)
    assert p.data == {}


def test_read_success(tmp_path: Path) -> None:
    file = tmp_path / "test.json"
    data = {"section": {"option": "value"}}
    file.write_text(msgspec.json.encode(data).decode("utf-8"))
    p = MsgspecParser()
    p.read(file)
    assert p.data == data
