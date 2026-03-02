"""
This examples shows how to use references to link configuration files.
"""
from confkit.ext.reference import Reference
from pathlib import Path
from configparser import ConfigParser
from confkit import Config

class OtherConfig(Config):
    pass

# Set up the parser and file
Config.set_file(Path(__file__).parent / "ref.ini")
OtherConfig.set_file(Path(__file__).parent / "other_ref.ini")

class AppConfig:
    ref = OtherConfig(Reference(Config))
    other_ref = Config(Reference(OtherConfig))
    some_value_1 = Config("value1")
    some_value_2 = OtherConfig("value2")
    some_value_3 = Config("value3")

if __name__ == "__main__":
    cfg = AppConfig()
    print(cfg.ref)
    cfg.ref = Config
    print(cfg.ref)
    print(cfg.other_ref)
    cfg.other_ref = OtherConfig
    print(cfg.other_ref)
