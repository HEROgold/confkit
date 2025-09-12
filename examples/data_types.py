"""
Examples demonstrating the various data types available in confkit.

This example shows:
1. Using primitive data types (int, float, bool, str)
2. Using specialized number formats (hex, octal, binary)
3. Custom base integers
4. Type validation and conversion

Run with: python data_types.py
"""

from configparser import ConfigParser
from pathlib import Path

from confkit import Config
from confkit.data_types import Binary, Boolean, Float, Hex, Integer, Octal, String

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class DataTypeConfig:
    """Configuration class demonstrating various data types."""
    
    # Simple primitive types (explicit for showcase)
    string_value = Config(String("default string"))
    int_value = Config(Integer(42))
    float_value = Config(Float(3.14159))
    bool_value = Config(Boolean(True))

    # Auto-detected types (more convenient but less explicit)
    auto_string = Config("auto-detected string")
    auto_int = Config(100)
    auto_float = Config(2.71828)
    auto_bool = Config(False)

    # Specialized number formats
    hex_value = Config(Hex(0xFF))  # Stored as 0xff in config.ini
    octal_value = Config(Octal(0o755))  # Stored as 0o755 in config.ini
    binary_value = Config(Binary(0b10101010))  # Stored as 0b10101010 in config.ini
    binary_from_bytes = Config(Binary(b"hello"))  # Converts bytes to int

    # Custom base integers
    base7_value = Config(Integer(42, base=7))  # Stored as 7c42 in config.ini
    base5_value = Config(Integer(13, base=5))  # Stored as 5c13 in config.ini



def main():
    # Print primitive types
    print("--- Primitive Types ---")
    print(f"String: {DataTypeConfig.string_value}")
    print(f"Integer: {DataTypeConfig.int_value}")
    print(f"Float: {DataTypeConfig.float_value}")
    print(f"Boolean: {DataTypeConfig.bool_value}")

    # Update values
    DataTypeConfig.string_value = "updated string"
    DataTypeConfig.int_value = 99
    DataTypeConfig.float_value = 2.71828
    DataTypeConfig.bool_value = not DataTypeConfig.bool_value
    
    print("\n--- Updated Primitive Types ---")
    print(f"String: {DataTypeConfig.string_value}")
    print(f"Integer: {DataTypeConfig.int_value}")
    print(f"Float: {DataTypeConfig.float_value}")
    print(f"Boolean: {DataTypeConfig.bool_value}")

    # Print specialized number formats
    print("\n--- Specialized Number Formats ---")
    print(f"Hex: {DataTypeConfig.hex_value} (0x{DataTypeConfig.hex_value:x})")
    print(f"Octal: {DataTypeConfig.octal_value} (0o{DataTypeConfig.octal_value:o})")
    print(f"Binary: {DataTypeConfig.binary_value} (0b{DataTypeConfig.binary_value:b})")
    
    # Update specialized formats
    DataTypeConfig.hex_value = 0xABCD
    DataTypeConfig.octal_value = 0o644
    DataTypeConfig.binary_value = 0b11001100
    
    print("\n--- Updated Specialized Formats ---")
    print(f"Hex: {DataTypeConfig.hex_value} (0x{DataTypeConfig.hex_value:x})")
    print(f"Octal: {DataTypeConfig.octal_value} (0o{DataTypeConfig.octal_value:o})")
    print(f"Binary: {DataTypeConfig.binary_value} (0b{DataTypeConfig.binary_value:b})")
    
    # Print custom base integers
    print("\n--- Custom Base Integers ---")
    print(f"Base 7: {DataTypeConfig.base7_value}")
    print(f"Base 5: {DataTypeConfig.base5_value}")
    
    # Print auto-detected types
    print("\n--- Auto-detected Types ---")
    print(f"Auto String: {DataTypeConfig.auto_string}")
    print(f"Auto Int: {DataTypeConfig.auto_int}")
    print(f"Auto Float: {DataTypeConfig.auto_float}")
    print(f"Auto Bool: {DataTypeConfig.auto_bool}")


if __name__ == "__main__":
    main()
