
"""Tests for MsgspecParser (unified YAML/JSON/TOML parser)."""
import pathlib
import tempfile

import hypothesis.strategies as st
import msgspec.json
import msgspec.toml
import msgspec.yaml
import pytest
from hypothesis import given

from confkit.ext.parsers import MsgspecParser

config_value_strategy = st.one_of(
    st.text(),
    st.integers(),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.none(),
)

config_dict_strategy = st.fixed_dictionaries(
    {
        "section1": st.fixed_dictionaries(
            {"option1": config_value_strategy, "option2": config_value_strategy},
        ),
        "section2": st.fixed_dictionaries(
            {"optionA": config_value_strategy, "optionB": config_value_strategy},
        ),
    },
)


@given(data=config_dict_strategy)
def test_write_supported_formats(data: dict) -> None:
    formats = [
        (".json", msgspec.json, True),
        (".toml", msgspec.toml, False),
        (".yaml", msgspec.yaml, True),
        (".yml", msgspec.yaml, True),
    ]
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = pathlib.Path(tmpdir)
        for ext, parser, supports_none in formats:
            # TOML does not support None/null, so filter out such cases
            if not supports_none and any(v is None for section in data.values() for v in section.values()):
                continue  # skip this case for TOML
            file = tmp_path / f"test{ext}"
            p = MsgspecParser()
            p.data = data.copy()
            with file.open("w") as f:
                p.write(f)
            # Read back and compare
            with file.open("rb") as f:
                loaded = parser.decode(f.read())
            assert loaded == data

def test_write_unsupported_extension(tmp_path: pathlib.Path) -> None:
    file = tmp_path / "test.unsupported"
    p = MsgspecParser()
    p.data = {"section": {"option": "value"}}
    with pytest.raises(ValueError, match="Unsupported file extension for writing"):
        p.write(file)
