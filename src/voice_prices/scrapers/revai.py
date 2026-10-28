"""Rev AI: speech-to-text prices, pay as you go, in US dollars.

The pricing page has one "Pay As You Go" card listing each offering as
``<name> $a per <hour|minute>``. Each listing is followed by a billing note
such as ``Rounded up to the nearest second, 15 second minimum``. The note
is kept in the evidence; ``extra["billing"]`` is only for telephony rows.

The page gives one price per product and names no mode, so mode is "any".
Forced alignment, language identification, translation, sentiment,
summarization and topic extraction are not speech-to-text and are skipped.
Human transcription is a transcription service, so it is kept. Enterprise
pricing is volume-based with no stated price. The page does not say whether
tax is included, and it states no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.rev.ai/pricing"

_PLAN = "Pay As You Go"
_PRODUCTS = [
    "Reverb Transcription",
    "Reverb Foreign Language Transcription",
    "Whisper Large Transcription",
    "Human Transcription",
]
_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_UNITS = {"hour": "hour", "minute": "minute"}


def _offer(text: str, name: str) -> re.Match[str]:
    """The listing of one offering: its price, unit and billing note."""
    match = re.search(
        rf"{re.escape(name)} (?P<price>{_MONEY}) per (?P<unit>hour|minute)"
        r"(?:[^$]*?Rounded up to the nearest second, [0-9]+ second minimum)?",
        text,
    )
    if match is None:
        raise PageChangedError(f"no price for {name!r}")
    return match


def parse(text: str) -> list[Scraped]:
    """One pay-as-you-go STT price per transcription product."""
    if _PLAN not in text:
        raise PageChangedError(f"no {_PLAN!r} plan")
    rows: list[Scraped] = []
    for name in _PRODUCTS:
        match = _offer(text, name)
        product = slug(name.removesuffix(" Transcription"))
        rows.append(
            Scraped(
                category="stt",
                provider="revai",
                product=product,
                mode="any",
                plan=slug(_PLAN),
                amount=amount(match.group("price")),
                currency="USD",
                per=1,
                unit=_UNITS[match.group("unit")],
                source_url=PRICING_URL,
                evidence=match.group(0),
            )
        )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
