"""Test suite for new data types: URL, DateTime, and TimeDelta."""

import datetime
from configparser import ConfigParser
from pathlib import Path
from urllib.parse import urlparse

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.config import Config
from confkit.data_types import DateTime, TimeDelta, URL


# Set up test configuration
config_file = Path("test_new_types.ini")
config_file.unlink(missing_ok=True)
config_file.touch()

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(config_file)
Config.write_on_edit = True


class TestURLDataType:
    """Test cases for the URL data type."""
    
    def test_valid_url_creation(self):
        """Test creating URL with valid URLs."""
        url_type = URL("https://example.com")
        assert url_type.default == "https://example.com"
        assert url_type.value == "https://example.com"
    
    def test_empty_url(self):
        """Test empty URL is allowed."""
        url_type = URL("")
        assert url_type.convert("") == ""
    
    def test_valid_url_conversion(self):
        """Test converting valid URL strings."""
        url_type = URL()
        
        valid_urls = [
            "https://example.com",
            "http://subdomain.example.com:8080/path?query=value",
            "ftp://ftp.example.com/file.txt",
            "file:///path/to/file",
            "mailto:user@example.com",
            "tel:+1234567890"
        ]
        
        for url in valid_urls:
            result = url_type.convert(url)
            assert result == url
    
    def test_invalid_url_conversion(self):
        """Test that invalid URLs raise ValueError."""
        url_type = URL()
        
        invalid_urls = [
            "not-a-url",
            "://missing-scheme",
            "invalid://scheme",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                url_type.convert(url)
    
    def test_url_without_scheme(self):
        """Test that URLs without scheme raise ValueError."""
        url_type = URL()
        
        with pytest.raises(ValueError, match="URL must have a scheme"):
            url_type.convert("example.com")
    
    @given(st.text())
    def test_url_hypothesis_fuzz(self, text):
        """Fuzz test URL conversion with random strings."""
        url_type = URL()
        
        # Most random strings should either convert successfully or raise ValueError
        try:
            result = url_type.convert(text)
            # If it doesn't raise, it should return the same string
            assert isinstance(result, str)
        except ValueError:
            # This is expected for invalid URLs
            pass


class TestDateTimeDataType:
    """Test cases for the DateTime data type."""
    
    def test_default_datetime_creation(self):
        """Test creating DateTime with default current time."""
        dt_type = DateTime()
        assert isinstance(dt_type.default, datetime.datetime)
        assert isinstance(dt_type.value, datetime.datetime)
    
    def test_explicit_datetime_creation(self):
        """Test creating DateTime with explicit datetime."""
        test_dt = datetime.datetime(2023, 12, 25, 10, 30, 0)
        dt_type = DateTime(test_dt)
        assert dt_type.default == test_dt
        assert dt_type.value == test_dt
    
    def test_iso_format_conversion(self):
        """Test converting ISO format datetime strings."""
        dt_type = DateTime()
        
        iso_strings = [
            "2023-12-25T10:30:00",
            "2023-12-25T10:30:00.123456",
            "2023-12-25T10:30:00+00:00",
            "2023-12-25T10:30:00Z",
        ]
        
        for iso_string in iso_strings:
            result = dt_type.convert(iso_string)
            assert isinstance(result, datetime.datetime)
    
    def test_common_format_conversion(self):
        """Test converting common datetime format strings."""
        dt_type = DateTime()
        
        format_tests = [
            ("2023-12-25 10:30:00", datetime.datetime(2023, 12, 25, 10, 30, 0)),
            ("2023-12-25", datetime.datetime(2023, 12, 25, 0, 0, 0)),
        ]
        
        for dt_string, expected in format_tests:
            result = dt_type.convert(dt_string)
            assert result == expected
    
    def test_empty_datetime_returns_default(self):
        """Test that empty string returns default datetime."""
        test_dt = datetime.datetime(2023, 1, 1)
        dt_type = DateTime(test_dt)
        
        result = dt_type.convert("")
        assert result == test_dt
    
    def test_invalid_datetime_conversion(self):
        """Test that invalid datetime strings raise ValueError."""
        dt_type = DateTime()
        
        invalid_strings = [
            "not-a-datetime",
            "2023-13-01",  # Invalid month
            "2023-01-32",  # Invalid day
        ]
        
        for dt_string in invalid_strings:
            with pytest.raises(ValueError):
                dt_type.convert(dt_string)
    
    def test_datetime_str_representation(self):
        """Test string representation of datetime."""
        test_dt = datetime.datetime(2023, 12, 25, 10, 30, 0)
        dt_type = DateTime(test_dt)
        
        assert str(dt_type) == "2023-12-25T10:30:00"


class TestTimeDeltaDataType:
    """Test cases for the TimeDelta data type."""
    
    def test_default_timedelta_creation(self):
        """Test creating TimeDelta with default zero duration."""
        td_type = TimeDelta()
        assert td_type.default == datetime.timedelta()
        assert td_type.value == datetime.timedelta()
    
    def test_explicit_timedelta_creation(self):
        """Test creating TimeDelta with explicit timedelta."""
        test_td = datetime.timedelta(hours=2, minutes=30)
        td_type = TimeDelta(test_td)
        assert td_type.default == test_td
        assert td_type.value == test_td
    
    def test_numeric_seconds_conversion(self):
        """Test converting numeric seconds to timedelta."""
        td_type = TimeDelta()
        
        # Test integer seconds
        result = td_type.convert("3600")
        assert result == datetime.timedelta(seconds=3600)
        
        # Test float seconds
        result = td_type.convert("3600.5")
        assert result == datetime.timedelta(seconds=3600.5)
    
    def test_iso8601_duration_conversion(self):
        """Test converting ISO 8601 duration format."""
        td_type = TimeDelta()
        
        iso_tests = [
            ("P1D", datetime.timedelta(days=1)),
            ("PT1H", datetime.timedelta(hours=1)),
            ("PT30M", datetime.timedelta(minutes=30)),
            ("PT45S", datetime.timedelta(seconds=45)),
            ("P1DT2H30M45S", datetime.timedelta(days=1, hours=2, minutes=30, seconds=45)),
        ]
        
        for iso_string, expected in iso_tests:
            result = td_type.convert(iso_string)
            assert result == expected
    
    def test_colon_format_conversion(self):
        """Test converting colon-separated time format."""
        td_type = TimeDelta()
        
        colon_tests = [
            ("30:45", datetime.timedelta(minutes=30, seconds=45)),
            ("1:30:45", datetime.timedelta(hours=1, minutes=30, seconds=45)),
        ]
        
        for colon_string, expected in colon_tests:
            result = td_type.convert(colon_string)
            assert result == expected
    
    def test_flexible_format_conversion(self):
        """Test converting flexible duration formats."""
        td_type = TimeDelta()
        
        flexible_tests = [
            ("2d", datetime.timedelta(days=2)),
            ("3h", datetime.timedelta(hours=3)),
            ("45m", datetime.timedelta(minutes=45)),
            ("30s", datetime.timedelta(seconds=30)),
            ("1h 30m", datetime.timedelta(hours=1, minutes=30)),
            ("2 days 3 hours", datetime.timedelta(days=2, hours=3)),
        ]
        
        for flexible_string, expected in flexible_tests:
            result = td_type.convert(flexible_string)
            assert result == expected
    
    def test_empty_timedelta_returns_default(self):
        """Test that empty string returns default timedelta."""
        test_td = datetime.timedelta(minutes=15)
        td_type = TimeDelta(test_td)
        
        result = td_type.convert("")
        assert result == test_td
    
    def test_invalid_timedelta_conversion(self):
        """Test that invalid timedelta strings raise ValueError."""
        td_type = TimeDelta()
        
        invalid_strings = [
            "not-a-duration",
            "invalid-format",
        ]
        
        for td_string in invalid_strings:
            with pytest.raises(ValueError):
                td_type.convert(td_string)
    
    def test_timedelta_str_representation(self):
        """Test string representation of timedelta."""
        # Test zero duration
        td_type = TimeDelta()
        assert str(td_type) == "0s"
        
        # Test complex duration
        test_td = datetime.timedelta(days=2, hours=3, minutes=30, seconds=45)
        td_type = TimeDelta(test_td)
        assert str(td_type) == "2d 3h 30m 45s"


# Integration test with Config descriptors
class TestConfigIntegration:
    """Test integration of new data types with Config descriptors."""
    
    class TestConfig:
        """Test configuration class using new data types."""
        
        website_url = Config(URL("https://example.com"))
        created_at = Config(DateTime(datetime.datetime(2023, 1, 1, 12, 0, 0)))
        timeout = Config(TimeDelta(datetime.timedelta(seconds=30)))
    
    def test_url_config_integration(self):
        """Test URL data type integration with Config."""
        # Test getting value
        assert self.TestConfig.website_url == "https://example.com"
        
        # Test setting value
        self.TestConfig.website_url = "https://new-site.com"
        assert self.TestConfig.website_url == "https://new-site.com"
    
    def test_datetime_config_integration(self):
        """Test DateTime data type integration with Config."""
        # Test getting value
        assert isinstance(self.TestConfig.created_at, datetime.datetime)
        
        # Test setting value
        new_dt = datetime.datetime(2024, 1, 1, 15, 30, 0)
        self.TestConfig.created_at = new_dt
        assert self.TestConfig.created_at == new_dt
    
    def test_timedelta_config_integration(self):
        """Test TimeDelta data type integration with Config."""
        # Test getting value
        assert isinstance(self.TestConfig.timeout, datetime.timedelta)
        
        # Test setting value
        new_td = datetime.timedelta(minutes=5)
        self.TestConfig.timeout = new_td
        assert self.TestConfig.timeout == new_td


# Clean up test file after tests
def teardown_module():
    """Clean up test configuration file."""
    config_file.unlink(missing_ok=True)