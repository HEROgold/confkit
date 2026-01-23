from configparser import ConfigParser
from pathlib import Path
from tempfile import TemporaryDirectory

from confkit.config import Config


def test_two_instances_share_values_and_on_file_change_called() -> None:
    """Verify two instances of the same Config-backed class see the same values.

    Also assert that the `on_file_change` hook (attached to the descriptor)
    is invoked when the file is observed to have changed.
    """
    with TemporaryDirectory() as tmpdir:
        config_file = Path(tmpdir) / "test.ini"

        parser = ConfigParser()
        # Use the global Config parser/file for tests (same pattern as other tests)
        Config.set_parser(parser)
        Config.set_file(config_file)
        Config.write_on_edit = True

        # Initialize file with a section and default value
        parser.add_section("AppConfig")
        parser.set("AppConfig", "debug", "False")
        with config_file.open("w") as f:
            parser.write(f)

        events: list = []

        # Attach a single handler to the descriptor (it's shared across instances)
        def handler(origin, old, new) -> None:  # noqa: ANN001
            events.append((origin, old, new))

        class AppConfigLocal:
            debug = Config(False)
            debug.on_file_change = handler

        a1 = AppConfigLocal()
        a2 = AppConfigLocal()

        # initial value is False
        assert a1.debug is False
        assert a2.debug is False

        # change via instance a1; this writes to the backing file
        a1.debug = True

        # reading from a2 should reflect the updated value
        assert a2.debug is True

        # the descriptor-level handler should have been called at least once
        assert any(ev[0] in ("get", "set") for ev in events)
