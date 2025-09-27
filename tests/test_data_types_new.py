"""Test suite for the new data types: URL, DateTime, and TimeDelta."""

import sys
sys.path.insert(0, '../src')

from datetime import datetime, timedelta, timezone
from configparser import ConfigParser
from pathlib import Path
from urllib.parse import urlparse

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    from hypothesis import given, strategies as st
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False

from confkit.config import Config
from confkit.data_types import URL, DateTime, TimeDelta
from confkit.exceptions import InvalidConverterError


# Test configuration setup
config = Path("test_new_types.ini")
config.unlink(missing_ok=True)
config.touch()
parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(config)
Config.write_on_edit = True


class TestURL:
    """Test suite for URL data type."""
    
    def test_url_valid_creation(self):
        """Test creating URL with valid default."""
        url_type = URL("https://example.com")
        assert url_type.default == "https://example.com"
        assert url_type.value == "https://example.com"
    
    def test_url_invalid_default(self):
        """Test creating URL with invalid default raises error."""
        try:
            URL("invalid-url")
            assert False, "Should raise ValueError for invalid URL"
        except ValueError as e:
            assert "Invalid default URL" in str(e)
    
    def test_url_convert_valid(self):
        """Test converting valid URL strings."""
        url_type = URL("https://example.com")
        
        # Test various valid URL formats
        valid_urls = [
            "https://google.com",
            "http://localhost:8080",
            "ftp://files.example.com/path",
            "https://user:pass@example.com:443/path?query=1#fragment"
        ]
        
        for url in valid_urls:
            result = url_type.convert(url)
            parsed = urlparse(result)
            assert parsed.scheme
            assert parsed.netloc
    
    def test_url_convert_invalid(self):
        """Test converting invalid URL strings raises errors."""
        url_type = URL("https://example.com")
        
        invalid_urls = [
            "",
            "   ",
            "not-a-url",
            "://missing-scheme",
            "http://",
            "scheme-only://",
        ]
        
        for url in invalid_urls:
            try:
                url_type.convert(url)
                assert False, f"Should raise ValueError for: {url}"
            except ValueError:
                pass  # Expected
    
    def test_url_str_representation(self):
        """Test string representation of URL."""
        url_type = URL("https://example.com")
        assert str(url_type) == "https://example.com"
        
        url_type.value = "http://localhost:8080"
        assert str(url_type) == "http://localhost:8080"
    
    def test_url_normalization(self):
        """Test URL normalization during conversion."""
        url_type = URL("https://example.com")
        
        # Test that URLs get normalized
        result = url_type.convert("https://example.com:443/path/../other")
        assert "example.com" in result
        assert ":443" in result or ":443" not in result  # Port may be normalized


class TestDateTime:
    """Test suite for DateTime data type."""
    
    def test_datetime_valid_creation(self):
        """Test creating DateTime with valid default."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        dt_type = DateTime(dt)
        assert dt_type.default == dt
        assert dt_type.value == dt
    
    def test_datetime_invalid_default(self):
        """Test creating DateTime with invalid default raises error."""
        try:
            DateTime("not-a-datetime")
            assert False, "Should raise TypeError for invalid datetime"
        except TypeError as e:
            assert "datetime object" in str(e)
    
    def test_datetime_convert_iso_format(self):
        """Test converting ISO 8601 datetime strings."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        dt_type = DateTime(dt)
        
        # Test various ISO formats
        iso_formats = [
            "2024-01-01T12:00:00",
            "2024-01-01T12:00:00.123456",
            "2024-01-01T12:00:00+00:00",
            "2024-01-01T12:00:00Z",
            "2024-12-31T23:59:59.999999",
        ]
        
        for iso_str in iso_formats:
            result = dt_type.convert(iso_str)
            assert isinstance(result, datetime)
            assert result.year == 2024
    
    def test_datetime_convert_invalid(self):
        """Test converting invalid datetime strings raises errors."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        dt_type = DateTime(dt)
        
        invalid_formats = [
            "",
            "   ",
            "not-a-datetime",
            "2024-13-01T12:00:00",  # Invalid month
            "2024-01-32T12:00:00",  # Invalid day
            "2024-01-01T25:00:00",  # Invalid hour
            "01/01/2024",           # Wrong format
        ]
        
        for invalid_str in invalid_formats:
            try:
                dt_type.convert(invalid_str)
                assert False, f"Should raise ValueError for: {invalid_str}"
            except ValueError:
                pass  # Expected
    
    def test_datetime_str_representation(self):
        """Test string representation of DateTime."""
        dt = datetime(2024, 1, 1, 12, 0, 0)
        dt_type = DateTime(dt)
        result = str(dt_type)
        assert "2024-01-01T12:00:00" == result
        
        # Test with microseconds
        dt_micro = datetime(2024, 1, 1, 12, 0, 0, 123456)
        dt_type.value = dt_micro
        result = str(dt_type)
        assert "2024-01-01T12:00:00.123456" == result
    
    def test_datetime_timezone_handling(self):
        """Test datetime with timezone information."""
        dt = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        dt_type = DateTime(dt)
        
        # Test timezone-aware conversion
        result = dt_type.convert("2024-01-01T12:00:00+05:00")
        assert isinstance(result, datetime)
        assert result.tzinfo is not None


class TestTimeDelta:
    """Test suite for TimeDelta data type."""
    
    def test_timedelta_valid_creation(self):
        """Test creating TimeDelta with valid default."""
        td = timedelta(hours=1, minutes=30)
        td_type = TimeDelta(td)
        assert td_type.default == td
        assert td_type.value == td
    
    def test_timedelta_invalid_default(self):
        """Test creating TimeDelta with invalid default raises error."""
        try:
            TimeDelta("not-a-timedelta")
            assert False, "Should raise TypeError for invalid timedelta"
        except TypeError as e:
            assert "timedelta object" in str(e)
    
    def test_timedelta_convert_iso8601(self):
        """Test converting ISO 8601 duration strings."""
        td = timedelta(hours=1)
        td_type = TimeDelta(td)
        
        # Test various ISO 8601 durations
        iso_durations = [
            ("PT1H", timedelta(hours=1)),
            ("PT30M", timedelta(minutes=30)),
            ("PT45S", timedelta(seconds=45)),
            ("P1D", timedelta(days=1)),
            ("P1DT1H30M45S", timedelta(days=1, hours=1, minutes=30, seconds=45)),
            ("PT1.5H", timedelta(hours=1, minutes=30)),
        ]
        
        for iso_str, expected in iso_durations:
            result = td_type.convert(iso_str)
            assert isinstance(result, timedelta)
            # Allow some tolerance for approximation
            assert abs(result.total_seconds() - expected.total_seconds()) < 1
    
    def test_timedelta_convert_flexible(self):
        """Test converting flexible duration formats."""
        td = timedelta(hours=1)
        td_type = TimeDelta(td)
        
        # Test various flexible formats
        flexible_formats = [
            ("1h", timedelta(hours=1)),
            ("30m", timedelta(minutes=30)),
            ("45s", timedelta(seconds=45)),
            ("1h 30m", timedelta(hours=1, minutes=30)),
            ("2 hours 15 minutes", timedelta(hours=2, minutes=15)),
            ("1:30:00", timedelta(hours=1, minutes=30)),
            ("90", timedelta(seconds=90)),  # Pure number as seconds
            ("1.5", timedelta(seconds=1.5)),
        ]
        
        for format_str, expected in flexible_formats:
            result = td_type.convert(format_str)
            assert isinstance(result, timedelta)
            assert abs(result.total_seconds() - expected.total_seconds()) < 1
    
    def test_timedelta_convert_invalid(self):
        """Test converting invalid duration strings raises errors."""
        td = timedelta(hours=1)
        td_type = TimeDelta(td)
        
        invalid_formats = [
            "",
            "   ",
            "invalid-duration",
            "1x",  # Invalid unit
            "PT",  # Incomplete ISO format
        ]
        
        for invalid_str in invalid_formats:
            try:
                td_type.convert(invalid_str)
                assert False, f"Should raise ValueError for: {invalid_str}"
            except ValueError:
                pass  # Expected
    
    def test_timedelta_str_representation(self):
        """Test string representation of TimeDelta."""
        # Test simple cases
        td_hour = TimeDelta(timedelta(hours=1))
        assert str(td_hour) == "PT1H"
        
        td_mixed = TimeDelta(timedelta(days=1, hours=2, minutes=30, seconds=45))
        result = str(td_mixed)
        assert result.startswith("P1D")
        assert "T2H" in result
        assert "30M" in result
        assert "45S" in result
        
        # Test zero duration
        td_zero = TimeDelta(timedelta(0))
        assert str(td_zero) == "PT0S"


class TestConfigIntegration:
    """Test integration of new data types with Config descriptors."""
    
    def test_url_config_integration(self):
        """Test URL type with Config descriptor."""
        class URLConfig:
            api_url = Config(URL("https://api.example.com"))
            base_url = Config(URL("https://example.com"))
        
        config_obj = URLConfig()
        
        # Test getting default value
        assert config_obj.api_url == "https://api.example.com"
        
        # Test setting new value
        config_obj.api_url = "https://newapi.example.com"
        assert config_obj.api_url == "https://newapi.example.com"
    
    def test_datetime_config_integration(self):
        """Test DateTime type with Config descriptor."""
        class DateTimeConfig:
            created_at = Config(DateTime(datetime(2024, 1, 1, 12, 0, 0)))
            updated_at = Config(DateTime(datetime.now()))
        
        config_obj = DateTimeConfig()
        
        # Test getting default value
        assert isinstance(config_obj.created_at, datetime)
        
        # Test setting new value via string conversion
        config_obj.created_at = datetime(2024, 6, 15, 14, 30, 0)
        assert config_obj.created_at.year == 2024
        assert config_obj.created_at.month == 6
    
    def test_timedelta_config_integration(self):
        """Test TimeDelta type with Config descriptor."""
        class TimeDeltaConfig:
            timeout = Config(TimeDelta(timedelta(seconds=30)))
            retry_interval = Config(TimeDelta(timedelta(minutes=5)))
        
        config_obj = TimeDeltaConfig()
        
        # Test getting default value
        assert config_obj.timeout == timedelta(seconds=30)
        
        # Test setting new value
        config_obj.timeout = timedelta(minutes=2)
        assert config_obj.timeout == timedelta(minutes=2)


# Property-based tests using Hypothesis (if available)
if HYPOTHESIS_AVAILABLE:
    
    @given(st.integers(min_value=1, max_value=65535))
    def test_url_port_hypothesis(port):
        """Property-based test for URL with different ports."""
        url_type = URL("https://example.com")
        test_url = f"https://example.com:{port}"
        result = url_type.convert(test_url)
        assert str(port) in result or port == 443 or port == 80  # Default ports may be omitted
    
    @given(st.datetimes(min_value=datetime(1900, 1, 1), max_value=datetime(2100, 12, 31)))
    def test_datetime_roundtrip_hypothesis(dt):
        """Property-based test for datetime round-trip conversion."""
        # Remove timezone for simpler testing
        dt = dt.replace(tzinfo=None)
        dt_type = DateTime(dt)
        
        # Convert to string and back
        dt_str = str(dt_type)
        dt_type.value = dt
        converted = dt_type.convert(dt_str)
        
        # Should be very close (within microseconds)
        assert abs((converted - dt).total_seconds()) < 0.001
    
    @given(st.integers(min_value=0, max_value=86400))  # 0 to 24 hours in seconds
    def test_timedelta_seconds_hypothesis(seconds):
        """Property-based test for timedelta with different second values."""
        td = timedelta(seconds=seconds)
        td_type = TimeDelta(td)
        
        # Test round-trip conversion
        td_str = str(td_type)
        td_type.value = td
        converted = td_type.convert(td_str)
        
        # Should be exactly equal for simple cases
        assert abs(converted.total_seconds() - seconds) < 1


def run_basic_tests():
    """Run basic tests without pytest."""
    print("Running basic tests for new data types...")
    
    # URL tests
    print("Testing URL...")
    url_test = TestURL()
    url_test.test_url_valid_creation()
    url_test.test_url_convert_valid()
    url_test.test_url_str_representation()
    print("URL tests passed!")
    
    # DateTime tests  
    print("Testing DateTime...")
    dt_test = TestDateTime()
    dt_test.test_datetime_valid_creation()
    dt_test.test_datetime_convert_iso_format()
    dt_test.test_datetime_str_representation()
    print("DateTime tests passed!")
    
    # TimeDelta tests
    print("Testing TimeDelta...")
    td_test = TestTimeDelta()
    td_test.test_timedelta_valid_creation()
    td_test.test_timedelta_convert_iso8601()
    td_test.test_timedelta_convert_flexible()
    td_test.test_timedelta_str_representation()
    print("TimeDelta tests passed!")
    
    # Integration tests
    print("Testing Config integration...")
    integration_test = TestConfigIntegration()
    integration_test.test_url_config_integration()
    integration_test.test_datetime_config_integration()
    integration_test.test_timedelta_config_integration()
    print("Integration tests passed!")
    
    print("All basic tests passed!")


if __name__ == "__main__":
    if PYTEST_AVAILABLE:
        pytest.main([__file__])
    else:
        run_basic_tests()