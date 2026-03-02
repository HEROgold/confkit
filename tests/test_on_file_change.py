"""Tests for on_file_change method in Config descriptor."""
from pathlib import Path
from typing import Any, ClassVar

from hypothesis import given
from hypothesis import strategies as st

from confkit.config import Config


# config class with a custom on_file_change
class ConfigTest(Config[Any]):
    file_change_events: ClassVar[list[tuple[str, Any, Any]]] = []

    def on_file_change(self, origin: str, old: Any, new: Any) -> None:  # noqa: ANN401, D102
        self.__class__.file_change_events.append((origin, old, new))

config_file = Path("config_test.ini")
ConfigTest.set_file(config_file)
ConfigTest._watcher.has_changed = lambda: True # Always trigger file_changed. triggering the logging of events
ConfigTest.validate_types = False  # Disable strict type validation for testing
ConfigTest.write_on_edit = True

class Test:
    setting = ConfigTest(0)

prev_value = 0

@given(st.integers())
def test_on_file_change_get_and_set(value: int) -> None:
    """Test that on_file_change is called on get and set operations."""
    # This only tests the set event, but we also assert get for sanity.
    # To test the get event, we would need to write the file, before getting, but after setting.
    global prev_value  # noqa: PLW0603
    ConfigTest.file_change_events.clear()
    test = Test()
    events = ConfigTest.file_change_events

    assert len(events) == 0

    # Set the value
    test.setting = value
    assert len(events) == 1

    # Check the set event
    event = events[0]
    assert event[0] == "set"
    assert event[1] == prev_value
    assert event[2] == value

    # Get the value
    _ = test.setting
    assert len(events) == 2

    # Check the get event
    event = events[1]
    assert event[0] == "get"
    assert event[1] == value
    assert event[2] == value
    prev_value = value
