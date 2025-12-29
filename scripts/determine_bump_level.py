"""Determine the version bump level from PR labels.

This helper reads the `LABELS_JSON` environment variable (as emitted by GitHub
Actions) and writes the detected bump level to `GITHUB_OUTPUT`. The workflow can
then branch on the `level` output to decide whether to run `uv version bump`.
"""  # noqa: INP001
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ALLOWED_LABELS = ("major", "minor", "patch")


def _ensure_output_path(path: str | None) -> Path:
    if path:
        return Path(path)
    msg = "GITHUB_OUTPUT is not set; cannot emit workflow output."
    raise SystemExit(msg)


def determine_level(labels: list[str]) -> str:
    """Return the requested bump level or an empty string when not provided."""
    present = [label for label in labels if label.lower() in ALLOWED_LABELS]
    unique: list[str] = []
    for label in present:
        if label not in unique:
            unique.append(label)
    if len(unique) > 1:
        msg = "Multiple release labels (major/minor/patch) detected. Please keep exactly one."
        raise SystemExit(msg)
    return unique[0] if unique else ""


def main() -> None:
    """CLI entry point to determine the bump level from PR labels."""
    parser = argparse.ArgumentParser(description=__doc__ or "determine bump level")
    parser.add_argument(
        "--labels-json",
        default=None,
        help="JSON array of label names (defaults to $LABELS_JSON)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Path to write the GitHub output (defaults to $GITHUB_OUTPUT)",
    )
    args = parser.parse_args()

    labels_json = args.labels_json or os.environ.get("LABELS_JSON") or "[]"
    try:
        labels = json.loads(labels_json)
    except json.JSONDecodeError as exc:
        msg = f"Invalid LABELS_JSON payload: {exc}"
        raise SystemExit(msg) from exc

    level = determine_level(labels)
    output_path = _ensure_output_path(args.output or os.environ.get("GITHUB_OUTPUT"))
    with output_path.open("a", encoding="utf-8") as fh:
        fh.write(f"level={level}\n")

if __name__ == "__main__":
    main()
