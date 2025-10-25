
from configparser import ConfigParser
from pathlib import Path
from confkit.config import Config


class DatabaseConfig(Config): ...
class ApiConfig(Config): ...

DatabaseConfig.set_parser(ConfigParser())
DatabaseConfig.set_file(Path("database.ini"))
ApiConfig.set_parser(ConfigParser())
ApiConfig.set_file(Path("api.ini"))

class AppConfiguration:
    """Application configuration with multiple config files."""

    db_host = DatabaseConfig("localhost")
    db_port = DatabaseConfig(5432)

    api_key = ApiConfig("default_api_key")
    api_timeout = ApiConfig(30)
