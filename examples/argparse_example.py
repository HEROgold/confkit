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

from confkit import Config
from confkit.data_types import List

# Setup a standard confkit config file (unrelated to argparse defaults file)
parser_ini = ConfigParser()
ini_path = Path("config.ini")
Config.write_on_edit = False
Config.set_parser(parser_ini)
Config.set_file(ini_path)

class AppConfig:
    debug = Config(False)
    host = Config("127.0.0.1")
    port = Config(8000)
    tags = Config(List(["example", "demo"]))

# Argparse parser definition with defaults
# Note: These defaults are only set on startup.
# Due to Config.write_on_edit = False, they will not be written to args.ini when changed.
ap = ArgumentParser(description="Demo application")
ap.add_argument("--host", default=AppConfig.host, help="Host to bind")
ap.add_argument("--port", type=int, default=AppConfig.port, help="Port to bind")
ap.add_argument("--debug", action="store_true", default=AppConfig.debug, help="Enable debug mode")
ap.add_argument("--tags", nargs="*", default=AppConfig.tags, help="List of tags")
