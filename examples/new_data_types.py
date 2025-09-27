"""
Example demonstrating the new data types: URL, DateTime, and TimeDelta.

This example shows:
1. Using URL data type for configuration values
2. Using DateTime data type with ISO 8601 format
3. Using TimeDelta data type with flexible duration formats
4. Integration with Config descriptors

Run with: python new_data_types.py
"""

from configparser import ConfigParser
from datetime import datetime, timedelta
from pathlib import Path

from confkit import Config
from confkit.data_types import URL, DateTime, TimeDelta

# Initialize confkit
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("new_types_config.ini"))


class AppConfig:
    """Configuration class demonstrating new data types."""
    
    # URL configurations
    api_url = Config(URL("https://api.example.com/v1"))
    database_url = Config(URL("postgresql://localhost:5432/mydb"))
    redis_url = Config(URL("redis://localhost:6379/0"))
    
    # DateTime configurations
    created_at = Config(DateTime(datetime(2024, 1, 1, 12, 0, 0)))
    last_backup = Config(DateTime(datetime.now()))
    maintenance_window = Config(DateTime(datetime(2024, 1, 1, 2, 0, 0)))
    
    # TimeDelta configurations
    request_timeout = Config(TimeDelta(timedelta(seconds=30)))
    cache_ttl = Config(TimeDelta(timedelta(hours=24)))
    retry_interval = Config(TimeDelta(timedelta(minutes=5)))
    session_lifetime = Config(TimeDelta(timedelta(days=7)))


def demonstrate_url_type():
    """Demonstrate URL data type functionality."""
    print("=== URL Data Type Demo ===")
    
    print(f"API URL: {AppConfig.api_url}")
    print(f"Database URL: {AppConfig.database_url}")
    print(f"Redis URL: {AppConfig.redis_url}")
    
    # Update a URL
    print("\nUpdating API URL...")
    AppConfig.api_url = "https://newapi.example.com/v2"
    print(f"New API URL: {AppConfig.api_url}")
    
    # Demonstrate validation
    print("\nTesting URL validation...")
    try:
        AppConfig.api_url = "invalid-url"
    except ValueError as e:
        print(f"Validation caught invalid URL: {e}")
    
    print()


def demonstrate_datetime_type():
    """Demonstrate DateTime data type functionality."""
    print("=== DateTime Data Type Demo ===")
    
    print(f"Created at: {AppConfig.created_at}")
    print(f"Last backup: {AppConfig.last_backup}")
    print(f"Maintenance window: {AppConfig.maintenance_window}")
    
    # Update a datetime
    print("\nUpdating maintenance window...")
    AppConfig.maintenance_window = datetime(2024, 12, 25, 1, 0, 0)
    print(f"New maintenance window: {AppConfig.maintenance_window}")
    
    # Show ISO format in config file
    print(f"ISO format: {AppConfig.maintenance_window.isoformat()}")
    
    print()


def demonstrate_timedelta_type():
    """Demonstrate TimeDelta data type functionality."""
    print("=== TimeDelta Data Type Demo ===")
    
    print(f"Request timeout: {AppConfig.request_timeout}")
    print(f"Cache TTL: {AppConfig.cache_ttl}")
    print(f"Retry interval: {AppConfig.retry_interval}")
    print(f"Session lifetime: {AppConfig.session_lifetime}")
    
    # Update timeouts with different formats
    print("\nUpdating timeouts...")
    AppConfig.request_timeout = timedelta(minutes=2)
    print(f"New request timeout: {AppConfig.request_timeout}")
    
    AppConfig.retry_interval = timedelta(seconds=30)
    print(f"New retry interval: {AppConfig.retry_interval}")
    
    # Show ISO 8601 duration format
    td_type = TimeDelta(timedelta(hours=1, minutes=30, seconds=45))
    print(f"ISO 8601 format example: {td_type}")
    
    print()


def demonstrate_config_persistence():
    """Demonstrate how values are persisted in the config file."""
    print("=== Config File Persistence Demo ===")
    
    # Set some values
    AppConfig.api_url = "https://production.api.com"
    AppConfig.created_at = datetime(2024, 6, 15, 14, 30, 0)
    AppConfig.request_timeout = timedelta(minutes=2, seconds=30)
    
    # Read and display the config file
    config_file = Path("new_types_config.ini")
    if config_file.exists():
        print("Current config file contents:")
        print(config_file.read_text())
    else:
        print("Config file not found")
    
    print()


def demonstrate_flexible_parsing():
    """Demonstrate flexible parsing capabilities of TimeDelta."""
    print("=== Flexible TimeDelta Parsing Demo ===")
    
    # Create a TimeDelta type for testing
    td_type = TimeDelta(timedelta(seconds=30))
    
    # Test various input formats
    test_formats = [
        # ISO 8601 formats
        "PT30S",           # 30 seconds
        "PT5M",            # 5 minutes  
        "PT1H",            # 1 hour
        "P1D",             # 1 day
        "P1DT2H30M45S",    # 1 day, 2 hours, 30 minutes, 45 seconds
        
        # Flexible formats
        "30s",             # 30 seconds
        "5m",              # 5 minutes
        "1h",              # 1 hour
        "1h 30m",          # 1 hour 30 minutes
        "2 hours 15 minutes", # 2 hours 15 minutes
        "1:30:00",         # HH:MM:SS format
        "90",              # 90 seconds (number only)
        "1.5h",            # 1.5 hours
    ]
    
    print("Testing various TimeDelta input formats:")
    for format_str in test_formats:
        try:
            result = td_type.convert(format_str)
            iso_repr = TimeDelta(result).__str__()
            print(f"  '{format_str}' -> {result} ({iso_repr})")
        except ValueError as e:
            print(f"  '{format_str}' -> ERROR: {e}")
    
    print()


def main():
    """Main demonstration function."""
    print("New Data Types Example - URL, DateTime, and TimeDelta")
    print("=" * 60)
    print()
    
    demonstrate_url_type()
    demonstrate_datetime_type()
    demonstrate_timedelta_type()
    demonstrate_config_persistence()
    demonstrate_flexible_parsing()
    
    print("Demo completed successfully!")
    print("\nCheck 'new_types_config.ini' to see how values are stored.")


if __name__ == "__main__":
    main()