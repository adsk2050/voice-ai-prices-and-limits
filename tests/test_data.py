"""Every row in data/*.json fits the schema and has a unique id."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads(
    (ROOT / "schema" / "row.schema.json").read_text(encoding="utf-8")
)
FILES = [ROOT / "data" / f"{c}.json" for c in ("stt", "tts", "telephony")]


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_rows_fit_the_schema(path: Path) -> None:
    rows = json.loads(path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(SCHEMA)
    for row in rows:
        validator.validate(row)
        assert row["category"] == path.stem


@pytest.mark.parametrize("path", FILES, ids=lambda p: p.name)
def test_ids_are_unique(path: Path) -> None:
    ids = [r["id"] for r in json.loads(path.read_text(encoding="utf-8"))]
    assert len(ids) == len(set(ids))
