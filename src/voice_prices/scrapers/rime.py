"""Rime: Mist v3 and Coda v2 TTS and Rime STT, pay-as-you-go, in dollars.

The "Pay as you go" plan card lists each model as ``<model> <tagline>
$a / min``. The STT price is followed by ``from Nov 20 Free until Nov
19``: the printed price applies from November 20, and STT is free until
then. The same card states the concurrency limits (``15 concurrent Mist,
10 Coda, 10 STT``). TTS is also quoted per 1K characters further down. This
module uses the per-minute card price. Enterprise is "Volume rates" with no
number, so it is skipped. The page does not say whether tax is included.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount

PRICING_URL = "https://www.rime.ai/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_CARD = "Pay as you go For new production users"

# (product, category, anchor before the price, anchor after it, limit key)
_MODELS = [
    ("mist-v3", "tts", r"Mist v3 Text to speech, lowest latency", "", "mist"),
    ("coda-v2", "tts", r"Coda v2 Text to speech, most natural", "", "coda"),
    (
        "rime-stt",
        "stt",
        r"Rime STT",
        r" from Nov 20 Free until Nov 19",
        "stt",
    ),
]

_LIMITS = re.compile(
    r"(?P<mist>[0-9]+) concurrent Mist, (?P<coda>[0-9]+) Coda, "
    r"(?P<stt>[0-9]+) STT"
)


def _card(text: str) -> str:
    """The text of the pay-as-you-go plan card, up to the Enterprise card."""
    start = text.find(_CARD)
    if start < 0:
        raise PageChangedError("no pay-as-you-go plan card")
    end = text.find("Enterprise", start)
    return text[start : end if end > 0 else len(text)]


def parse(text: str) -> list[Scraped]:
    """One per-minute pay-as-you-go price per model, with its concurrency."""
    card = _card(text)
    limits = _LIMITS.search(card)
    if limits is None:
        raise PageChangedError("no concurrency limits on the plan card")
    rows: list[Scraped] = []
    for product, category, before, after, key in _MODELS:
        match = re.search(rf"{before} (?P<price>{_MONEY}) / min{after}", card)
        if match is None:
            raise PageChangedError(f"no price for {product!r}")
        rows.append(
            Scraped(
                category=category,
                provider="rime",
                product=product,
                mode="any",
                plan="pay-as-you-go",
                amount=amount(match.group("price")),
                currency="USD",
                per=1,
                unit="minute",
                source_url=PRICING_URL,
                evidence=match.group(0),
                limits={
                    "concurrent": int(limits.group(key)),
                    "source_url": PRICING_URL,
                    "evidence": limits.group(0),
                },
            )
        )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
