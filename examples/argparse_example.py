"""Example showing argparse + confkit integration stage 1.

Run:
    python argparse_example.py --host 0.0.0.0 --port 9090

Observe that args.ini is created (or updated) with default values only.
CLI provided host/port will NOT be written to args.ini.
"""
from __future__ import annotations

from argparse import ArgumentParser
from configparser import ConfigParser
from pathlib import Path

from confkit import Config, materialize_argparse_defaults, parse_with_persisted_defaults

# Setup a standard confkit config file (unrelated to argparse defaults file)
parser_ini = ConfigParser()
Config.set_parser(parser_ini)
Config.set_file(Path("config.ini"))

class AppConfig:
    debug = Config(False)
    host = Config("127.0.0.1")
    port = Config(8000)

# Argparse parser definition with defaults
ap = ArgumentParser(description="Demo application")
ap.add_argument("--host", default="127.0.0.1", help="Host to bind")
ap.add_argument("--port", type=int, default=8000, help="Port to bind")
ap.add_argument("--debug", action="store_true", default=False, help="Enable debug mode")
ap.add_argument("--tags", nargs="*", default=["api", "v1"], help="List of tags (space separated)")

# Materialize defaults (creates args.ini if not present)
materialize_argparse_defaults(ap, ini_path=Path("args.ini"))

# Parse CLI (overrides not saved back)
ns, ini_path = parse_with_persisted_defaults(ap)

print("Parsed CLI namespace:", ns)
print("Defaults file at:", ini_path.resolve())
