
from configparser import ConfigParser
from enum import StrEnum
from pathlib import Path

from confkit import Config, Optional, String
from confkit import StrEnum as ConfigEnum

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class LogLevel(StrEnum):
    DEBUG = "debug"
    INFO = "info"
    ERROR = "error"

class ServerConfig:
    log_level = Config(ConfigEnum(LogLevel.INFO))
    db_url = Config(String("sqlite:///app.db"))
    fallback_level = Config(Optional(ConfigEnum(LogLevel.ERROR)))

config = ServerConfig()
config.log_level = LogLevel.DEBUG  # Type-safe
