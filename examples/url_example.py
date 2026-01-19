"""Example of using a custom URL data type with confkit."""
from pathlib import Path
from configparser import ConfigParser

from confkit import Config, BaseDataType
from urllib.parse import ParseResult, urlparse

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))

class URL(BaseDataType[ParseResult]):
    """A config value that is a URL."""

    def convert(self, value: str) -> ParseResult:
        """Convert a string value to a URL."""
        return urlparse(value)

class AppConfig:
    homepage = Config(URL(urlparse("https://github.com/HEROgold/confkit")))
    docs = Config(URL(urlparse("https://herogold.github.io/confkit/")))


def main() -> None:
    app_config = AppConfig()
    # Accessing and printing the parsed URLs
    print("Homepage:", app_config.homepage)
    print("Homepage scheme:", app_config.homepage.scheme)
    print("Homepage netloc:", app_config.homepage.netloc)
    print("Docs:", app_config.docs)
    print("Docs path:", app_config.docs.path)

    # You can also assign a new URL string
    app_config.homepage = "https://example.com/newpage"
    print("Updated homepage:", app_config.homepage)
    print("Updated homepage netloc:", app_config.homepage.netloc)



if __name__ == "__main__":
    main()
