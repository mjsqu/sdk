"""General helper functions, helper classes, and decorators."""

from __future__ import annotations

import json
import typing as t
from pathlib import Path

import pendulum

if t.TYPE_CHECKING:
    from singer_sdk._python_types import _FilePath


def read_json_file(path: _FilePath) -> dict[str, t.Any]:
    """Read json file, throwing an error if missing."""
    if not path:
        raise RuntimeError("Could not open file. Filepath not provided.")

    path_obj = Path(path)

    if not path_obj.exists():
        msg = f"File at '{path!r}' was not found."
        for template in [f"{path!r}.template"]:
            if Path(template).exists():
                msg += f"\nFor more info, please see the sample template at: {template}"
        raise FileExistsError(msg)

    return t.cast(dict, json.loads(path_obj.read_text()))


def utc_now() -> pendulum.DateTime:
    """Return current time in UTC."""
    return pendulum.now(tz="UTC")
