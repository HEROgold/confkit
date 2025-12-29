# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "confkit[pydantic]",
# ]
# ///
"""Example showing how to use Pydantic models with confkit.

Run with: python pydantic.py
Requires: pip install "confkit[pydantic]"
"""
from __future__ import annotations

from configparser import ConfigParser
from pathlib import Path

from pydantic import BaseModel

from confkit import Config
from confkit.ext.pydantic import apply_model

parser = ConfigParser()
Config.set_parser(parser)
Config.set_file(Path("pydantic.ini"))


class ServiceConfig:
    host = Config("localhost")
    port = Config(8080)
    debug = Config(False)
    timeout = Config(30.0)
    api_token = Config("", optional=True)


class ServiceSettings(BaseModel):
    host: str
    port: int
    debug: bool
    timeout: float
    api_token: str | None = None


def main() -> None:
    payload = ServiceSettings(
        host="api.service.local",
        port=9090,
        debug=True,
        timeout=42.0,
        api_token=None,
    )

    config = ServiceConfig()
    apply_model(config, payload)

    print(f"Host -> {ServiceConfig.host}")
    print(f"Port -> {ServiceConfig.port}")
    print(f"Debug -> {ServiceConfig.debug}")
    print(f"Timeout -> {ServiceConfig.timeout}")
    print(f"API token -> {ServiceConfig.api_token}")


if __name__ == "__main__":
    main()
