
"""
Basic example showing how to use the on_file_change() hook to detect changes in the configuration file.
Copy of basic.py
"""
from random import randint

from configparser import ConfigParser
from pathlib import Path

from confkit import Config

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

# Enable automatic writing when config values are changed (this is the default)
Config.write_on_edit = True


def on_api_change(origin: str, old: str, new: str):
    if origin == "get":
        print(f"[on_file_change] API key accessed. Current value: '{new}' (previous: '{old}')")
    elif origin == "set":
        print(f"[on_file_change] API key changed from '{old}' to '{new}'. Reconnecting to API...")

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


if __name__ == "__main__":
    cfg = AppConfig()
    # Read values from config
    print(f"Debug mode: {cfg.debug}")
    print(f"Server port: {cfg.port}")
    print(f"Host: {cfg.host}")
    print(f"Timeout: {cfg.timeout}s")
    
    # Modify a configuration value
    # This automatically saves to config.ini when write_on_edit is True
    cfg.debug = not cfg.debug
    # Set the API key
    cfg.api_key = randint(100000, 999999)
