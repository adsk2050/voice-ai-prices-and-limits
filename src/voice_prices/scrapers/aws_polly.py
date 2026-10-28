"""Amazon Polly text-to-speech prices, per million characters, in dollars.

The pricing page states one sentence per voice type: ``Amazon Polly's
<Type> voices are priced at $x per 1 million characters``. The first block
is the standard (commercial) regions; a later "AWS GovCloud (US) Pricing
Details" block repeats Standard and Neural at GovCloud prices, read here as
a separate plan. The page states no tax treatment and no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://aws.amazon.com/polly/pricing/"

_GOVCLOUD = "AWS GovCloud (US) Pricing Details"
_PRICE = re.compile(
    r"Amazon Polly.s (?P<voice>Standard|Neural|Long-Form|Generative)"
    r"(?: TTS)? voices are priced at (?P<price>\$[0-9][0-9,]*(?:\.[0-9]+)?)"
    r" per (?P<per>[0-9]+) million characters"
)

# (plan, voice types the block must price)
_BLOCKS = [
    ("pay-as-you-go", ["Standard", "Neural", "Long-Form", "Generative"]),
    ("govcloud-us", ["Standard", "Neural"]),
]


def _blocks(text: str) -> list[str]:
    """The commercial text and the GovCloud text."""
    split = text.find(_GOVCLOUD)
    if split < 0:
        raise PageChangedError("no GovCloud pricing section")
    return [text[:split], text[split:]]


def parse(text: str) -> list[Scraped]:
    """One TTS price per voice type and plan."""
    rows: list[Scraped] = []
    for (plan, voices), block in zip(_BLOCKS, _blocks(text), strict=True):
        found = {m.group("voice"): m for m in _PRICE.finditer(block)}
        for voice in voices:
            match = found.get(voice)
            if match is None:
                raise PageChangedError(f"no {voice!r} price for {plan!r}")
            rows.append(
                Scraped(
                    category="tts",
                    provider="aws",
                    product=slug(f"{voice} voices"),
                    mode="any",
                    plan=plan,
                    amount=amount(match.group("price")),
                    currency="USD",
                    per=int(match.group("per")) * 1_000_000,
                    unit="character",
                    source_url=PRICING_URL,
                    evidence=match.group(0),
                )
            )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
