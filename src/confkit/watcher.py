"""A simple file watcher to monitor changes in a file."""
from pathlib import Path


class FileWatcher:  # noqa: D101
    def __init__(self, filepath: Path) -> None:  # noqa: D107
        self.filepath = filepath
        self.last_modified = None

    def has_changed(self) -> bool:
        """Check if the file has been modified since the last check."""
        current_modified = self.filepath.stat().st_mtime
        if self.last_modified is None or current_modified != self.last_modified:
            self.last_modified = current_modified
            return True
        return False
