"""Speechmatics: STT per hour for pre-recorded models, and TTS per characters.

The pricing page lists the pre-recorded models under "Pre-recorded
models", each as ``<model> $a / hr``, up to the "Model-training discount"
line. Real-time rates are not printed in the page text, so they are
skipped. Add-ons (translation, summaries...) are not STT itself. The Text
to Speech block reads ``$a per 1,000 characters``. The page says nothing
about tax, and the limits it states are for real-time sessions or files
per second, which have no row or key here.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.speechmatics.com/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_MODELS = ["Melia 1", "Enhanced", "Oak 1 Medical", "Standard"]
_START = "Pre-recorded models"
_END = "Model-training discount"
_TTS = re.compile(
    rf"Text to Speech .{{0,200}}?(?P<price>{_MONEY}) per "
    r"(?P<per>[0-9][0-9,]*) characters"
)


def _section(text: str) -> str:
    """The text of the pre-recorded models list."""
    start = text.find(_START)
    if start < 0:
        raise PageChangedError("no pre-recorded models section")
    end = text.find(_END, start)
    if end < 0:
        raise PageChangedError("no end of pre-recorded models section")
    return text[start + len(_START) : end]


def _stt(text: str) -> list[Scraped]:
    """One batch row per pre-recorded model, per hour."""
    section = _section(text)
    rows: list[Scraped] = []
    for model in _MODELS:
        match = re.search(
            rf"{re.escape(model)} (?P<price>{_MONEY}) / hr", section
        )
        if match is None:
            raise PageChangedError(f"no price for {model!r}")
        rows.append(
            Scraped(
                category="stt",
                provider="speechmatics",
                product=slug(model),
                mode="batch",
                plan="pay-as-you-go",
                amount=amount(match.group("price")),
                currency="USD",
                per=1,
                unit="hour",
                source_url=PRICING_URL,
                evidence=match.group(0),
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
