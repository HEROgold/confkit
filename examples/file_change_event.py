
"""
Basic example showing how to use the on_file_change() hook to detect changes in the configuration file.
Copy of basic.py
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


def on_api_change(self, origin: str, old: str, new: str):
    if origin == "get":
        print(f"[on_file_change] API key changed from '{old}' to '{new}'. Reconnecting to API...")
    elif origin == "set":
        print(f"[on_file_change] API key accessed. Current value: '{new}' (previous: '{old}')")

def print_change(origin, old, new):
    print(f"Configuration file has changed! {origin=} {old=} {new=}")

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

    debug.on_file_change = print_change
    api_key.on_file_change = on_api_change



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
