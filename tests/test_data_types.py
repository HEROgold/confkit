"""Tests for data type classes in confkit.data_types."""
from datetime import UTC, date, datetime, time, timedelta
from typing import Final

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.data_types import Boolean, Date, DateTime, Dict, Float, List, Set, String, Time, TimeDelta, Tuple

DUMMY_DATE: Final = Date(year=2000, month=1, day=1)

class TestList:
    """Test the List data type."""

    def test_empty_list(self) -> None:
        """Test conversion of an empty string to an empty list."""
        list_type = List([1, 2, 3])
        assert list_type.convert("") == []

    def test_list_basic(self) -> None:
        """Test basic list functionality."""
        list_type = List([1, 2, 3])
        assert list_type.convert("1,2,3") == [1, 2, 3]
        assert str(list_type) == "1,2,3"

    def test_list_with_separator_in_values(self) -> None:
        """Test list with escaped separators in values."""
        list_type = List(["a", "b,c", "d"])
        list_type.value = ["a", "b,c", "d"]
        assert str(list_type) == "a,b\\,c,d"
        assert list_type.convert(str(list_type)) == ["a", "b,c", "d"]

    def test_list_with_escape_char(self) -> None:
        """Test list with escaped escape chars."""
        list_type = List(["a\\", "b", "c"])
        list_type.value = ["a\\", "b", "c"]
        assert str(list_type) == "a\\\\,b,c"
        assert list_type.convert(str(list_type)) == ["a\\", "b", "c"]

    def test_list_with_mixed_types(self) -> None:
        """Test list with mixed types using explicit data type."""
        str_data_type = String("")
        list_type = List(["1", "2", "3"], data_type=str_data_type)
        assert list_type.convert("1,2,3") == ["1", "2", "3"]

    def test_list_custom_separator(self) -> None:
        """Test list with custom separator."""
        list_type = List([1, 2, 3])
        list_type.separator = ";"
        list_type.value = [4, 5, 6]
        assert str(list_type) == "4;5;6"
        assert list_type.convert("7;8;9") == [7, 8, 9]

    @given(st.lists(st.integers()))
    def test_list_round_trip(self, values: list[int]) -> None:
        """Test that converting to string and back preserves values."""
        if not values:
            values = [0]  # Ensure non-empty list for initialization
        list_type = List(values)
        as_string = str(list_type)
        assert list_type.convert(as_string) == values


class TestTuple:
    """Test the Tuple data type."""

    def test_empty_tuple(self) -> None:
        """Test conversion of an empty string to an empty tuple."""
        tuple_type = Tuple((1, 2, 3))
        assert tuple_type.convert("") == ()

    def test_tuple_basic(self) -> None:
        """Test basic tuple functionality."""
        tuple_type = Tuple((1, 2, 3))
        assert tuple_type.convert("1,2,3") == (1, 2, 3)
        assert str(tuple_type) == "1,2,3"

    def test_tuple_with_separator_in_values(self) -> None:
        """Test tuple with escaped separators in values."""
        tuple_type = Tuple(("a", "b,c", "d"))
        tuple_type.value = ("a", "b,c", "d")
        assert str(tuple_type) == "a,b\\,c,d"
        assert tuple_type.convert(str(tuple_type)) == ("a", "b,c", "d")

    @given(st.lists(st.integers()).map(tuple))
    def test_tuple_round_trip(self, values: tuple[int, ...]) -> None:
        """Test that converting to string and back preserves values."""
        if not values:
            values = (0,)  # Ensure non-empty tuple for initialization
        tuple_type = Tuple(values)
        as_string = str(tuple_type)
        assert tuple_type.convert(as_string) == values


class TestSet:
    """Test the Set data type."""

    def test_empty_set(self) -> None:
        """Test conversion of an empty string to an empty set."""
        set_type = Set(set(), data_type=String())
        assert set_type.convert("") == set()

    def test_set_basic(self) -> None:
        """Test basic set functionality."""
        set_type = Set({1, 2, 3})
        assert set_type.convert("1,2,3") == {1, 2, 3}
        # Order can vary in string representation
        result = {int(x) for x in str(set_type).split(",")}
        assert result == {1, 2, 3}

    def test_set_with_custom_data_type(self) -> None:
        """Test set with a custom data type."""
        bool_data_type = Boolean(default=False)
        set_type = Set({True}, data_type=bool_data_type)
        assert set_type.convert("true,false,yes") == {True, False}

    def test_set_empty_default_error(self) -> None:
        """Test creating a set with an empty default raises error."""
        with pytest.raises(ValueError, match="Set default must have at least one element" ):
            Set(set())


class TestDict:
    """Test the Dict data type."""

    def test_empty_dict(self) -> None:
        """Test conversion of an empty string to an empty dict."""
        dict_type = Dict({"key": "value"})
        assert dict_type.convert("") == {}

    def test_dict_basic(self) -> None:
        """Test basic dict functionality."""
        dict_type = Dict({"a": 1, "b": 2})
        assert dict_type.convert("a=1,b=2") == {"a": 1, "b": 2}
        # Order can vary in string representation
        result = {}
        for pair in str(dict_type).split( ","):
            k, v = pair.split("=")
            result[k] = int(v)
        assert result == {"a": 1, "b": 2}

    def test_dict_with_custom_types(self) -> None:
        """Test dict with custom key and value types."""
        dict_type = Dict(
            {True: 1.0, False: 2.0},
            key_type=Boolean(default=True),
            value_type=Float(0.0),
        )
        assert dict_type.convert("true=1.5,false=2.5") == {True: 1.5, False: 2.5}

    def test_dict_invalid_entry(self) -> None:
        """Test dict with invalid entry format."""
        dict_type = Dict({"key": "value"})
        with pytest.raises(ValueError, match="Invalid dictionary entry" ):
            dict_type.convert("invalid_entry")

    def test_dict_empty_default_error(self) -> None:
        """Test creating a dict with an empty default raises error."""
        error_match = r"Dict requires either a default with at least one key/value pair, or both key_type and value_type to be specified."  # noqa: E501
        with pytest.raises(ValueError, match=error_match):
            Dict(value_type=String())  # pyright: ignore[reportCallIssue]
        with pytest.raises(ValueError, match=error_match):
            Dict(key_type=String())  # pyright: ignore[reportCallIssue]


class TestDate:
    """Test the Date data type."""

    def test_date_basic(self) -> None:
        """Test basic date functionality."""
        test_date = date(2023, 1, 1)
        date_type = Date(test_date)
        assert date_type.convert("2023-01-01") == test_date
        assert str(date_type) == "2023-01-01"

    def test_date_default(self) -> None:
        """Test date with default value."""
        # Since default uses datetime.now(), we can only check the type
        assert isinstance(DUMMY_DATE.value, date)

    def test_date_invalid(self) -> None:
        """Test date with invalid format."""
        with pytest.raises(ValueError, match="Invalid isoformat string: 'not-a-date'"):
            DUMMY_DATE.convert("not-a-date")


class TestTime:
    """Test the Time data type."""

    def test_time_basic(self) -> None:
        """Test basic time functionality."""
        test_time = time(12, 34, 56)
        time_type = Time(test_time)
        assert time_type.convert("12:34:56") == test_time
        assert str(time_type) == "12:34:56"

    def test_time_with_microseconds(self) -> None:
        """Test time with microseconds."""
        test_time = time(12, 34, 56, 789000)
        time_type = Time(test_time)
        assert time_type.convert("12:34:56.789000") == test_time
        assert str(time_type) == "12:34:56.789000"

    def test_time_default(self) -> None:
        """Test time with default value."""
        time_type = Time()
        # Since default uses datetime.now(), we can only check the type
        assert isinstance(time_type.value, time)


class TestDateTime:
    """Test the DateTime data type."""

    def test_datetime_basic(self) -> None:
        """Test basic datetime functionality."""
        test_dt = datetime(2023, 1, 1, 12, 34, 56, tzinfo=UTC)
        dt_type = DateTime(test_dt)
        assert dt_type.convert("2023-01-01T12:34:56+00:00") == test_dt
        assert str(dt_type) == "2023-01-01T12:34:56+00:00"

    def test_datetime_default(self) -> None:
        """Test datetime with default value."""
        dt_type = DateTime()
        # Since default uses datetime.now(), we can only check the type
        assert isinstance(dt_type.value, datetime)

    def test_datetime_with_timezone(self) -> None:
        """Test datetime with different timezone."""
        dt_str = "2023-01-01T12:34:56+01:00"
        dt_type = DateTime()
        converted = dt_type.convert(dt_str)
        assert converted.isoformat() == dt_str


class TestTimeDelta:
    """Test the TimeDelta data type."""

    def test_timedelta_basic(self) -> None:
        """Test basic timedelta functionality."""
        test_td = timedelta(seconds=300)  # 5 minutes
        td_type = TimeDelta(test_td)
        assert td_type.convert("300") == test_td
        assert str(td_type) == "300.0"

    def test_timedelta_default(self) -> None:
        """Test timedelta with default value."""
        td_type = TimeDelta()
        assert td_type.value == timedelta()
        assert str(td_type) == "0.0"

    def test_timedelta_fractional_seconds(self) -> None:
        """Test timedelta with fractional seconds."""
        test_td = timedelta(seconds=300.5)  # 5 minutes and 0.5 seconds
        td_type = TimeDelta(test_td)
        assert td_type.convert("300.5") == test_td
        assert str(td_type) == "300.5"
