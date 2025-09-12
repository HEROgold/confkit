"""Test suite for testing supposedly unreachable code paths in data_types.py."""

import pytest
from hypothesis import given
from hypothesis import strategies as st

from confkit.data_types import BaseDataType


class DataType(BaseDataType[str]):
    """Basic DataType that doesn't do anything."""

    def convert(self, value: str) -> str: ... # ty: ignore[invalid-return-type].  # noqa: D102

class MockBase:
    """Mock base class without __args__."""


def test_base_data_type_validate_unreachable_path() -> None:
    """Test the unreachable TypeError path in BaseDataType.validate.

    This tests lines 41-42 in data_types.py which are theoretically unreachable
    but we can trigger them by creating a malformed class hierarchy.
    """
    test_type = DataType("test")
    # Intentionally create a malformed class hierarchy
    setattr(test_type.__class__, "__orig_bases__", (MockBase,))  # noqa: B010
    with pytest.raises(TypeError, match=r"This should not have raised.*DTBDT"):
        test_type.validate()


def test_base_data_type_validate_no_type_args() -> None:
    """Test another path to reach the supposedly unreachable code.

    This creates a base class that has __args__ but is empty.
    """
    class MockBaseWithEmptyArgs:
        __args__ = ()

    test_type = DataType("test")
    setattr(test_type.__class__, "__orig_bases__", (MockBaseWithEmptyArgs,))  # noqa: B010
    with pytest.raises(TypeError, match=r"This should not have raised.*DTBDT"):
        test_type.validate()


@given(st.text(min_size=1))
def test_base_data_type_validate_unreachable_path_hypothesis(test_value: str) -> None:
    """Test the unreachable TypeError path with various string values using Hypothesis."""
    test_type = DataType(test_value)

    setattr(test_type.__class__, "__orig_bases__", (MockBase,))  # noqa: B010
    with pytest.raises(TypeError, match=r"This should not have raised.*DTBDT"):
        test_type.validate()

