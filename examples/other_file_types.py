"""Examples of using Config with JSON, TOML, and YAML files.

This requires the 'msgspec' extra to be installed!!
The Parser facade automatically selects the appropriate adapter based on file extension.
"""
from confkit.data_types import List
from typing import TypeVar
from pathlib import Path
from confkit.config import Config


T = TypeVar("T")
class JsonConfig(Config[T]): ...
class TomlConfig(Config[T]): ...
class YamlConfig(Config[T]): ...

# Set up each config class with its file - parser is auto-detected
JsonConfig.set_file(Path("example.json"))
TomlConfig.set_file(Path("example.toml"))
YamlConfig.set_file(Path("example.yaml"))

# Define config values for each class
class JsonSettings:
    value = JsonConfig(123)

class TomlSettings:
    value = TomlConfig("hello")

class YamlSettings:
    value = YamlConfig(List([1, 2, 3]))


if __name__ == "__main__":
    print("JsonSettings.value:", JsonSettings.value)
    print("TomlSettings.value:", TomlSettings.value)
    print("YamlSettings.value:", YamlSettings.value)
