"""Tests for enum types displaying allowed values."""
import enum
from enum import IntEnum, IntFlag, StrEnum, auto

from confkit.data_types import Enum, Optional
from confkit.data_types import IntEnum as ConfigIntEnum
from confkit.data_types import IntFlag as ConfigIntFlag
from confkit.data_types import StrEnum as ConfigStrEnum


class SampleEnum(enum.Enum):
    """Sample enum for standard Enum type."""

    OPTION_A = auto()
    OPTION_B = auto()
    OPTION_C = auto()


class SampleStrEnum(StrEnum):
    """Sample enum for StrEnum type."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class SampleIntEnum(IntEnum):
    """Sample enum for IntEnum type."""

    LOW = 0
    MEDIUM = 5
    HIGH = 10


class SampleIntFlag(IntFlag):
    """Sample enum for IntFlag type."""

    READ = 1
    WRITE = 2
    EXECUTE = 4


class TestEnumAllowedValues:
    """Test that enum types display allowed values."""

    def test_enum_str_includes_allowed_values(self) -> None:
        """Test that standard Enum __str__ includes all allowed values."""
        enum_type = Enum(SampleEnum.OPTION_B)
        result = str(enum_type)

        # Should include the current value
        assert "OPTION_B" in result

        # Should include the allowed values comment
        assert "# allowed:" in result
        assert "OPTION_A" in result
        assert "OPTION_B" in result
        assert "OPTION_C" in result

    def test_str_enum_str_includes_allowed_values(self) -> None:
        """Test that StrEnum __str__ includes all allowed values."""
        enum_type = ConfigStrEnum(SampleStrEnum.INFO)
        result = str(enum_type)

        # Should include the current value
        assert "info" in result

        # Should include the allowed values comment
        assert "# allowed:" in result
        assert "debug" in result
        assert "info" in result
        assert "warning" in result
        assert "error" in result

    def test_int_enum_str_includes_allowed_values(self) -> None:
        """Test that IntEnum __str__ includes all allowed values with their integer values."""
        enum_type = ConfigIntEnum(SampleIntEnum.MEDIUM)
        result = str(enum_type)

        # Should include the current value
        assert "5" in result

        # Should include the allowed values comment with names and values
        assert "# allowed:" in result
        assert "LOW(0)" in result
        assert "MEDIUM(5)" in result
        assert "HIGH(10)" in result

    def test_int_flag_str_includes_allowed_values(self) -> None:
        """Test that IntFlag __str__ includes all allowed values with their integer values."""
        enum_type = ConfigIntFlag(SampleIntFlag.WRITE)
        result = str(enum_type)

        # Should include the current value
        assert "2" in result

        # Should include the allowed values comment with names and values
        assert "# allowed:" in result
        assert "READ(1)" in result
        assert "WRITE(2)" in result
        assert "EXECUTE(4)" in result


class TestEnumConvertWithComments:
    """Test that enum convert methods correctly strip inline comments."""

    def test_enum_convert_strips_comment(self) -> None:
        """Test that Enum.convert strips inline comments."""
        enum_type = Enum(SampleEnum.OPTION_A)
        result = enum_type.convert("OPTION_B  # allowed: OPTION_A, OPTION_B, OPTION_C")
        assert result == SampleEnum.OPTION_B

    def test_str_enum_convert_strips_comment(self) -> None:
        """Test that StrEnum.convert strips inline comments."""
        enum_type = ConfigStrEnum(SampleStrEnum.INFO)
        result = enum_type.convert("warning  # allowed: debug, info, warning, error")
        assert result == SampleStrEnum.WARNING

    def test_int_enum_convert_strips_comment(self) -> None:
        """Test that IntEnum.convert strips inline comments."""
        enum_type = ConfigIntEnum(SampleIntEnum.LOW)
        result = enum_type.convert("10  # allowed: LOW(0), MEDIUM(5), HIGH(10)")
        assert result == SampleIntEnum.HIGH

    def test_int_flag_convert_strips_comment(self) -> None:
        """Test that IntFlag.convert strips inline comments."""
        enum_type = ConfigIntFlag(SampleIntFlag.READ)
        result = enum_type.convert("4  # allowed: READ(1), WRITE(2), EXECUTE(4)")
        assert result == SampleIntFlag.EXECUTE

    def test_enum_convert_without_comment(self) -> None:
        """Test that Enum.convert works without comments (backwards compatibility)."""
        enum_type = Enum(SampleEnum.OPTION_A)
        result = enum_type.convert("OPTION_C")
        assert result == SampleEnum.OPTION_C

    def test_str_enum_convert_without_comment(self) -> None:
        """Test that StrEnum.convert works without comments (backwards compatibility)."""
        enum_type = ConfigStrEnum(SampleStrEnum.INFO)
        result = enum_type.convert("debug")
        assert result == SampleStrEnum.DEBUG

    def test_int_enum_convert_without_comment(self) -> None:
        """Test that IntEnum.convert works without comments (backwards compatibility)."""
        enum_type = ConfigIntEnum(SampleIntEnum.LOW)
        result = enum_type.convert("5")
        assert result == SampleIntEnum.MEDIUM

    def test_int_flag_convert_without_comment(self) -> None:
        """Test that IntFlag.convert works without comments (backwards compatibility)."""
        enum_type = ConfigIntFlag(SampleIntFlag.READ)
        result = enum_type.convert("2")
        assert result == SampleIntFlag.WRITE


class TestOptionalEnumAllowedValues:
    """Test that Optional wrapped enum types display allowed values."""

    def test_optional_enum_str_includes_allowed_values(self) -> None:
        """Test that Optional(Enum) __str__ includes all allowed values."""
        enum_type = Enum(SampleEnum.OPTION_B)
        optional_enum = Optional(enum_type)
        result = str(optional_enum)

        # Should include the current value
        assert "OPTION_B" in result

        # Should include the allowed values comment
        assert "# allowed:" in result
        assert "OPTION_A" in result
        assert "OPTION_B" in result
        assert "OPTION_C" in result

    def test_optional_str_enum_str_includes_allowed_values(self) -> None:
        """Test that Optional(StrEnum) __str__ includes all allowed values."""
        enum_type = ConfigStrEnum(SampleStrEnum.WARNING)
        optional_enum = Optional(enum_type)
        result = str(optional_enum)

        # Should include the current value
        assert "warning" in result

        # Should include the allowed values comment
        assert "# allowed:" in result
        assert "debug" in result
        assert "info" in result
        assert "warning" in result
        assert "error" in result


class TestEnumRoundTrip:
    """Test that enum values can be written and read back correctly."""

    def test_enum_round_trip_with_str(self) -> None:
        """Test that Enum values survive a str() -> convert() round trip."""
        enum_type = Enum(SampleEnum.OPTION_A)

        # Convert to string (includes allowed values comment)
        str_value = str(enum_type)

        # Convert back (should strip comment)
        result = enum_type.convert(str_value)
        assert result == SampleEnum.OPTION_A

    def test_str_enum_round_trip_with_str(self) -> None:
        """Test that StrEnum values survive a str() -> convert() round trip."""
        enum_type = ConfigStrEnum(SampleStrEnum.ERROR)

        str_value = str(enum_type)
        result = enum_type.convert(str_value)
        assert result == SampleStrEnum.ERROR

    def test_int_enum_round_trip_with_str(self) -> None:
        """Test that IntEnum values survive a str() -> convert() round trip."""
        enum_type = ConfigIntEnum(SampleIntEnum.HIGH)

        str_value = str(enum_type)
        result = enum_type.convert(str_value)
        assert result == SampleIntEnum.HIGH

    def test_int_flag_round_trip_with_str(self) -> None:
        """Test that IntFlag values survive a str() -> convert() round trip."""
        enum_type = ConfigIntFlag(SampleIntFlag.EXECUTE)

        str_value = str(enum_type)
        result = enum_type.convert(str_value)
        assert result == SampleIntFlag.EXECUTE
