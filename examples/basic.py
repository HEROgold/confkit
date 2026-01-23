
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


if __name__ == "__main__":
    app_config = AppConfig()
    # Read values from config
    print(f"Debug mode: {app_config.debug}")
    print(f"Server port: {app_config.port}")
    print(f"Host: {app_config.host}")
    print(f"Timeout: {app_config.timeout}s")
    
    # Modify a configuration value
    # This automatically saves to config.ini when write_on_edit is True
    app_config.port = 9000
    print(f"Updated port: {app_config.port}")
    
    # Get the optional value
    print(f"API Key: {'Not set' if not app_config.api_key else app_config.api_key}")

    # Set the API key
    app_config.api_key = "my-secret-key"
    print(f"Updated API Key: {app_config.api_key}")
