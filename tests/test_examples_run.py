"""Ensure every example script can be executed end-to-end."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = PROJECT_ROOT / "examples"
EXAMPLE_SCRIPTS = sorted(EXAMPLES_DIR.glob("*.py"))

if not EXAMPLE_SCRIPTS:
    pytest.skip("No example scripts found", allow_module_level=True)


@pytest.mark.parametrize("example_script", EXAMPLE_SCRIPTS, ids=lambda p: p.name)
def test_example_script_runs(example_script: Path, tmp_path: Path) -> None:
    workdir = tmp_path / example_script.stem
    shutil.copytree(EXAMPLES_DIR, workdir, dirs_exist_ok=True)
    script_path = workdir / example_script.name

    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}{os.pathsep}{existing_pythonpath}"
        if existing_pythonpath
        else str(PROJECT_ROOT)
    )

    completed = subprocess.run(  # noqa: S603 This runs our own examples. so it's trusted code.
        [sys.executable, str(script_path)],
        check=False, cwd=workdir,
        env=env,
        capture_output=True,
        text=True,
    )

    if completed.returncode != 0:
        msg = (
            f"{example_script.name} exited with {completed.returncode}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
        raise AssertionError(msg)
