"""
Comprehensive example demonstrating all new data types: URL, DateTime, and TimeDelta.

This example shows:
1. Using all three new data types in a single configuration
2. Real-world use case (web application configuration)
3. Interaction between different data types

Run with: python examples/new_data_types_example.py
"""

import datetime
from configparser import ConfigParser
from pathlib import Path

from confkit import Config, URL, DateTime, TimeDelta

# Set up the parser and file
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("webapp_config.ini"))

# Enable automatic writing when config values are changed
Config.write_on_edit = True


class WebAppConfig:
    """Web application configuration using all new data types."""
    
    # URLs
    base_url = Config(URL("https://myapp.com"))
    api_endpoint = Config(URL("https://api.myapp.com/v1"))
    database_url = Config(URL("postgresql://localhost:5432/myapp"))
    redis_url = Config(URL("redis://localhost:6379/0"))
    
    # DateTime values
    deployment_time = Config(DateTime(datetime.datetime(2023, 1, 1, 0, 0, 0)))
    last_backup = Config(DateTime())  # Current time as default
    maintenance_window_start = Config(DateTime(datetime.datetime(2023, 1, 1, 2, 0, 0)))
    maintenance_window_end = Config(DateTime(datetime.datetime(2023, 1, 1, 4, 0, 0)))
    
    # TimeDelta values (timeouts and intervals)
    request_timeout = Config(TimeDelta(datetime.timedelta(seconds=30)))
    connection_timeout = Config(TimeDelta(datetime.timedelta(seconds=10)))
    session_timeout = Config(TimeDelta(datetime.timedelta(minutes=30)))
    cache_ttl = Config(TimeDelta(datetime.timedelta(hours=1)))
    backup_interval = Config(TimeDelta(datetime.timedelta(hours=6)))
    health_check_interval = Config(TimeDelta(datetime.timedelta(minutes=5)))


def main():
    """Demonstrate comprehensive usage of all new data types."""
    print("New Data Types Comprehensive Example")
    print("=" * 45)
    
    # Display initial configuration
    print("Initial Configuration:")
    print("URLs:")
    print(f"  Base URL: {WebAppConfig.base_url}")
    print(f"  API Endpoint: {WebAppConfig.api_endpoint}")
    print(f"  Database URL: {WebAppConfig.database_url}")
    print(f"  Redis URL: {WebAppConfig.redis_url}")
    
    print("\nDateTime Values:")
    print(f"  Deployment Time: {WebAppConfig.deployment_time}")
    print(f"  Last Backup: {WebAppConfig.last_backup}")
    print(f"  Maintenance Start: {WebAppConfig.maintenance_window_start}")
    print(f"  Maintenance End: {WebAppConfig.maintenance_window_end}")
    
    print("\nTimeout & Interval Values:")
    print(f"  Request Timeout: {WebAppConfig.request_timeout}")
    print(f"  Connection Timeout: {WebAppConfig.connection_timeout}")
    print(f"  Session Timeout: {WebAppConfig.session_timeout}")
    print(f"  Cache TTL: {WebAppConfig.cache_ttl}")
    print(f"  Backup Interval: {WebAppConfig.backup_interval}")
    print(f"  Health Check Interval: {WebAppConfig.health_check_interval}")
    
    # Simulate configuration updates
    print("\n" + "="*45)
    print("Updating Configuration...")
    
    # Update URLs for production deployment
    WebAppConfig.base_url = "https://production.myapp.com"
    WebAppConfig.api_endpoint = "https://api.production.myapp.com/v2"
    WebAppConfig.database_url = "postgresql://prod-db:5432/myapp_prod"
    WebAppConfig.redis_url = "redis://prod-cache:6379/1"
    
    # Update deployment time to now
    WebAppConfig.deployment_time = datetime.datetime.now()
    
    # Set maintenance window for this weekend
    next_saturday_2am = datetime.datetime.now().replace(
        hour=2, minute=0, second=0, microsecond=0
    ) + datetime.timedelta(days=(5-datetime.datetime.now().weekday()) % 7)
    WebAppConfig.maintenance_window_start = next_saturday_2am
    WebAppConfig.maintenance_window_end = next_saturday_2am + datetime.timedelta(hours=2)
    
    # Update timeouts for production (more conservative)
    WebAppConfig.request_timeout = datetime.timedelta(seconds=60)
    WebAppConfig.connection_timeout = datetime.timedelta(seconds=15)
    WebAppConfig.session_timeout = datetime.timedelta(hours=2)
    WebAppConfig.cache_ttl = datetime.timedelta(hours=4)
    WebAppConfig.backup_interval = datetime.timedelta(hours=12)
    WebAppConfig.health_check_interval = datetime.timedelta(minutes=1)
    
    print("Updated Configuration:")
    print("URLs:")
    print(f"  Base URL: {WebAppConfig.base_url}")
    print(f"  API Endpoint: {WebAppConfig.api_endpoint}")
    print(f"  Database URL: {WebAppConfig.database_url}")
    print(f"  Redis URL: {WebAppConfig.redis_url}")
    
    print("\nDateTime Values:")
    print(f"  Deployment Time: {WebAppConfig.deployment_time}")
    print(f"  Last Backup: {WebAppConfig.last_backup}")
    print(f"  Maintenance Start: {WebAppConfig.maintenance_window_start}")
    print(f"  Maintenance End: {WebAppConfig.maintenance_window_end}")
    
    print("\nTimeout & Interval Values:")
    print(f"  Request Timeout: {WebAppConfig.request_timeout}")
    print(f"  Connection Timeout: {WebAppConfig.connection_timeout}")
    print(f"  Session Timeout: {WebAppConfig.session_timeout}")
    print(f"  Cache TTL: {WebAppConfig.cache_ttl}")
    print(f"  Backup Interval: {WebAppConfig.backup_interval}")
    print(f"  Health Check Interval: {WebAppConfig.health_check_interval}")
    
    # Demonstrate parsing various string formats
    print("\n" + "="*45)
    print("String Parsing Demonstrations:")
    
    # URL parsing
    print("\nURL Parsing:")
    url_type = URL()
    test_urls = [
        "https://api.example.com/users",
        "postgres://user:pass@localhost:5432/db",
        "redis://localhost:6379/0"
    ]
    for url in test_urls:
        print(f"  '{url}' -> {url_type.convert(url)}")
    
    # DateTime parsing
    print("\nDateTime Parsing:")
    dt_type = DateTime()
    test_datetimes = [
        "2024-06-15T14:30:00",
        "2024-06-15 14:30:00",
        "2024-06-15"
    ]
    for dt_str in test_datetimes:
        print(f"  '{dt_str}' -> {dt_type.convert(dt_str)}")
    
    # TimeDelta parsing
    print("\nTimeDelta Parsing:")
    td_type = TimeDelta()
    test_durations = [
        "30",          # 30 seconds
        "PT1H30M",     # ISO: 1 hour 30 minutes
        "2:30:00",     # 2 hours 30 minutes
        "5m 30s"       # 5 minutes 30 seconds
    ]
    for td_str in test_durations:
        print(f"  '{td_str}' -> {td_type.convert(td_str)}")
    
    # Show calculated maintenance duration
    maintenance_duration = WebAppConfig.maintenance_window_end - WebAppConfig.maintenance_window_start
    print(f"\nCalculated maintenance window duration: {maintenance_duration}")
    
    # Show when next backup is due
    next_backup = WebAppConfig.last_backup + WebAppConfig.backup_interval
    print(f"Next backup due at: {next_backup}")


if __name__ == "__main__":
    main()