"""AssemblyAI: speech-to-text models and TTS-1, pay as you go, in dollars.

The pricing page has one card per API (async, realtime, sync, dictation,
text-to-speech). Each model reads ``<model> [New] <description> $x /hr``
or ``$x /1M chars`` under the "Pay as you go" column. The "Custom" plan
says "Contact us" and has no price. Add-on features are surcharges on a
model, so they are not read as products. The page says nothing about tax
and states no numeric limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://www.assemblyai.com/pricing"

_UNITS = {"hr": (1, "hour"), "1M chars": (1_000_000, "character")}

# (category, model name, first words of its description, page's mode word)
_MODELS = [
    ("stt", "Universal-3.5 Pro", "The most accurate async", "batch"),
    ("stt", "Universal-2", "Our highly accurate", "batch"),
    ("stt", "Universal-3.6 Pro Realtime", "The most accurate", "realtime"),
    ("stt", "Universal-Streaming", "High-quality realtime", "realtime"),
    (
        "stt",
        "Universal-Streaming Multilingual",
        "Multilingual transcription",
        "realtime",
    ),
    # Sync and Dictation take a recorded clip per request: pre-recorded.
    ("stt", "Sync API", "Universal-3.5 Pro accuracy", "pre-recorded"),
    ("stt", "Dictation API", "Finished text", "pre-recorded"),
    # One TTS price over both WebSocket and HTTP.
    ("tts", "AssemblyAI-TTS-1", "Streaming text-to-speech", "any"),
]


def _pattern(name: str, lead: str) -> re.Pattern[str]:
    """``<name> [New] <lead>...`` up to the first price after it."""
    return re.compile(
        rf"{re.escape(name)} (?:New )?{re.escape(lead)}[^$]*? "
        r"(?P<price>\$[0-9][0-9,]*(?:\.[0-9]+)?) /(?P<unit>hr|1M chars)"
    )


def parse(text: str) -> list[Scraped]:
    """One pay-as-you-go row per STT and TTS model."""
    if "Pay as you go" not in text:
        raise PageChangedError("no 'Pay as you go' column")
    rows: list[Scraped] = []
    for category, name, lead, word in _MODELS:
        match = _pattern(name, lead).search(text)
        if match is None:
            raise PageChangedError(f"no price for {name!r}")
        per, unit = _UNITS[match.group("unit")]
        rows.append(
            Scraped(
                category=category,
                provider="assemblyai",
                product=slug(name),
                mode=mode(word),
                plan="pay-as-you-go",
                amount=amount(match.group("price")),
                currency="USD",
                per=per,
                unit=unit,
                source_url=PRICING_URL,
                evidence=match.group(0),
            )
        )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
