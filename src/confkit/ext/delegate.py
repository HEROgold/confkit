"""Extension to confkit adds delegate-related functionality.

A `Delegate` passes reads and writes through to a setting declared elsewhere, usually in another config file.

```python
class Settings:
    dashboard_url = AppConfig("http://localhost:8001")


class DashboardSettings:
    public_url = Delegate(Settings.dashboard_url)
```
"""

from __future__ import annotations

import dis
import sys
from typing import TYPE_CHECKING, Any, Generic, TypeVar

from confkit.config import Config

if TYPE_CHECKING:
    from types import FrameType

T = TypeVar("T")

_NAME_LOADS = frozenset(
    {
        "LOAD_NAME",
        "LOAD_GLOBAL",
        "LOAD_DEREF",
        "LOAD_CLASSDEREF",  # 3.11, class body reading a variable of the enclosing function.
        "LOAD_FROM_DICT_OR_DEREF",  # 3.12+, same as above.
        "LOAD_FAST",
        "LOAD_FAST_CHECK",
        "LOAD_FAST_BORROW",
    },
)
_SKIPPED = frozenset({"PRECALL", "EXTENDED_ARG"})  # PRECALL only exists on 3.11.


class Delegate(Generic[T]):
    """Descriptor that passes reads and writes through to another setting.

    Pass the target setting as a plain attribute read, like `Delegate(Settings.dashboard_url)`.
    `Settings.dashboard_url` evaluates to its value before `Delegate` runs, so `Delegate`
    reads the caller's CPython bytecode to find the expression and looks up the `Config` descriptor it names.

    The delegate stores nothing. Reading it reads the target's key, and assigning through
    an instance writes the target's key, in the target's file.
    A delegate of a delegate passes through to the same `Config` descriptor.
    """

    def __init__(self, target: T, /) -> None:  # noqa: ARG002  The value is only there for type checkers.
        """Find the `Config` descriptor named by the argument expression."""
        owner, target_descriptor = _find_target(_caller_frame())
        self._owner: type = owner
        self._target: Config[T] = target_descriptor

    def __get__(self, obj: object, obj_type: type | None = None) -> T:
        """Read the target setting."""
        return self._target.__get__(None, self._owner)

    def __set__(self, obj: object, value: T) -> None:
        """Write the target setting.

        The target's owner class is passed on, so `Config.__set__` never touches the delegating instance.
        """
        self._target.__set__(self._owner, value)


def _caller_frame() -> FrameType:
    """Return the frame that called `Delegate(...)`.

    `Delegate[str](...)` goes through `typing`'s generic alias, which adds its own frames.
    """
    frame = sys._getframe(2)  # noqa: SLF001  Skip this function and Delegate.__init__.
    while frame.f_globals.get("__name__") == "typing" and frame.f_back is not None:
        frame = frame.f_back
    return frame


def _find_target(frame: FrameType) -> tuple[type, Config[Any]]:
    """Find the descriptor read by the single argument of the call running in `frame`.

    Walks back from the CALL instruction over the LOAD_ATTR chain to the name it starts from,
    for example LOAD_NAME Settings, LOAD_ATTR dashboard_url.
    """
    instructions = [i for i in dis.get_instructions(frame.f_code) if i.opname not in _SKIPPED]
    call = next((n for n, i in enumerate(instructions) if i.offset == frame.f_lasti), None)
    attrs: list[str] = []
    base: str | None = None
    if call is not None and instructions[call].opname == "CALL" and instructions[call].arg == 1:
        for instruction in reversed(instructions[:call]):
            if instruction.opname == "LOAD_ATTR":
                attrs.append(instruction.argval)
                continue
            if instruction.opname in _NAME_LOADS:
                base = instruction.argval
            break

    if base is None or not attrs:
        msg = "Delegate needs a setting read as its only argument, like Delegate(Settings.dashboard_url)."
        raise TypeError(msg)

    *path, name = reversed(attrs)
    owner = _resolve_name(frame, base)
    for attr in path:
        owner = getattr(owner, attr)
    return _lookup_descriptor(owner, name)


def _resolve_name(frame: FrameType, name: str) -> object:
    """Look a name up the way the caller's code would.

    A class body's frame doesn't expose the enclosing function's variables. For a free variable,
    follow the frames that run the class statements out to the one that holds it.
    """
    scope = frame
    while name not in scope.f_locals and name in scope.f_code.co_freevars and scope.f_back is not None:
        scope = scope.f_back
    for namespace in (scope.f_locals, frame.f_globals, frame.f_builtins):
        if name in namespace:
            return namespace[name]
    msg = f"Delegate could not resolve {name!r}."
    raise NameError(msg)


def _lookup_descriptor(owner: object, name: str) -> tuple[type, Config[Any]]:
    """Return the class that declares the `Config` descriptor `name`, and the descriptor, following delegates."""
    cls = owner if isinstance(owner, type) else type(owner)
    for class_ in cls.__mro__:
        attr = vars(class_).get(name)
        if isinstance(attr, Delegate):
            return attr._owner, attr._target  # noqa: SLF001
        if isinstance(attr, Config):
            return class_, attr
    msg = f"{cls.__qualname__}.{name} is not a Config setting, so Delegate can't pass through to it."
    raise TypeError(msg)


__all__ = ["Delegate"]
