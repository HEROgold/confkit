"""
Example demonstrating the TimeDelta data type in confkit.

This example shows:
1. Using TimeDelta data type with flexible parsing
2. Setting and getting timedelta values
3. Multiple input formats (ISO 8601, colon-separated, flexible text)

Run with: python examples/timedelta_example.py
"""

import datetime
from configparser import ConfigParser
from pathlib import Path

from confkit import Config, TimeDelta

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("timedelta_config.ini"))

# Enable automatic writing when config values are changed
Config.write_on_edit = True


class ServiceConfig:
    """Service configuration with timeout and duration values."""
    
    # Request timeout
    request_timeout = Config(TimeDelta(datetime.timedelta(seconds=30)))
    
    # Connection timeout
    connection_timeout = Config(TimeDelta(datetime.timedelta(seconds=10)))
    
    # Cache expiration time
    cache_expiry = Config(TimeDelta(datetime.timedelta(hours=1)))
    
    # Retry delay
    retry_delay = Config(TimeDelta(datetime.timedelta(seconds=5)))
    
    # Session lifetime
    session_lifetime = Config(TimeDelta(datetime.timedelta(days=7)))


def main():
    """Demonstrate TimeDelta data type usage."""
    print("TimeDelta Data Type Example")
    print("=" * 35)
    
    # Read initial values
    print("Initial configuration:")
    print(f"Request Timeout: {ServiceConfig.request_timeout}")
    print(f"Connection Timeout: {ServiceConfig.connection_timeout}")
    print(f"Cache Expiry: {ServiceConfig.cache_expiry}")
    print(f"Retry Delay: {ServiceConfig.retry_delay}")
    print(f"Session Lifetime: {ServiceConfig.session_lifetime}")
    
    # Update configuration values
    print("\nUpdating configuration...")
    ServiceConfig.request_timeout = datetime.timedelta(seconds=60)
    ServiceConfig.connection_timeout = datetime.timedelta(seconds=15)
    ServiceConfig.cache_expiry = datetime.timedelta(hours=2, minutes=30)
    ServiceConfig.retry_delay = datetime.timedelta(seconds=2)
    
    print("Updated configuration:")
    print(f"Request Timeout: {ServiceConfig.request_timeout}")
    print(f"Connection Timeout: {ServiceConfig.connection_timeout}")
    print(f"Cache Expiry: {ServiceConfig.cache_expiry}")
    print(f"Retry Delay: {ServiceConfig.retry_delay}")
    
    # Demonstrate timedelta parsing
    print("\nTimeDelta Parsing Examples:")
    td_type = TimeDelta()
    
    # Numeric seconds
    print("Numeric seconds:")
    numeric_examples = ["30", "60.5", "3600", "86400"]
    for example in numeric_examples:
        try:
            parsed = td_type.convert(example)
            print(f"  ✓ '{example}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{example}': {e}")
    
    # ISO 8601 duration format
    print("\nISO 8601 duration format:")
    iso_examples = [
        "PT30S",           # 30 seconds
        "PT5M",            # 5 minutes
        "PT1H",            # 1 hour
        "P1D",             # 1 day
        "PT1H30M45S",      # 1 hour, 30 minutes, 45 seconds
        "P1DT2H30M",       # 1 day, 2 hours, 30 minutes
    ]
    for example in iso_examples:
        try:
            parsed = td_type.convert(example)
            print(f"  ✓ '{example}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{example}': {e}")
    
    # Colon-separated format
    print("\nColon-separated time format:")
    colon_examples = [
        "5:30",          # 5 minutes, 30 seconds
        "1:30:45",       # 1 hour, 30 minutes, 45 seconds
        "0:30",          # 30 seconds
    ]
    for example in colon_examples:
        try:
            parsed = td_type.convert(example)
            print(f"  ✓ '{example}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{example}': {e}")
    
    # Flexible text format
    print("\nFlexible text format:")
    text_examples = [
        "30s",             # 30 seconds
        "5m",              # 5 minutes
        "2h",              # 2 hours
        "1d",              # 1 day
        "1h 30m",          # 1 hour 30 minutes
        "2 days",          # 2 days
        "3 hours 45 minutes",  # 3 hours 45 minutes
        "1d 2h 30m 45s",   # Complex duration
    ]
    for example in text_examples:
        try:
            parsed = td_type.convert(example)
            print(f"  ✓ '{example}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{example}': {e}")
    
    # Invalid formats
    print("\nInvalid formats:")
    invalid_examples = [
        "not-a-duration",
        "invalid-format",
        "1 invalid",
    ]
    for example in invalid_examples:
        try:
            parsed = td_type.convert(example)
            print(f"  ✓ '{example}' -> {parsed}")
        except ValueError as e:
            print(f"  ✗ '{example}': {e}")
    
    # Demonstrate timedelta serialization
    print("\nTimeDelta Serialization:")
    test_timedeltas = [
        datetime.timedelta(seconds=0),
        datetime.timedelta(seconds=30),
        datetime.timedelta(minutes=5),
        datetime.timedelta(hours=2, minutes=30),
        datetime.timedelta(days=1, hours=2, minutes=30, seconds=45),
    ]
    
    for td in test_timedeltas:
        td_type_with_value = TimeDelta(td)
        print(f"  {td} -> '{td_type_with_value}'")


if __name__ == "__main__":
    main()