"""Speechmatics: STT per hour per model and mode, and TTS per characters.

The pricing page lists the models twice, under "Pre-recorded models" and
under "Real-time models", each as ``<model> <tagline> $a / hr``. A
promotion prints the old price before the current one (``Linden 1
Responsive $0.20 $0.15 / hr``); the current price is used and the
evidence shows both. Linden 1 is real-time only. Add-ons (translation,
summaries...) are not STT itself. The self-serve plan allows ``Concurrent
sessions (Real-time) 50``, stored on the real-time rows; files per
second for pre-recorded audio have no key here. The Text to Speech block
reads ``$a per 1,000 characters``. The page says nothing about tax.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount

PRICING_URL = "https://www.speechmatics.com/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
# (name on the page, product id, modes it is sold in)
_MODELS = [
    ("Melia 1", "melia-1", ("batch", "real-time")),
    ("Enhanced", "enhanced", ("batch", "real-time")),
    ("Oak 1", "oak-1-medical", ("batch", "real-time")),
    ("Linden 1", "linden-1", ("real-time",)),
    ("Standard", "standard", ("batch", "real-time")),
]
# mode -> (section start, section end)
_SECTIONS = {
    "batch": ("Pre-recorded models", "Real-time models"),
    "real-time": ("Real-time models", "How credits work"),
}
_LIMIT = re.compile(r"Concurrent sessions \(Real-time\) (?P<n>[0-9]+)")
_TTS = re.compile(
    rf"Text to Speech .{{0,200}}?(?P<price>{_MONEY}) per "
    r"(?P<per>[0-9][0-9,]*) characters"
)


def _section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    if begin < 0:
        raise PageChangedError(f"no section starting {start!r}")
    stop = text.find(end, begin + len(start))
    if stop < 0:
        raise PageChangedError(f"no end of section {start!r}")
    return text[begin + len(start) : stop]


def _realtime_limits(text: str) -> dict[str, object]:
    match = _LIMIT.search(text)
    if match is None:
        raise PageChangedError("no real-time concurrency limit")
    return {
        "concurrent": int(match.group("n")),
        "source_url": PRICING_URL,
        "evidence": match.group(0),
    }


def _stt(text: str) -> list[Scraped]:
    """One row per model and mode, per hour."""
    limits = _realtime_limits(text)
    rows: list[Scraped] = []
    for mode, (start, end) in _SECTIONS.items():
        section = _section(text, start, end)
        for name, product, modes in _MODELS:
            if mode not in modes:
                continue
            match = re.search(
                rf"{re.escape(name)} [^$]{{0,40}}?(?:{_MONEY} )?"
                rf"(?P<price>{_MONEY}) / hr",
                section,
            )
            if match is None:
                raise PageChangedError(f"no {mode} price for {name!r}")
            rows.append(
                Scraped(
                    category="stt",
                    provider="speechmatics",
                    product=product,
                    mode=mode,
                    plan="pay-as-you-go",
                    amount=amount(match.group("price")),
                    currency="USD",
                    per=1,
                    unit="hour",
                    source_url=PRICING_URL,
                    evidence=match.group(0),
                    limits=limits if mode == "real-time" else None,
                )
            )
    return rows


def _tts(text: str) -> Scraped:
    """The single text-to-speech price."""
    match = _TTS.search(text)
    if match is None:
        raise PageChangedError("no text to speech price")
    return Scraped(
        category="tts",
        provider="speechmatics",
        product="text-to-speech",
        mode="any",
        plan="pay-as-you-go",
        amount=amount(match.group("price")),
        currency="USD",
        per=int(match.group("per").replace(",", "")),
        unit="character",
        source_url=PRICING_URL,
        evidence=match.group(0),
    )


def parse(text: str) -> list[Scraped]:
    """Pre-recorded STT prices per model and the TTS price."""
    if not text:
        raise PageChangedError("empty page")
    return _stt(text) + [_tts(text)]


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
