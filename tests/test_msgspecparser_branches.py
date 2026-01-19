"""Tests for MsgspecParser.get fallback and string branch in write."""
import io

from confkit.ext.parsers import MsgspecParser


def test_get_fallback() -> None:
    p = MsgspecParser()
    assert p.get("missing_section", "missing_option", fallback="fallback_value") == "fallback_value"


def test_write_string_branch() -> None:
    class DummyParser:
        @staticmethod
        def encode(_) -> str:  # noqa: ANN001
            return "string output"
    p = MsgspecParser()
    p._parsers[".dummy"] = DummyParser
    p.data = {"foo": {"bar": "baz"}}
    buf = io.StringIO()
    buf.name = "file.dummy"
    p.write(buf)
    buf.seek(0)
    assert buf.read() == "string output"
