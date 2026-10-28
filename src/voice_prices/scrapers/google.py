"""Google Cloud Speech-to-Text: price per minute, in US dollars.

Each SKU table is headed by its name (``Recognition (sku:...)``).
Each table has three price columns: the list price, then the Gemini
Enterprise Flexible Savings Plan for 1 year, then for 3 years. Each
column repeats its usage tiers.

The list price is the first tier that costs money. For V2 Recognition
that is ``0 minute to 500,000 minute``. For V1 and Medical it is
``60 minute and above``, because the first 60 minutes are free.
Dynamic batch has no tiers. The page names no plan fees or limits, and
it does not say whether tax is included.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://cloud.google.com/speech-to-text/pricing"

_PLANS = [
    "pay-as-you-go",
    slug("Gemini Enterprise Flexible Savings Plan - 1 Year"),
    slug("Gemini Enterprise Flexible Savings Plan - 3 Year"),
]
_PRICE = r"\$[0-9]+(?:\.[0-9]+)? / 1 minute, per 1 month / account"
_END = re.compile(r"sku:|\* Each|models include")

# (heading regex, product, mode, tier label before the price or None)
_BLOCKS: list[tuple[str, str, str, str | None]] = [
    (
        r"(?<!Batch )Recognition \(sku:[^)]+\) Standard",
        "recognition",
        "any",
        "0 minute to 500,000 minute",
    ),
    (
        r"Dynamic Batch Recognition \(sku:[^)]+\) Standard¹",
        "dynamic-batch-recognition",
        "batch",
        None,
    ),
    (
        r"Speech Recognition \(with data logging\) sku:\S+ Standard¹",
        "speech-recognition-with-data-logging",
        "any",
        "60 minute and above",
    ),
    (
        r"Speech Recognition \(without data logging\) sku:\S+ Standard¹",
        "speech-recognition-without-data-logging",
        "any",
        "60 minute and above",
    ),
    (
        r"Medical Dictation \(sku:[^)]+\) Medical²",
        "medical-dictation",
        "any",
        "60 minute and above",
    ),
    (
        r"Medical Conversation \(sku:[^)]+\) Medical²",
        "medical-conversation",
        "any",
        "60 minute and above",
    ),
]


def _segment(text: str, heading: str) -> str:
    """The text of one SKU table, from its heading to the next one."""
    match = re.search(heading, text)
    if match is None:
        raise PageChangedError(f"no table for {heading!r}")
    end = _END.search(text, match.end())
    return text[match.end() : end.start() if end else len(text)]


def _prices(segment: str, tier: str | None) -> list[re.Match[str]]:
    """One price match per plan, in the order of the plan columns."""
    prefix = rf"{re.escape(tier)} " if tier else ""
    found = list(re.finditer(rf"{prefix}(?P<price>{_PRICE})", segment))
    if len(found) != len(_PLANS):
        raise PageChangedError(
            f"expected {len(_PLANS)} prices for tier {tier!r}, "
            f"found {len(found)}"
        )
    return found


def parse(text: str) -> list[Scraped]:
    """The first paid tier of each STT SKU, one row per plan."""
    if "Price (USD)" not in text:
        raise PageChangedError("no USD price table")
    rows: list[Scraped] = []
    for heading, product, row_mode, tier in _BLOCKS:
        segment = _segment(text, heading)
        for plan, match in zip(_PLANS, _prices(segment, tier), strict=True):
            price = re.match(r"\$[0-9.]+", match.group("price"))
            if price is None:
                raise PageChangedError(f"no amount in {match.group(0)!r}")
            rows.append(
                Scraped(
                    category="stt",
                    provider="google",
                    product=product,
                    mode=row_mode,
                    plan=plan,
                    amount=amount(price.group(0)),
                    currency="USD",
                    per=1,
                    unit="minute",
                    source_url=PRICING_URL,
                    evidence=match.group(0),
                )
            )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
