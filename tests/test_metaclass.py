from pathlib import Path

from confkit.config import Config as OG
from confkit.config import ConfigContainerMeta
from confkit.ext.parsers import IniParser


class Config(OG):
    """A Config class for testing purposes."""

Config.set_file(Path("meta_test.ini"))
Config._set_parser(IniParser())

def mock_meta_class() -> None:
    class Mock(ConfigContainerMeta):
        called_count = 0

    def set_mock(cls, key, value) -> None:  # noqa: ANN001
        Mock.called_count += 1
        ConfigContainerMeta.__setattr__(cls, key, value)

    Mock.__setattr__ = set_mock
    return Mock

def test_set_class_attribute() -> None:
    """Test that setting a class attribute works as expected."""
    meta = mock_meta_class()

    class Test(metaclass=meta):
        x = Config(10)

    assert isinstance(Test.__dict__["x"], Config)
    Test.x = 20
    assert isinstance(Test.__dict__["x"], Config)
    assert meta.called_count == 2 # one for Test.x = 20, one is called in __set__ on the descriptor

def test_meta_avoiding_non_Config() -> None: # noqa: N802
    """Test that MetaConfig does not interfere with non-Config attributes."""
    meta = mock_meta_class()

    class Test(metaclass=meta):
        x = 10

    assert isinstance(Test.__dict__["x"], int)
    Test.x = 20
    assert isinstance(Test.__dict__["x"], int)
    assert meta.called_count == 1 # should ony be called when Test.x = 20.
    # Meaning __set__ was never called from the Config descriptor
