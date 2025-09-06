"""Argparse integration utilities for confkit (stage 1).

Functionality provided:
* Materialize argparse defaults into an ``args.ini`` (defaults only, not CLI values).
* Parse CLI arguments while ensuring defaults are persisted for inspection.

CLI values override defaults for the current run only and are NOT written back.
"""
from __future__ import annotations

from argparse import SUPPRESS, ArgumentParser
from configparser import ConfigParser
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - typing only
    from argparse import Action
    from collections.abc import Iterable, Iterator

ARGS_SECTION_DEFAULT = "Args"

__all__ = [
    "materialize_argparse_defaults",
    "parse_with_persisted_defaults",
]

def _iter_argument_actions(parser: ArgumentParser) -> Iterator[Action]:
    """Iterate real user argument actions (skips help & invalid dest)."""
    for action in parser._actions:  # noqa: SLF001
        dest = getattr(action, "dest", None)
        if dest in {None, "help"}:
            continue
        yield action  # type: ignore[misc]

def _format_default(default: object) -> str:
    """Format a default value for INI storage."""
    if isinstance(default, (list, tuple, set)) and not isinstance(default, (str, bytes)):
        return ",".join(str(v) for v in default)
    return str(default)

def materialize_argparse_defaults(
    parser: ArgumentParser,
    ini_path: Path | str = Path("args.ini"),
    *,
    section: str = ARGS_SECTION_DEFAULT,
    overwrite_missing_only: bool = True,
) -> Path:
    """Write parser default values to an INI file.

    Parameters
    ----------
    parser: ArgumentParser
        The parser whose defaults will be written.
    ini_path: Path | str
        Path to args.ini file to create/update.
    section: str
        Section name under which to store defaults.
    overwrite_missing_only: bool
        If True (default) only set options that are not already present.
        If False, rewrite all defaults (clobber existing values).

    Returns
    -------
    Path
        Path to the created/updated INI file.

    """
    path = Path(ini_path)
    cp = ConfigParser()
    cp.read(path)
    if not cp.has_section(section):
        cp.add_section(section)

    for action in _iter_argument_actions(parser):
        default = getattr(action, "default", SUPPRESS)
        if default in (SUPPRESS, None):
            continue
        option = action.dest.replace("-", "_")  # type: ignore[attr-defined]
        if overwrite_missing_only and cp.has_option(section, option):
            continue
        cp.set(section, option, _format_default(default))

    with path.open("w", encoding="utf-8") as f:
        cp.write(f)
    return path

def parse_with_persisted_defaults(
    parser: ArgumentParser,
    argv: Iterable[str] | None = None,
    *,
    ini_path: Path | str = Path("args.ini"),
    section: str = ARGS_SECTION_DEFAULT,
) -> tuple[object, Path]:
    """Parse arguments while persisting defaults to args.ini.

    Steps:
    1. Materialize defaults (only adding missing ones).
    2. Parse args (CLI values override defaults in memory only).

    Returns
    -------
    tuple[object, Path]
        (Namespace, path to INI file).

    """
    ini_file = materialize_argparse_defaults(parser, ini_path=ini_path, section=section)
    ns = parser.parse_args(list(argv) if argv is not None else None)
    return ns, ini_file
