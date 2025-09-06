"""
Examples demonstrating advanced usage patterns and edge cases with confkit.

This example shows:
1. Class-level configuration inheritance
2. Working with complex nested configurations
3. Handling configuration errors gracefully
4. Runtime configuration changes
5. Performance considerations

Run with: python advanced_patterns.py
"""

from configparser import ConfigParser
from pathlib import Path
import time
from typing import Any, Optional

from confkit import Config
from confkit.data_types import Integer, List, String
from confkit.exceptions import InvalidConverterError, InvalidDefaultError

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


# Example 1: Class inheritance with configurations
class BaseConfig:
    """Base configuration with common settings."""
    app_name = Config("BaseApp")
    version = Config("1.0.0")
    debug = Config(False)


class DevelopmentConfig(BaseConfig):
    """Development environment specific configuration."""
    debug = Config(True)
    log_level = Config("DEBUG")
    auto_reload = Config(True)


class ProductionConfig(BaseConfig):
    """Production environment specific configuration."""
    log_level = Config("WARNING")
    workers = Config(4)
    auto_reload = Config(False)


# Example 2: Nested configurations with references
class DatabaseConfig:
    """Database specific configuration."""
    host = Config("localhost")
    port = Config(5432)
    name = Config("app_db")
    user = Config("admin")
    password = Config("", optional=True)
    
    def get_connection_string(self) -> str:
        """Build a connection string from components."""
        password_part = f":{self.password}" if self.password else ""
        return f"postgresql://{self.user}{password_part}@{self.host}:{self.port}/{self.name}"


class CacheConfig:
    """Cache specific configuration."""
    enabled = Config(True)
    ttl = Config(300)  # Time to live in seconds
    backend = Config("memory")  # memory, redis, etc.


class ApplicationConfig:
    """Main application configuration that references other configs."""
    name = Config("AdvancedApp")
    environment = Config("development")
    
    def __init__(self) -> None:
        """Initialize with appropriate environment config."""
        self.db = DatabaseConfig()
        self.cache = CacheConfig()
        
        # Select appropriate environment config
        if self.environment == "development":
            self.env_config = DevelopmentConfig()
        elif self.environment == "production":
            self.env_config = ProductionConfig()
        else:
            self.env_config = BaseConfig()
    
    def is_debug(self) -> bool:
        """Get debug setting from environment config."""
        return self.env_config.debug


# Example 3: Error handling and validation
class ErrorHandlingConfig:
    """Configuration demonstrating error handling."""
    
    valid_value = Config(42)
    
    # These will raise errors when the value is retrieved
    # We don't actually create these but we can show how to handle potential errors
    
    def get_with_error_handling(self, section: str, setting: str, default: Any = None) -> Any:
        """Safely get a configuration value with error handling."""
        try:
            # This would normally be a direct attribute access
            # But we simulate accessing potentially invalid configurations
            return self._get_config_value(section, setting)
        except InvalidConverterError:
            print(f"Warning: Invalid type for {section}.{setting}, using default")
            return default
        except Exception as e:
            print(f"Error reading {section}.{setting}: {type(e).__name__}: {str(e)}")
            return default
    
    def _get_config_value(self, section: str, setting: str) -> Any:
        """Simulate getting a config value that might fail."""
        # This is just for demonstration
        if section == "invalid" and setting == "converter":
            raise InvalidConverterError("Invalid converter")
        elif section == "invalid" and setting == "default":
            raise InvalidDefaultError("Invalid default value")
        elif section == "invalid" and setting == "type":
            raise TypeError("Type mismatch")
        elif section == "invalid" and setting == "value":
            raise ValueError("Invalid value")
        return self.valid_value


# Example 4: Performance considerations
class PerformanceConfig:
    """Configuration demonstrating performance patterns."""
    
    # A potentially expensive configuration with many items
    large_list = Config(List([f"item_{i}" for i in range(100)]))
    
    # A simple value
    update_interval = Config(60)
    
    def __init__(self) -> None:
        """Initialize with cached values."""
        self._cached_list: Optional[list[str]] = None
        self._last_update_time = 0
    
    def get_list_cached(self) -> list[str]:
        """Get the list with caching for performance."""
        current_time = time.time()
        if (self._cached_list is None or 
                current_time - self._last_update_time > self.update_interval):
            self._cached_list = self.large_list
            self._last_update_time = current_time
        return self._cached_list


def main():
    # Example 1: Class inheritance
    print("=== Class Inheritance ===")
    dev_config = DevelopmentConfig()
    prod_config = ProductionConfig()
    
    print(f"Development - App: {dev_config.app_name}, Debug: {dev_config.debug}")
    print(f"Production - App: {prod_config.app_name}, Debug: {prod_config.debug}")
    
    # Example 2: Nested configurations
    print("\n=== Nested Configurations ===")
    app_config = ApplicationConfig()
    
    print(f"App Name: {app_config.name}")
    print(f"Environment: {app_config.environment}")
    print(f"Debug Mode: {app_config.is_debug()}")
    print(f"Database Connection: {app_config.db.get_connection_string()}")
    print(f"Cache Enabled: {app_config.cache.enabled}, TTL: {app_config.cache.ttl}s")
    
    # Change environment and reload
    app_config.environment = "production"
    app_config.__init__()  # Re-initialize with new environment
    
    print(f"\nAfter changing to production:")
    print(f"Debug Mode: {app_config.is_debug()}")
    
    # Example 3: Error handling
    print("\n=== Error Handling ===")
    error_config = ErrorHandlingConfig()
    
    # Valid access
    print(f"Valid Value: {error_config.valid_value}")
    
    # Simulated error scenarios
    print(f"Invalid Converter: {error_config.get_with_error_handling('invalid', 'converter', 'default_value')}")
    print(f"Invalid Default: {error_config.get_with_error_handling('invalid', 'default', 'default_value')}")
    print(f"Type Error: {error_config.get_with_error_handling('invalid', 'type', 'default_value')}")
    print(f"Value Error: {error_config.get_with_error_handling('invalid', 'value', 'default_value')}")
    
    # Example 4: Performance considerations
    print("\n=== Performance Patterns ===")
    perf_config = PerformanceConfig()
    
    # Measure time for direct access
    start_time = time.time()
    direct_list = perf_config.large_list
    direct_time = time.time() - start_time
    
    # Measure time for cached access
    start_time = time.time()
    cached_list = perf_config.get_list_cached()
    first_cache_time = time.time() - start_time
    
    # Second cached access should be faster
    start_time = time.time()
    cached_list_again = perf_config.get_list_cached()
    second_cache_time = time.time() - start_time
    
    print(f"Direct access time: {direct_time:.6f}s")
    print(f"First cached access time: {first_cache_time:.6f}s")
    print(f"Second cached access time: {second_cache_time:.6f}s")
    print(f"Lists are identical: {direct_list == cached_list == cached_list_again}")


if __name__ == "__main__":
    main()
