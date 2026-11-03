from __future__ import annotations

from pathlib import Path

import pytest

from voice_prices.rows import PageChangedError
from voice_prices.scrapers import deepgram

HTML = (Path(__file__).parent / "fixtures" / "deepgram.html").read_text(
    encoding="utf-8"
)


def test_stt_and_tts_rows() -> None:
    rows = {r.id: r for r in deepgram.parse(HTML)}
    assert len(rows) == 20
    stream = rows["deepgram/nova-3-monolingual/streaming/pay-as-you-go"]
    assert (stream.amount, stream.per, stream.unit) == ("0.0077", 1, "minute")
    assert stream.limits["concurrent"] == 150
    batch = rows["deepgram/nova-3-monolingual/batch/growth"]
    assert (batch.amount, batch.limits) == ("0.0036", None)
    assert (
        rows["deepgram/flux-english/streaming/growth"].limits["concurrent"]
        == 225
    )
    tts = rows["deepgram/aura-2/any/growth"]
    assert (tts.amount, tts.per, tts.unit) == ("0.027", 1000, "character")
    assert not any("redaction" in i or "agent" in i for i in rows)
    for row in rows.values():
        row.to_row(since="2026-10-28")
        assert row.amount.rstrip("0").rstrip(".") in row.evidence


def test_no_catalog_raises() -> None:
    with pytest.raises(PageChangedError):
        deepgram.parse(HTML.replace("Rates by product", "Something else"))


def test_an_empty_page_raises() -> None:
    with pytest.raises(PageChangedError):
        deepgram.parse("")
