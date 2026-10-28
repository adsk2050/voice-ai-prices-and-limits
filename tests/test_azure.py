from __future__ import annotations

import json
from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError
from voice_prices.scrapers import azure

ITEMS = json.loads(
    (Path(__file__).parent / "fixtures" / "azure-retail-prices.json").read_text(
        encoding="utf-8"
    )
)


def test_main_meters() -> None:
    rows = {r.id: r for r in azure.parse(ITEMS)}
    stt = rows["azure/speech-to-text/real-time/pay-as-you-go"]
    assert (stt.amount, stt.currency, stt.per, stt.unit) == (
        "1",
        "USD",
        1,
        "hour",
    )
    tts = rows["azure/neural/any/pay-as-you-go"]
    assert (tts.amount, tts.per, tts.unit) == ("15", 1_000_000, "character")
    for row in rows.values():
        row.to_row(since="2026-10-28")


def test_a_missing_meter_raises() -> None:
    with pytest.raises(PageChangedError):
        azure.parse(ITEMS[1:])
