from __future__ import annotations

from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError
from voice_prices.scrapers import smallestai

FIXTURES = Path(__file__).parent / "fixtures"
PAGE = (FIXTURES / "smallestai-models-pricing.txt").read_text(encoding="utf-8")


def _by_id() -> dict[str, smallestai.Scraped]:
    return {r.id: r for r in smallestai.parse(PAGE)}


def test_tts_prices_per_10k_characters() -> None:
    rows = _by_id()
    row = rows["smallestai/lightning-v3.1/any/pay-as-you-go"]
    assert (row.category, row.amount, row.currency) == ("tts", "0.175", "USD")
    assert (row.per, row.unit) == (10000, "character")
    pro = rows["smallestai/lightning-v3.1-pro/any/pay-as-you-go"]
    assert pro.amount == "0.195"


def test_stt_prices_per_minute() -> None:
    rows = _by_id()
    got = {
        r.id.split("/", 1)[1]: r.amount
        for r in rows.values()
        if r.category == "stt"
    }
    assert got == {
        "pulse/batch/pay-as-you-go": "0.003",
        "pulse/real-time/pay-as-you-go": "0.004",
        "pulse-pro/batch/pay-as-you-go": "0.0035",
    }


def test_limits_and_unstated_fee_and_tax() -> None:
    rows = _by_id()
    tts = rows["smallestai/lightning-v3.1/any/pay-as-you-go"]
    assert tts.limits is not None
    assert tts.limits["concurrent"] == 15
    assert tts.limits["requests_per_minute"] == 100
    stt = rows["smallestai/pulse/real-time/pay-as-you-go"]
    assert stt.limits is not None
    assert stt.limits["concurrent"] == 100
    assert tts.plan_fee is None
    assert tts.tax_included is None


def test_rows_fit_the_schema() -> None:
    for row in smallestai.parse(PAGE):
        row.to_row("2026-10-28")


def test_a_changed_page_raises_instead_of_guessing() -> None:
    with pytest.raises(PageChangedError):
        smallestai.parse(PAGE.replace("/10K characters", "/10K chars"))
    with pytest.raises(PageChangedError):
        smallestai.parse(PAGE.replace("RPM for TTS APIs", "Rate"))
