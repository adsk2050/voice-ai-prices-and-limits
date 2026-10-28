"""Shared checks for scrapers that read one page: each parses its saved
page excerpt, every price appears in its evidence, and every evidence
string is on the page."""

from __future__ import annotations

import importlib
from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError

FIXTURES = Path(__file__).parent / "fixtures"
MODULES = [
    "assemblyai",
    "aws_polly",
    "cartesia",
    "deepgram",
    "elevenlabs",
    "google",
    "google_tts",
    "inworld",
    "openai",
    "revai",
    "rime",
    "soniox",
    "speechmatics",
    "telnyx",
    "twilio",
]


@pytest.mark.parametrize("name", MODULES)
def test_parses_its_page(name: str) -> None:
    module = importlib.import_module(f"voice_prices.scrapers.{name}")
    text = (FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
    rows = module.parse(text)
    assert rows
    assert len({r.id for r in rows}) == len(rows)
    for row in rows:
        row.to_row(since="2026-10-28")
        assert row.evidence in text
        printed = row.amount.rstrip("0").rstrip(".") or "0"
        assert printed in row.evidence.replace(",", "")


@pytest.mark.parametrize("name", MODULES)
def test_an_empty_page_raises(name: str) -> None:
    module = importlib.import_module(f"voice_prices.scrapers.{name}")
    with pytest.raises(PageChangedError):
        module.parse("")
