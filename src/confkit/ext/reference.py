"""Extension to confkit adds reference-related functionality.

It allows you to create relative references to other configuration files
"""

from pathlib import Path
from typing import Any

from confkit import Config
from confkit.data_types import BaseDataType

ConfigType = type[Config[Any]]


class Reference(BaseDataType[ConfigType]):
    """Data type for referencing other configuration.

    This data type allows you to create relative references to other
    configuration files within the confkit framework.
    """

    def __str__(self) -> str:
        """Return the string representation of the reference."""
        return f"{self.value._file}"  # noqa: SLF001

    def convert(self, value: str) -> ConfigType:
        """Convert a string value to the desired type."""
        file_path = Path(value)
        cls = self.value
        cls.set_file(file_path.resolve())
        return cls

    def __set__(self, instance: object, value: ConfigType) -> None:
        """Set the value on the owner configuration instance."""
        if not isinstance(value, type) or not issubclass(value, Config):
            msg = "Reference data type can only be set to Config<class>."
            raise TypeError(msg)
        self.value = value

    def __get__(self, instance: object, owner: type) -> ConfigType:
        """Get the value from the owner configuration instance."""
        return self.value

__all__ = [
    "Reference",
]
