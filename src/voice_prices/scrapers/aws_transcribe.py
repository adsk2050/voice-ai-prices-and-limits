"""Amazon Transcribe (AWS) speech-to-text prices, in US dollars.

The excerpt does not include the pricing tables. Prices come from the
worked examples for US East (N. Virginia):

- standard streaming: ``Streaming transcription is priced at $0.01 per
  minute``
- standard batch: ``Batch transcription is priced at $0.006 per minute``
- content redaction and Call Analytics: three tier sentences each,
  ``Tier 1 (T1) ... pricing of $x applies to the first 250,000 minutes``
  followed by the "next ..." tiers.

The streaming and batch examples print one price with no tier, so those
rows carry no volume. Generative call summarization is an LLM feature and
is skipped. Medical prices appear only as example totals with no per-unit
price, so they are skipped. The page does not say whether tax is included,
and it states no limits.
"""

from __future__ import annotations

import re
from typing import Any

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://aws.amazon.com/transcribe/pricing/"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_NUM = r"[0-9][0-9,]*"

_FLAT = re.compile(
    rf"(?P<word>Streaming|Batch) transcription is priced at "
    rf"(?P<price>{_MONEY}) per minute"
)

# (product name, label used in the tier sentences)
_TIERED = [("Content redaction", "content redaction "), ("Call Analytics", "")]


class _Minutes(int):
    """An int that formats as plain digits, so ``:g`` in ids never gives
    ``1e+06`` (which the id pattern rejects)."""

    def __format__(self, spec: str) -> str:
        return str(int(self))


def _volume(low: int, high: int) -> dict[str, Any]:
    return {"min": _Minutes(low), "max": _Minutes(high), "unit": "minute"}


def _row(
    product: str,
    word: str,
    price: str,
    evidence: str,
    volume: dict[str, Any] | None,
) -> Scraped:
    return Scraped(
        category="stt",
        provider="aws",
        product=slug(product),
        mode=word,
        plan="pay-as-you-go",
        amount=amount(price),
        currency="USD",
        per=1,
        unit="minute",
        source_url=PRICING_URL,
        evidence=evidence,
        volume=volume,
    )


def _tiers(text: str, product: str, label: str) -> list[Scraped]:
    """Three tiers of one product, each read from its own sentence."""
    label = re.escape(label)
    first = re.search(
        rf"Tier 1 \(T1\) {label}pricing of (?P<price>{_MONEY})(?:/minute)? "
        rf"applies to the first (?P<n>{_NUM}) minutes",
        text,
    )
    if first is None:
        raise PageChangedError(f"no tier 1 price for {product!r}")
    high = int(first.group("n").replace(",", ""))
    rows = [
        _row(
            product,
            "any",
            first.group("price"),
            first.group(0),
            _volume(0, high),
        )
    ]
    pos = first.end()
    for tier in (2, 3):
        match = re.compile(
            rf"Tier {tier} {label}pricing of (?P<price>{_MONEY})(?:/minute)?"
            rf" \([^)]*\) applies to the next (?P<n>{_NUM}) minutes"
        ).search(text, pos)
        if match is None:
            raise PageChangedError(f"no tier {tier} price for {product!r}")
        low = high
        high = low + int(match.group("n").replace(",", ""))
        rows.append(
            _row(
                product,
                "any",
                match.group("price"),
                match.group(0),
                _volume(low, high),
            )
        )
        pos = match.end()
    return rows


def parse(text: str) -> list[Scraped]:
    """Standard streaming and batch, content redaction and Call Analytics."""
    rows: list[Scraped] = []
    found = {m.group("word"): m for m in _FLAT.finditer(text)}
    for word in ("Streaming", "Batch"):
        match = found.get(word)
        if match is None:
            raise PageChangedError(f"no {word.lower()} transcription price")
        rows.append(
            _row(
                "transcribe",
                mode(word),
                match.group("price"),
                match.group(0),
                None,
            )
        )
    for product, label in _TIERED:
        rows.extend(_tiers(text, product, label))
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
