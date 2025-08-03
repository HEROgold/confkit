"""Test cases for the UNSET sentinel from confkit.sentinels."""

from confkit.sentinels import UNSET


def test_sentinel_equality() -> None:
    """Test UNSET sentinel equality behavior."""
    # Test __eq__ returns False for any comparison
    test_value = 42
    assert (UNSET == UNSET) is False  # noqa: PLR0124
    assert (UNSET == None) is False  # noqa: E711
    assert (UNSET == "test") is False
    assert (UNSET == test_value) is False  # noqa: SIM300


def test_sentinel_bool() -> None:
    """Test UNSET sentinel boolean behavior."""
    assert bool(UNSET) is False
    assert not UNSET


def test_sentinel_hash() -> None:
    """Test UNSET sentinel hash behavior."""
    assert hash(UNSET) == 0


def test_sentinel_repr() -> None:
    """Test UNSET sentinel repr behavior."""
    assert repr(UNSET) == "MISSING"
