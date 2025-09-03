"""
Examples demonstrating optional values and advanced configuration patterns.

This example shows:
1. Working with optional values that can be None
2. Using Optional wrapper with different data types
3. Handling validation and type safety with optional values
4. Creating cascading configurations with fallbacks

Run with: python optional_values.py
"""

from configparser import ConfigParser
from enum import StrEnum
from pathlib import Path

from confkit import Config
from confkit.data_types import Integer, Optional, String, StrEnum as ConfigStrEnum

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class Environment(StrEnum):
    """Enum for environment selection."""
    DEVELOPMENT = "dev"
    TESTING = "test"
    STAGING = "staging"
    PRODUCTION = "prod"


class OptionalConfig:
    """Configuration with optional values."""
    
    # Optional values using the optional parameter
    database_url = Config("sqlite:///app.db", optional=True)
    log_file = Config("app.log", optional=True)
    worker_count = Config(4, optional=True)
    
    # Optional values using the Optional wrapper
    optional_string = Config(Optional(String("default")))
    optional_int = Config(Optional(Integer(42)))
    optional_enum = Config(Optional(ConfigStrEnum(Environment.DEVELOPMENT)))
    
    # This is equivalent to setting optional=True
    api_key = Config("", optional=True)
    
    # Empty optional value - will be None if not set
    secret_key = Config(Optional(String("")))


class DatabaseConfig:
    """Example of cascading configurations with fallbacks."""
    
    # Main connection string with a fallback
    connection_string = Config(Optional(String("sqlite:///fallback.db")))
    
    # Username with no default (will be None if not set)
    username = Config(Optional(String("")))
    
    # Password with no default (will be None if not set)
    password = Config(Optional(String("")))
    
    # Port with default
    port = Config(Optional(Integer(5432)))
    
    def get_connection_params(self):
        """Example of providing fallbacks for optional values."""
        # For username, use a default if None
        username = self.username or "default_user"
        
        # For password, check if it exists
        if self.password:
            password_info = "Password set"
        else:
            password_info = "No password"
            
        # For port, provide a fallback
        port = self.port or 5432
        
        return {
            "connection": self.connection_string,
            "username": username,
            "password_info": password_info,
            "port": port,
        }


def main():
    # Test basic optional configurations
    config = OptionalConfig()
    
    print("--- Optional Values ---")
    print(f"Database URL: {config.database_url}")
    print(f"Log File: {config.log_file}")
    print(f"Worker Count: {config.worker_count}")
    
    # Set to None
    config.database_url = None
    config.log_file = None
    config.worker_count = None
    
    print("\n--- After Setting to None ---")
    print(f"Database URL: {config.database_url}")
    print(f"Log File: {config.log_file}")
    print(f"Worker Count: {config.worker_count}")
    
    # Test the Optional wrapper
    print("\n--- Optional Wrapper ---")
    print(f"Optional String: {config.optional_string}")
    print(f"Optional Int: {config.optional_int}")
    print(f"Optional Enum: {config.optional_enum}")
    
    # Set values again
    config.optional_string = "new value"
    config.optional_int = 100
    config.optional_enum = Environment.PRODUCTION
    
    print("\n--- After Setting New Values ---")
    print(f"Optional String: {config.optional_string}")
    print(f"Optional Int: {config.optional_int}")
    print(f"Optional Enum: {config.optional_enum}")
    
    # Test empty optional values
    print("\n--- Empty Optional Values ---")
    print(f"API Key: {config.api_key}")
    print(f"Secret Key: {config.secret_key}")
    
    # Test DatabaseConfig with fallbacks
    db_config = DatabaseConfig()
    print("\n--- Database Configuration with Fallbacks ---")
    params = db_config.get_connection_params()
    for key, value in params.items():
        print(f"{key}: {value}")
    
    # Set some values and test again
    db_config.connection_string = "postgresql://localhost/mydb"
    db_config.username = "admin"
    db_config.port = 5433
    
    print("\n--- Updated Database Configuration ---")
    params = db_config.get_connection_params()
    for key, value in params.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
