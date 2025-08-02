"""Private sentinel for missing values."""

from typing import Any


class _MissingSentinel:
    __slots__ = ()

    def __eq__(self, other: object) -> bool:
        return False

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "MISSING"

UNSET: Any = _MissingSentinel()
