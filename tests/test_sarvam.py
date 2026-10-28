from __future__ import annotations

from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError
from voice_prices.scrapers import sarvam

FIXTURES = Path(__file__).parent / "fixtures"
PRICING = (FIXTURES / "sarvam-api-pricing.txt").read_text(encoding="utf-8")
DOCS = (FIXTURES / "sarvam-docs-pricing.txt").read_text(encoding="utf-8")


def _by_id() -> dict[str, sarvam.Scraped]:
    return {r.id: r for r in sarvam.parse(PRICING, DOCS)}


def test_bulbul_v4_flash_per_plan() -> None:
    rows = _by_id()
    got = {
        plan: rows[f"sarvam/bulbul-v4-flash/real-time/{plan}"].amount
        for plan in ("pay-as-you-go", "pro", "growth", "business")
    }
    assert got == {
        "pay-as-you-go": "1.00",
        "pro": "0.925",
        "growth": "0.85",
        "business": "0.80",
    }
    row = rows["sarvam/bulbul-v4-flash/real-time/pay-as-you-go"]
    assert (row.currency, row.per, row.unit) == ("INR", 1000, "character")
    assert row.category == "tts"


def test_stt_rows_name_the_product_and_skip_language_id() -> None:
    rows = _by_id()
    row = rows["sarvam/saaras/real-time/pay-as-you-go"]
    assert (row.category, row.amount, row.unit) == ("stt", "0.49", "minute")
    assert "sarvam/saaras/batch-with-diarization/business" in rows
    assert not any("language-identification" in r for r in rows)


def test_plan_fee_and_tax() -> None:
    row = _by_id()["sarvam/bulbul-v3/real-time/business"]
    assert row.plan_fee == {
        "amount": "199999",
        "currency": "INR",
        "period": "month",
    }
    assert row.tax_included is False


def test_a_changed_page_raises_instead_of_guessing() -> None:
    with pytest.raises(PageChangedError):
        sarvam.parse(PRICING.replace("Text to speech Service", "TTS"), DOCS)
