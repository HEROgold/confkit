"""Test Config.detect_parser behavior for different file extensions."""
from configparser import ConfigParser
from pathlib import Path

import pytest

from confkit.config import Config as OG
from confkit.ext.parsers import MsgspecParser
from confkit.sentinels import UNSET


class Config(OG):
    """Subclass of Config to set test-specific parameters."""

def test_detect_parser_ini() -> None:
    Config._file = Path("test.ini")
    Config._parser = None
    Config._detect_parser()
    assert isinstance(Config._parser, ConfigParser)

def test_detect_parser_msgspec() -> None:
    Config._file = Path("test.yaml")
    Config._parser = None
    Config._detect_parser()
    assert isinstance(Config._parser, MsgspecParser)

def test_detect_parser_unsupported() -> None:
    Config._file = Path("test.unsupported")
    Config._parser = None
    with pytest.raises(ValueError, match="Unsupported config file extension"):
        Config._detect_parser()

def test_detect_parser_no_file_unset() -> None:
    Config._file = UNSET
    Config._parser = None
    with pytest.raises(ValueError, match="Config file is not set"):
        Config._detect_parser()
