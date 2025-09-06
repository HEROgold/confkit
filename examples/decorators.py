
"""
Examples demonstrating decorators provided by confkit.

This example shows:
1. Using the with_setting decorator to inject config values into function parameters
2. Using the as_kwarg decorator to customize parameter injection
3. Using set and default decorators to set configuration values

Run with: python decorators.py
"""

from configparser import ConfigParser
from pathlib import Path
from typing import Any

from confkit.config import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class ServiceConfig:
    """Service configuration class demonstrating decorator usage."""
    
    # Define configuration values that we'll use with decorators
    retry_count = Config(3)
    timeout = Config(30)
    max_connections = Config(100)
    cache_time = Config(60)

    # with_setting decorator injects the current value of retry_count into kwargs
    @Config.with_setting(retry_count)
    def process(self, data: Any, **kwargs: Any) -> str:
        """Process data with retries based on configuration."""
        retries = kwargs.get("retry_count")
        return f"Processing data with {retries} retries"

    # as_kwarg renames the parameter from "timeout" to "request_timeout"
    # and sets a default value of 60 if the config value isn't set
    @Config.as_kwarg("ServiceConfig", "timeout", "request_timeout", 60)
    def request(self, url: str, **kwargs: Any) -> str:
        """Make a request with a configured timeout."""
        timeout = kwargs.get("request_timeout")
        return f"Requesting {url} with timeout: {timeout}s"
    
    # Example of using the set decorator to set a config value
    @Config.set("ServiceConfig", "max_connections", 150)
    def increase_connections(self) -> str:
        """Increase the maximum number of connections and save to config."""
        return f"Increased max connections to {self.max_connections}"
    
    # Example of using the default decorator to set a default value
    # This only sets the value if it's not already set
    @Config.default("ServiceConfig", "cache_time", 120)
    def set_default_cache_time(self) -> str:
        """Set a default cache time if not already configured."""
        return f"Default cache time is {self.cache_time}"


def main():
    service = ServiceConfig()
    
    # Test with_setting decorator
    print(service.process("sample data"))
    
    # Change the configuration value
    service.retry_count = 5
    print(service.process("more data"))  # Now uses the updated value
    
    # Test as_kwarg decorator
    print(service.request("https://example.com"))
    
    # Test set decorator
    print(service.increase_connections())
    
    # Test default decorator
    print(service.set_default_cache_time())
    
    # Change value and test again
    service.cache_time = 180
    print(service.set_default_cache_time())  # Value should not change


if __name__ == "__main__":
    main()
