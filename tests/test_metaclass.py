from configparser import ConfigParser
from pathlib import Path
from confkit.config import Config as OG, ConfigContainerMeta

class Config(OG):
    """A Config class for testing purposes."""

Config.set_file(Path("meta_test.ini"))
Config.set_parser(ConfigParser())

def mock_metaClass():
    class mock(ConfigContainerMeta):
        called_count = 0

    def set_mock(cls, key, value):
        mock.called_count += 1
        ConfigContainerMeta.__setattr__(cls, key, value)

    mock.__setattr__ = set_mock
    return mock

def test_set_class_attribute():
    """Test that setting a class attribute works as expected."""
    meta = mock_metaClass()

    class Test(metaclass=meta):
        x = Config(10)

    assert isinstance(Test.__dict__["x"], Config)
    Test.x = 20
    assert isinstance(Test.__dict__["x"], Config)
    assert meta.called_count == 2 # one for Test.x = 20, one is called in __set__ on the descriptor

def test_meta_avoiding_non_Config():
    """Test that MetaConfig does not interfere with non-Config attributes."""
    meta = mock_metaClass()

    class Test(metaclass=meta):
        x = 10

    assert isinstance(Test.__dict__["x"], int)
    Test.x = 20
    assert isinstance(Test.__dict__["x"], int)
    assert meta.called_count == 1 # should ony be called when Test.x = 20.
    # Meaning __set__ was never called from the Config descriptor
