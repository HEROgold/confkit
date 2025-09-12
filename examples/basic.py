
"""
Basic example showing the fundamental usage of confkit.

This example demonstrates how to:
1. Set up the configuration parser and file
2. Define a configuration class with various data types
3. Access and modify configuration values

Run with: python basic.py
"""

from configparser import ConfigParser
from pathlib import Path

from confkit import Config

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

# Enable automatic writing when config values are changed (this is the default)
Config.write_on_edit = True


class AppConfig:
    """Basic application configuration with various data types."""
    
    # Boolean configuration value
    debug = Config(False)
    
    # Integer configuration value
    port = Config(8080)
    
    # String configuration value
    host = Config("localhost")
    
    # Float configuration value
    timeout = Config(30.5)
    
    # Optional string (can be empty)
    api_key = Config("", optional=True)


def main():
    # Read values from config
    print(f"Debug mode: {AppConfig.debug}")
    print(f"Server port: {AppConfig.port}")
    print(f"Host: {AppConfig.host}")
    print(f"Timeout: {AppConfig.timeout}s")
    
    # Modify a configuration value
    # This automatically saves to config.ini when write_on_edit is True
    AppConfig.port = 9000
    print(f"Updated port: {AppConfig.port}")
    
    # Get the optional value
    print(f"API Key: {'Not set' if not AppConfig.api_key else AppConfig.api_key}")

    # Set the API key
    AppConfig.api_key = "my-secret-key"
    print(f"Updated API Key: {AppConfig.api_key}")


if __name__ == "__main__":
    main()
