"""
Example demonstrating the DateTime data type in confkit.

This example shows:
1. Using DateTime data type with ISO 8601 parsing
2. Setting and getting datetime values  
3. Timezone handling and format support

Run with: python examples/datetime_example.py
"""

import datetime
from configparser import ConfigParser
from pathlib import Path

from confkit import Config, DateTime

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("datetime_config.ini"))

# Enable automatic writing when config values are changed
Config.write_on_edit = True


class ScheduleConfig:
    """Application configuration with datetime values."""
    
    # Application start time
    app_start_time = Config(DateTime(datetime.datetime(2023, 1, 1, 9, 0, 0)))
    
    # Last backup time
    last_backup = Config(DateTime())  # Defaults to current time
    
    # Maintenance window start
    maintenance_start = Config(DateTime(datetime.datetime(2023, 1, 1, 2, 0, 0)))
    
    # Created timestamp
    created_at = Config(DateTime(datetime.datetime.now()))


def main():
    """Demonstrate DateTime data type usage."""
    print("DateTime Data Type Example")
    print("=" * 35)
    
    # Read initial values
    print("Initial configuration:")
    print(f"App Start Time: {ScheduleConfig.app_start_time}")
    print(f"Last Backup: {ScheduleConfig.last_backup}")
    print(f"Maintenance Start: {ScheduleConfig.maintenance_start}")
    print(f"Created At: {ScheduleConfig.created_at}")
    
    # Update configuration values
    print("\nUpdating configuration...")
    ScheduleConfig.app_start_time = datetime.datetime(2024, 6, 15, 10, 30, 0)
    ScheduleConfig.last_backup = datetime.datetime(2024, 6, 14, 23, 45, 30)
    ScheduleConfig.maintenance_start = datetime.datetime(2024, 6, 16, 3, 0, 0)
    
    print("Updated configuration:")
    print(f"App Start Time: {ScheduleConfig.app_start_time}")
    print(f"Last Backup: {ScheduleConfig.last_backup}")
    print(f"Maintenance Start: {ScheduleConfig.maintenance_start}")
    
    # Demonstrate datetime parsing
    print("\nDateTime Parsing Examples:")
    dt_type = DateTime()
    
    datetime_strings = [
        "2024-12-25T10:30:00",          # ISO format
        "2024-12-25T10:30:00.123456",   # ISO with microseconds
        "2024-12-25T10:30:00+00:00",    # ISO with timezone
        "2024-12-25T10:30:00Z",         # ISO with Z timezone
        "2024-12-25 10:30:00",          # Common format
        "2024-12-25 10:30:00.123456",   # Common format with microseconds
        "2024-12-25",                   # Date only
    ]
    
    print("Valid datetime strings:")
    for dt_str in datetime_strings:
        try:
            parsed = dt_type.convert(dt_str)
            print(f"  ✓ '{dt_str}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{dt_str}': {e}")
    
    invalid_datetime_strings = [
        "not-a-datetime",
        "2024-13-01",        # Invalid month
        "2024-01-32",        # Invalid day
        "25-12-2024",        # Wrong format
        "2024/12/25",        # Wrong separators
    ]
    
    print("\nInvalid datetime strings:")
    for dt_str in invalid_datetime_strings:
        try:
            parsed = dt_type.convert(dt_str)
            print(f"  ✓ '{dt_str}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{dt_str}': {e}")
    
    # Demonstrate datetime serialization
    print("\nDateTime Serialization:")
    test_datetime = datetime.datetime(2024, 6, 15, 14, 30, 45, 123456)
    dt_type_with_value = DateTime(test_datetime)
    print(f"Original: {test_datetime}")
    print(f"Serialized: {dt_type_with_value}")


if __name__ == "__main__":
    main()