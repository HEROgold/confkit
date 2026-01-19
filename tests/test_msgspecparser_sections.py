"""Tests for MsgspecParser section/option methods."""
from confkit.ext.parsers import MsgspecParser


def test_set_and_get_section_and_option() -> None:
    p = MsgspecParser()
    assert not p.has_section("foo")
    p.set_section("foo")
    assert p.has_section("foo")
    assert not p.has_option("foo", "bar")
    p.set("foo", "bar", "baz")
    assert p.has_option("foo", "bar")
    assert p.get("foo", "bar") == "baz"
    assert p.get("foo", "notfound", fallback="default") == "default"
    p.add_section("newsec")
    assert p.has_section("newsec")
    p.set("foo", "bar", "qux")
    assert p.get("foo", "bar") == "qux"


def test_set_option_creates_section() -> None:
    p = MsgspecParser()
    p.set("newsection", "opt", "val")
    assert p.has_section("newsection")
    assert p.has_option("newsection", "opt")
    assert p.get("newsection", "opt") == "val"
