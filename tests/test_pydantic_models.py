"""Tests for using Pydantic models as inputs to confkit Config descriptors."""
from __future__ import annotations

import warnings
from configparser import ConfigParser
from typing import TYPE_CHECKING

import pytest
from pydantic import BaseModel

from confkit.config import Config
from confkit.data_types import List
from confkit.ext.pydantic import apply_model

if TYPE_CHECKING:
    from collections.abc import Generator
    from pathlib import Path

warnings.filterwarnings(
    "ignore",
    message="<Config> is the base class. Subclass <Config> to avoid unexpected behavior.",
)


@pytest.fixture
def config_environment(tmp_path: Path) -> Generator[ConfigParser]:
    parser = ConfigParser()
    config_path = tmp_path / "pydantic.ini"
    config_path.touch()

    previous_parser = Config._parser
    previous_file = Config._file
    previous_read_state = Config._has_read_config
    previous_write_state = Config.write_on_edit

    Config.set_parser(parser)
    Config.set_file(config_path)
    Config._has_read_config = False
    Config.write_on_edit = True

    yield parser

    Config._parser = previous_parser
    Config._file = previous_file
    Config._has_read_config = previous_read_state
    Config.write_on_edit = previous_write_state


class ServiceModel(BaseModel):
    host: str
    port: int
    debug: bool
    timeout: float
    api_token: str | None = None


class FeatureFlagsModel(BaseModel):
    retries: int
    enabled: bool
    tags: list[str]


def test_pydantic_model_populates_config(config_environment: ConfigParser) -> None:
    parser = config_environment

    class ServiceConfig:
        host = Config("localhost")
        port = Config(8080)
        debug = Config(default=False)
        timeout = Config(30.0)
        api_token = Config("", optional=True)

    config_instance = ServiceConfig()
    payload = ServiceModel(
        host="api.internal",
        port=9090,
        debug=True,
        timeout=45.5,
        api_token=None,
    )

    apply_model(config_instance, payload)

    assert config_instance.host == payload.host
    assert config_instance.port == payload.port
    assert config_instance.debug is payload.debug
    assert config_instance.timeout == payload.timeout
    assert config_instance.api_token is None

    assert parser.get("ServiceConfig", "host") == payload.host
    assert parser.get("ServiceConfig", "port") == str(payload.port)


def test_pydantic_prevalidation_handles_type_casts(config_environment: ConfigParser) -> None:
    parser = config_environment

    class FeatureConfig:
        retries = Config(1)
        enabled = Config(default=False)
        tags = Config(List(["default"]))

    raw_payload = {
        "retries": "5",
        "enabled": "true",
        "tags": ("alpha", "beta"),
    }
    payload = FeatureFlagsModel(**raw_payload)

    config_instance = FeatureConfig()
    apply_model(config_instance, payload)

    assert config_instance.retries == 5  # noqa: PLR2004
    assert config_instance.enabled is True
    assert config_instance.tags == ["alpha", "beta"]

    assert parser.get("FeatureConfig", "tags") == "alpha,beta"
