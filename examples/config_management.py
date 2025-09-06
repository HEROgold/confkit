"""
Examples demonstrating advanced configuration management with confkit.

This example shows:
1. Managing configuration files and parsers
2. Global settings like write_on_edit and validate_types
3. Handling multiple configuration files
4. Configuration validation and error handling

Run with: python config_management.py
"""

import tempfile
from configparser import ConfigParser
from pathlib import Path

from confkit import Config
from confkit.data_types import Integer, String

# Example 1: Basic Configuration Setup
def basic_setup():
    """Demonstrate basic configuration setup."""
    print("\n=== Basic Configuration Setup ===")
    
    # Create a temporary file for this example
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp:
        config_file = Path(temp.name)
    
    # Set up the parser and file
    parser = ConfigParser()
    Config.set_parser(parser)
    Config.set_file(config_file)
    
    # Create a configuration class
    class BasicConfig:
        app_name = Config("MyApp")
        version = Config("1.0.0")
    
    # Use the configuration
    config = BasicConfig()
    print(f"App Name: {config.app_name}")
    print(f"Version: {config.version}")
    
    # Clean up
    config_file.unlink()


# Example 2: Configuration Writing Control
def writing_control():
    """Demonstrate control over when configuration is written to file."""
    print("\n=== Configuration Writing Control ===")
    
    # Create a temporary file for this example
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp:
        config_file = Path(temp.name)
    
    # Set up the parser and file
    parser = ConfigParser()
    Config.set_parser(parser)
    Config.set_file(config_file)
    
    # Create a configuration class
    class WritingConfig:
        setting1 = Config("default1")
        setting2 = Config("default2")
    
    # First with automatic writing (default)
    Config.write_on_edit = True
    config = WritingConfig()
    
    print("With write_on_edit = True:")
    config.setting1 = "changed1"
    print(f"Changed setting1 to: {config.setting1}")
    print(f"File size after change: {config_file.stat().st_size} bytes")
    
    # Then with manual writing
    Config.write_on_edit = False
    print("\nWith write_on_edit = False:")
    config.setting2 = "changed2"
    print(f"Changed setting2 to: {config.setting2}")
    print(f"File size before manual write: {config_file.stat().st_size} bytes")
    
    # Manually write the changes
    Config.write()
    print(f"File size after manual write: {config_file.stat().st_size} bytes")
    
    # Reset to default
    Config.write_on_edit = True
    
    # Clean up
    config_file.unlink()


# Example 3: Type Validation Control
def validation_control():
    """Demonstrate control over type validation."""
    print("\n=== Type Validation Control ===")
    
    # Create a temporary file for this example
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp:
        config_file = Path(temp.name)
    
    # Set up the parser and file
    parser = ConfigParser()
    Config.set_parser(parser)
    Config.set_file(config_file)
    
    # Create a configuration class with explicit types
    class TypedConfig:
        string_value = Config(String("text"))
        int_value = Config(Integer(42))
    
    # First with validation enabled (default)
    Config.validate_types = True
    config = TypedConfig()
    
    print("With validate_types = True:")
    try:
        # This would raise an error with validation enabled
        # We have to directly manipulate the config file to create an invalid state
        parser.set("TypedConfig", "int_value", "not_an_int")
        print(f"Changed int_value in config to 'not_an_int'")
        
        try:
            invalid_value = config.int_value
            print(f"Read int_value: {invalid_value}")
        except Exception as e:
            print(f"Error reading int_value: {type(e).__name__}: {str(e)}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
    
    # Fix the value
    parser.set("TypedConfig", "int_value", "42")
    
    # Then with validation disabled
    Config.validate_types = False
    print("\nWith validate_types = False:")
    
    # This will work but might not have the expected type
    parser.set("TypedConfig", "int_value", "not_an_int")
    try:
        invalid_value = config.int_value
        print(f"Read int_value: {invalid_value} (type: {type(invalid_value).__name__})")
    except Exception as e:
        print(f"Error reading int_value: {type(e).__name__}: {str(e)}")
    
    # Reset to default
    Config.validate_types = True
    
    # Clean up
    config_file.unlink()


# Example 4: Multiple Configuration Files
def multiple_configs():
    """Demonstrate working with multiple configuration files."""
    print("\n=== Multiple Configuration Files ===")
    
    # Create temporary files for this example
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp1:
        config_file1 = Path(temp1.name)
    
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp2:
        config_file2 = Path(temp2.name)
    
    # Create parsers
    parser1 = ConfigParser()
    parser2 = ConfigParser()
    
    # First configuration setup
    Config.set_parser(parser1)
    Config.set_file(config_file1)
    
    class FirstConfig:
        name = Config("FirstApp")
        value = Config(100)
    
    first = FirstConfig()
    print(f"First config - Name: {first.name}, Value: {first.value}")
    
    # Second configuration setup
    Config.set_parser(parser2)
    Config.set_file(config_file2)
    
    class SecondConfig:
        name = Config("SecondApp")
        value = Config(200)
    
    second = SecondConfig()
    print(f"Second config - Name: {second.name}, Value: {second.value}")
    
    # Switching back to first config
    Config.set_parser(parser1)
    Config.set_file(config_file1)
    
    # Update first config
    first.value = 150
    print(f"Updated first config - Value: {first.value}")
    
    # Switch to second config again
    Config.set_parser(parser2)
    Config.set_file(config_file2)
    
    # Verify second config is unchanged
    print(f"Second config - Value: {second.value}")
    
    # Clean up
    config_file1.unlink()
    config_file2.unlink()


def main():
    # Run all examples
    basic_setup()
    writing_control()
    validation_control()
    multiple_configs()
    
    print("\nAll examples completed!")


if __name__ == "__main__":
    main()
