"""Test Config.detect_parser behavior for different file extensions."""
from configparser import ConfigParser
from pathlib import Path

import pytest

from confkit.config import Config
from confkit.ext.parsers import MsgspecParser
from confkit.sentinels import UNSET


class DummyConfig(Config):
    pass

def test_detect_parser_ini() -> None:
    DummyConfig._file = Path("test.ini")
    DummyConfig._parser = None
    DummyConfig._detect_parser()
    assert isinstance(DummyConfig._parser, ConfigParser)

def test_detect_parser_msgspec() -> None:
    DummyConfig._file = Path("test.yaml")
    DummyConfig._parser = None
    DummyConfig._detect_parser()
    assert isinstance(DummyConfig._parser, MsgspecParser)

def test_detect_parser_unsupported() -> None:
    DummyConfig._file = Path("test.unsupported")
    DummyConfig._parser = None
    with pytest.raises(ValueError, match="Unsupported config file extension"):
        DummyConfig._detect_parser()

def test_detect_parser_no_file_unset() -> None:
    DummyConfig._file = UNSET
    DummyConfig._parser = None
    with pytest.raises(ValueError, match="Config file is not set"):
        DummyConfig._detect_parser()
