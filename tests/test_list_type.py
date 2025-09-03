"""Test the List data type."""

import pytest

from confkit.data_types import List, String
from confkit.exceptions import InvalidDefaultError

List.escape_char = "\\"

def test_list_with_escape_in_values() -> None:
    """Test that escapes in list values work correctly."""
    test_list = List(["path\\to\\file", "another\\path", "value,with,commas"])
    string_repr = str(test_list)
    new_list = List([""])
    result = new_list.convert(string_repr)
    assert result == ["path\\to\\file", "another\\path", "value,with,commas"]


def test_list_with_empty_values() -> None:
    """Test that empty values in lists work correctly."""
    test_list = List(["", "value", ""])
    string_repr = str(test_list)
    new_list = List([""])
    result = new_list.convert(string_repr)
    assert result == ["", "value", ""]


def test_list_with_escaped_sequences() -> None:
    """Test that complex escaped sequences work correctly."""
    test_list = List([
        "normal",
        "with,comma",
        "with\\escape",
        "with\\,both",
        "multiple,,,commas",
        "multiple\\\\escapees",
    ])
    string_repr = str(test_list)
    new_list = List([""])
    result = new_list.convert(string_repr)
    assert result == [
        "normal",
        "with,comma",
        "with\\escape",
        "with\\,both",
        "multiple,,,commas",
        "multiple\\\\escapees",
    ]


def test_empty_list_without_datatype() -> None:
    """Test that empty list without datatype throw exception."""
    with pytest.raises(InvalidDefaultError):
        List([])


def test_empty_list_with_datatype() -> None:
    """Test that empty list with data type works correctly."""
    test_list = List([], data_type=String(""))
    string_repr = str(test_list)
    new_list = List([""], data_type=String(""))
    result = new_list.convert(string_repr)
    assert result == []
    assert string_repr == ""

def test_empty_list() -> None:
    """Test that empty list with data type works correctly."""
    test_list = List([""])
    string_repr = str(test_list)
    new_list = List([""])
    result = new_list.convert(string_repr)
    assert result == []
    assert string_repr == ""
