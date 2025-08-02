
from configparser import ConfigParser
from pathlib import Path

from configurator.config import Config

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("config.ini"))


class ServiceConfig:
    retry_count = Config(3)
    timeout = Config(30)

    @Config.with_setting(retry_count)
    def process(self, data, **kwargs):
        retries = kwargs.get('retry_count')
        return f"Processing with {retries} retries"

    @Config.as_kwarg("ServiceConfig", "timeout", "request_timeout", 60)
    def request(self, url, **kwargs):
        timeout = kwargs.get('request_timeout')
        return f"Request timeout: {timeout}s"

service = ServiceConfig()
result = service.process("data")  # Uses current retry_count
