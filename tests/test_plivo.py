from __future__ import annotations

from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError
from voice_prices.scrapers import plivo

FIXTURES = Path(__file__).parent / "fixtures"
PAGE = (FIXTURES / "plivo-voice-pricing-in.txt").read_text(encoding="utf-8")


def _by_id() -> dict[str, plivo.Scraped]:
    return {r.id: r for r in plivo.parse(PAGE)}


def test_domestic_and_webrtc_prices_per_direction() -> None:
    rows = _by_id()
    got = {i: r.amount for i, r in rows.items() if r.mode != "any"}
    assert got == {
        "plivo/domestic-calls/outbound/pay-as-you-go": "0.38",
        "plivo/domestic-calls/inbound/pay-as-you-go": "0.38",
        "plivo/browser-sdks-and-webrtc/outbound/pay-as-you-go": "0.25",
        "plivo/browser-sdks-and-webrtc/inbound/pay-as-you-go": "0.25",
    }
    row = rows["plivo/domestic-calls/outbound/pay-as-you-go"]
    assert (row.category, row.currency, row.per, row.unit) == (
        "telephony",
        "INR",
        1,
        "minute",
    )


def test_country_and_pulse_reach_the_row() -> None:
    row = _by_id()["plivo/domestic-calls/inbound/pay-as-you-go"]
    stored = row.to_row("2026-10-28")
    assert stored["country"] == "IN"
    assert stored["billing"] == {"increment_seconds": 30.0}
    assert stored["tax_included"] is None
    assert stored["limits"] is None


def test_a_changed_page_raises_instead_of_guessing() -> None:
    with pytest.raises(PageChangedError):
        plivo.parse(PAGE.replace("Domestic Calls", "Local Calls"))
    with pytest.raises(PageChangedError):
        plivo.parse(PAGE.replace("Pulse is 30 seconds.", ""))


def test_number_rental_and_add_ons() -> None:
    rows = {r.id: r for r in plivo.parse(PAGE)}
    rental = rows["plivo/phone-number/any/pay-as-you-go"]
    assert (rental.amount, rental.per, rental.unit) == ("200.00", 1, "month")
    asr = rows["plivo/automatic-speech-recognition/any/pay-as-you-go"]
    assert (asr.amount, asr.per, asr.unit) == ("1.70", 15, "second")
    assert rows["plivo/call-recording/any/pay-as-you-go"].amount == "0.00"
    assert rows["plivo/noise-cancellation/any/pay-as-you-go"].amount == "0.12"
