
from configparser import ConfigParser
from pathlib import Path

from confkit import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class AppConfig:
    debug = Config(False)
    port = Config(8080)
    host = Config("localhost")
    timeout = Config(30.5)
    api_key = Config("", optional=True)

config = AppConfig()
print(config.debug)  # False
config.port = 9000   # Automatically saves to config.ini if write_on_edit is true (default).
