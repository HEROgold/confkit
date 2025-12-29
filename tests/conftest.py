"""Pytest configuration for confkit tests."""
from __future__ import annotations

import warnings


def pytest_configure() -> None:
    """Silence known warnings emitted by the Config base class."""
    warnings.filterwarnings(
        "ignore",
        message=r"<Config> is the base class\. Subclass <Config> to avoid unexpected behavior\.",
    )
