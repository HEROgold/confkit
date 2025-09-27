# New Data Types - URL, DateTime, and TimeDelta

This document describes the three new data types added to confkit: `URL`, `DateTime`, and `TimeDelta`.

## URL Data Type

The `URL` data type provides validation and normalization for URL configuration values.

### Usage

```python
from confkit import Config, URL
from pathlib import Path
from configparser import ConfigParser

# Configure confkit
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

class APIConfig:
    base_url = Config(URL("https://api.example.com"))
    database_url = Config(URL("postgresql://localhost:5432/db"))
    redis_url = Config(URL("redis://localhost:6379/0"))

# Usage
config = APIConfig()
print(config.base_url)  # https://api.example.com

# Update with validation
config.base_url = "https://newapi.example.com"  # Works
# config.base_url = "invalid-url"  # Raises ValueError
```

### Features

- **Validation**: Ensures URLs have both scheme and netloc (e.g., `https://example.com`)
- **Normalization**: URLs are normalized during conversion
- **Error Handling**: Clear error messages for invalid URLs
- **Scheme Support**: Supports all standard URL schemes (http, https, ftp, postgresql, etc.)

### Supported URL Formats

```python
# All of these are valid:
"https://example.com"
"http://localhost:8080"
"ftp://files.example.com/path"
"postgresql://user:pass@localhost:5432/database"
"redis://localhost:6379/0"
"mongodb://user:pass@host:27017/db"
```

## DateTime Data Type

The `DateTime` data type provides ISO 8601 datetime parsing and serialization.

### Usage

```python
from confkit import Config, DateTime
from datetime import datetime

class ScheduleConfig:
    created_at = Config(DateTime(datetime(2024, 1, 1, 12, 0, 0)))
    backup_time = Config(DateTime(datetime.now()))
    maintenance_window = Config(DateTime(datetime(2024, 12, 25, 2, 0, 0)))

# Usage
config = ScheduleConfig()
print(config.created_at)  # 2024-01-01 12:00:00

# Update with datetime object
config.backup_time = datetime(2024, 6, 15, 14, 30, 0)
```

### Features

- **ISO 8601 Support**: Parses ISO 8601 format strings (`YYYY-MM-DDTHH:MM:SS`)
- **Timezone Support**: Handles both naive and timezone-aware datetime objects
- **Robust Parsing**: Uses `datetime.fromisoformat()` for reliable parsing
- **Clean Serialization**: Stores as ISO 8601 format in config files

### Supported DateTime Formats

```python
# All of these ISO 8601 formats are supported:
"2024-01-01T12:00:00"              # Basic format
"2024-01-01T12:00:00.123456"       # With microseconds
"2024-01-01T12:00:00+00:00"        # With timezone
"2024-01-01T12:00:00Z"             # UTC timezone
"2024-12-31T23:59:59.999999"       # Max precision
```

### Config File Example

```ini
[ScheduleConfig]
created_at = 2024-01-01T12:00:00
backup_time = 2024-06-15T14:30:00
maintenance_window = 2024-12-25T02:00:00
```

## TimeDelta Data Type

The `TimeDelta` data type provides flexible duration parsing with support for multiple formats.

### Usage

```python
from confkit import Config, TimeDelta
from datetime import timedelta

class TimeoutConfig:
    request_timeout = Config(TimeDelta(timedelta(seconds=30)))
    cache_ttl = Config(TimeDelta(timedelta(hours=24)))
    retry_interval = Config(TimeDelta(timedelta(minutes=5)))
    session_lifetime = Config(TimeDelta(timedelta(days=7)))

# Usage
config = TimeoutConfig()
print(config.request_timeout)  # 0:00:30

# Update with timedelta object
config.request_timeout = timedelta(minutes=2, seconds=30)
```

### Features

- **ISO 8601 Durations**: Full support for ISO 8601 duration format (`P[n]DT[n]H[n]M[n]S`)
- **Flexible Parsing**: Supports human-readable formats like "1h 30m", "90 minutes"
- **Time Formats**: Supports `HH:MM:SS` and `MM:SS` time formats
- **Number Support**: Plain numbers are interpreted as seconds
- **Clean Serialization**: Stores as ISO 8601 duration format

### Supported Duration Formats

```python
# ISO 8601 duration formats:
"PT30S"              # 30 seconds
"PT5M"               # 5 minutes  
"PT1H"               # 1 hour
"P1D"                # 1 day
"P1DT2H30M45S"       # 1 day, 2 hours, 30 minutes, 45 seconds

# Human-readable formats:
"30s"                # 30 seconds
"5m"                 # 5 minutes
"1h"                 # 1 hour
"1h 30m"             # 1 hour 30 minutes
"2 hours 15 minutes" # 2 hours 15 minutes
"1.5h"               # 1.5 hours

# Time formats:
"1:30:00"            # 1 hour 30 minutes (HH:MM:SS)
"5:30"               # 5 minutes 30 seconds (MM:SS)

# Plain numbers:
"90"                 # 90 seconds
"1.5"                # 1.5 seconds
```

### Config File Example

```ini
[TimeoutConfig]
request_timeout = PT2M30S
cache_ttl = P1D
retry_interval = PT5M
session_lifetime = P7D
```

## Integration with Existing Features

All new data types integrate seamlessly with confkit's existing features:

### Optional Values

```python
from confkit import Config, Optional, URL, DateTime, TimeDelta
from datetime import datetime, timedelta

class OptionalConfig:
    api_url = Config(URL("https://api.example.com"), optional=True)
    backup_time = Config(Optional(DateTime(datetime.now())))
    timeout = Config(Optional(TimeDelta(timedelta(seconds=30))))
```

### Type Safety

```python
# These will maintain proper type hints in your IDE:
config = APIConfig()
url: str = config.base_url           # Type-safe URL access
dt: datetime = config.created_at     # Type-safe datetime access  
td: timedelta = config.timeout       # Type-safe timedelta access
```

### Error Handling

All new data types provide clear error messages:

```python
# URL validation error
try:
    config.api_url = "invalid-url"
except ValueError as e:
    print(e)  # "Invalid URL: invalid-url. URL must have scheme and netloc."

# DateTime parsing error  
try:
    config.created_at = datetime.fromisoformat("invalid-date")
except ValueError as e:
    print(e)  # "Invalid datetime format: invalid-date. Expected ISO 8601 format"

# TimeDelta parsing error
try:
    td_type.convert("invalid-duration")
except ValueError as e:
    print(e)  # "Invalid duration format: invalid-duration"
```

## Best Practices

1. **Use URL for any configuration that represents a connection string or endpoint**
2. **Use DateTime for timestamps, scheduled times, and date-based configuration**
3. **Use TimeDelta for timeouts, intervals, durations, and time-based limits**
4. **Prefer ISO formats in config files for portability and clarity**
5. **Use Optional wrapper when the configuration value might not be set**

## Migration from String-based Configurations

If you're currently using string-based configuration for URLs, dates, or durations, migration is straightforward:

```python
# Before:
class OldConfig:
    api_url = Config("https://api.example.com")         # String
    backup_time = Config("2024-01-01T12:00:00")         # String
    timeout = Config("30s")                             # String

# After:
class NewConfig:
    api_url = Config(URL("https://api.example.com"))                    # Validated URL
    backup_time = Config(DateTime(datetime(2024, 1, 1, 12, 0, 0)))     # Proper datetime
    timeout = Config(TimeDelta(timedelta(seconds=30)))                  # Proper timedelta
```

The new types provide better type safety, validation, and IDE support while maintaining the same config file format compatibility where possible.