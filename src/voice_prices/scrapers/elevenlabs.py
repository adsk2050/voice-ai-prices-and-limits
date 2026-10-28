"""ElevenLabs API: TTS per 1K characters and STT per hour, in US dollars.

The API pricing page has one card per model, reading ``<model> <category>
[New] $<price> Price per <unit>``. TTS cards are priced per 1K characters,
STT cards per hour. Scribe v2 Realtime is the real-time STT; other STT and
all TTS cards give one price for every mode. Speech to speech, agents,
music, audio processing and dubbing cards are ignored. The page says
"Prices exclude all taxes, levies and duties." It states no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://elevenlabs.io/pricing/api"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_CATEGORIES = {"Text to Speech": "tts", "Speech to Text": "stt"}
_UNITS = {"1K characters": (1000, "character"), "hour": (1, "hour")}

# Every card the page must still have: (model name, card category).
_EXPECTED = [
    ("v4", "Text to Speech"),
    ("v4 Turbo", "Text to Speech"),
    ("v3", "Text to Speech"),
    ("v3 Conversational", "Text to Speech"),
    ("v2 Multilingual", "Text to Speech"),
    ("Flash / Turbo", "Text to Speech"),
    ("Scribe v2", "Speech to Text"),
    ("Scribe v2 Medical", "Speech to Text"),
    ("Scribe v2 Realtime", "Speech to Text"),
]


def _card(name: str, category: str) -> re.Pattern[str]:
    """The pattern of one model's card, anchored on its exact name."""
    return re.compile(
        rf"(?<![A-Za-z0-9]){re.escape(name)} {category}(?: New)? "
        rf"(?P<price>{_MONEY}) Price per (?P<unit>1K characters|hour)"
    )


def _mode(name: str) -> str:
    """The card's mode: a realtime model is real-time, others any mode."""
    last = name.split()[-1]
    return mode(last) if slug(last) == "realtime" else "any"


def parse(text: str) -> list[Scraped]:
    """One row per TTS and STT model card."""
    if "Prices exclude all taxes" in text:
        tax_included: bool | None = False
    elif "Prices include all taxes" in text:
        tax_included = True
    else:
        tax_included = None
    rows: list[Scraped] = []
    missing: list[str] = []
    for name, category in _EXPECTED:
        match = _card(name, category).search(text)
        if match is None:
            missing.append(name)
            continue
        per, unit = _UNITS[match.group("unit")]
        rows.append(
            Scraped(
                category=_CATEGORIES[category],
                provider="elevenlabs",
                product=slug(name),
                mode=_mode(name),
                plan="pay-as-you-go",
                amount=amount(match.group("price")),
                currency="USD",
                per=per,
                unit=unit,
                source_url=PRICING_URL,
                evidence=match.group(0),
                tax_included=tax_included,
            )
        )
    if missing:
        raise PageChangedError(f"no price card for {missing!r}")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
