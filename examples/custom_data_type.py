"""Custom data type example for confkit.

Demonstrates how to:
1. Subclass BaseDataType[T]
2. Implement convert()
3. (Optionally) override __str__ for serialization
4. Use with Config descriptor

Run with:
    uv run python examples/custom_data_type.py

This example creates a `UpperString` type that always stores values upper-cased
in the config file, while presenting them upper-cased when read.
"""
from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

from confkit import Config
from confkit.data_types import BaseDataType

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

class UpperString(BaseDataType[str]):
    """Custom string data type that normalizes to UPPER CASE.

    Stored *exactly* as upper case in the INI file. Accepts any input that can
    be coerced to str.
    """

    def __str__(self) -> str:
        # Called when storing data in the INI;
        return self.value.upper()

    def convert(self, value: str) -> str:
        """Convert input to upper case string."""
        # Called when reading from INI
        return value.upper()

    def validate(self) -> bool:
        # enforce that value is upper case
        # Important! Must call super() first to ensure type conversion
        # You may raise an error to provide more information
        # Simply returning False will raise a generic error
        super().validate()
        if self.value.upper() != self.value:
            raise ValueError("Value must be upper case")
        return True

class CustomConfig:
    # Use the custom datatype by instantiating it with a default.
    shout_name = Config(UpperString("confkit"))
    project = Config(UpperString("Example Project"))


def main() -> None:
    print("Initial values:")
    print("shout_name:", CustomConfig.shout_name)
    print("project:", CustomConfig.project)

    # Assign lower / mixed case; storage normalizes to upper automatically
    CustomConfig.shout_name = "custom"
    CustomConfig.project = "demo Title"

    print("\nAfter reassignment:")
    print("shout_name:", CustomConfig.shout_name)
    print("project:", CustomConfig.project)

    # Show underlying INI content (optional diagnostic)
    ini_text = Path("config.ini").read_text(encoding="utf-8")
    print("\nRaw config.ini contents:\n" + ini_text)

if __name__ == "__main__":  # pragma: no cover
    main()
