"""Soniox speech-to-text and text-to-speech prices, in US dollars.

The pricing page has one token table per API. The "Speech-to-Text API
pricing" table has the header ``Async (file) Real-time (streaming)`` and
rows ``<token type> <description> $a per 1M tokens $b per 1M tokens``, with
the async price first. The "Text-to-Speech API pricing" table is real-time
(streaming) only, one price per row. The FAQ gives the flat hourly STT rate
(``Speech-to-Text is $0.10/hour for async ... and $0.12/hour for real-time``).
The TTS hourly figure is only an estimate ("about"), so it is skipped. The
page states no plans, no tax terms and no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://soniox.com/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_PER_1M = r"per 1M tokens"
_STT_HEAD = "Speech-to-Text API pricing"
_TTS_HEAD = "Text-to-Speech API pricing"
_STT_COLS = "Async (file) Real-time (streaming)"
_TOKENS = r"(?P<name>Input audio tokens|Input text tokens|Output text tokens"
_TOKENS += r"|Output audio tokens)"
_STT_ROW = re.compile(
    rf"{_TOKENS} [^$]*?(?P<a>{_MONEY}) {_PER_1M} (?P<b>{_MONEY}) {_PER_1M}"
)
_TTS_ROW = re.compile(rf"{_TOKENS} [^$]*?(?P<a>{_MONEY}) {_PER_1M}")
_HOURLY = re.compile(
    rf"Speech-to-Text is (?P<a>{_MONEY})/hour for async \(file uploads\) "
    rf"and (?P<b>{_MONEY})/hour for real-time \(streaming\)"
)


def _section(text: str, start: str, end: str) -> str:
    """The text between two headings."""
    i = text.find(start)
    j = text.find(end, i + 1) if i >= 0 else -1
    if i < 0 or j < 0:
        raise PageChangedError(f"no section {start!r}")
    return text[i + len(start) : j]


def _row(
    category: str,
    product: str,
    mode_: str,
    price: str,
    per: int,
    unit: str,
    evidence: str,
) -> Scraped:
    return Scraped(
        category=category,
        provider="soniox",
        product=product,
        mode=mode_,
        plan="pay-as-you-go",
        amount=amount(price),
        currency="USD",
        per=per,
        unit=unit,
        source_url=PRICING_URL,
        evidence=evidence,
    )


def parse(text: str) -> list[Scraped]:
    """STT token and hourly prices per mode, and TTS token prices."""
    rows: list[Scraped] = []
    stt = _section(text, _STT_HEAD, _TTS_HEAD)
    if _STT_COLS not in stt:
        raise PageChangedError("no STT column header")
    for match in _STT_ROW.finditer(stt):
        product = "stt-" + slug(match.group("name"))
        for group, word in (("a", "batch"), ("b", "real-time")):
            rows.append(
                _row(
                    "stt",
                    product,
                    mode(word),
                    match.group(group),
                    1000000,
                    "token",
                    match.group(0),
                )
            )
    if len(rows) != 6:
        raise PageChangedError(f"expected 3 STT token rows, got {len(rows)}")
    hourly = _HOURLY.search(text)
    if hourly is None:
        raise PageChangedError("no hourly STT rate")
    for group, word in (("a", "batch"), ("b", "real-time")):
        rows.append(
            _row(
                "stt",
                "stt",
                mode(word),
                hourly.group(group),
                1,
                "hour",
                hourly.group(0),
            )
        )
    tts = _section(text, _TTS_HEAD, "How the pricing works")
    if "Real-time (streaming)" not in tts:
        raise PageChangedError("no TTS mode header")
    found = 0
    for match in _TTS_ROW.finditer(tts):
        rows.append(
            _row(
                "tts",
                "tts-" + slug(match.group("name")),
                mode("real-time"),
                match.group("a"),
                1000000,
                "token",
                match.group(0),
            )
        )
        found += 1
    if found != 2:
        raise PageChangedError(f"expected 2 TTS token rows, got {found}")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
