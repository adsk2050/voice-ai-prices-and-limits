"""Every scraper, by provider. Add a new one here."""

from __future__ import annotations

from collections.abc import Callable

from voice_prices.rows import Scraped
from voice_prices.scrapers import (
    assemblyai,
    aws_polly,
    azure,
    cartesia,
    deepgram,
    elevenlabs,
    google,
    google_tts,
    inworld,
    openai,
    plivo,
    revai,
    rime,
    sarvam,
    smallestai,
    soniox,
    speechmatics,
    telnyx,
    twilio,
)


def _google() -> list[Scraped]:
    """Google's speech-to-text and text-to-speech pages."""
    return google.scrape() + google_tts.scrape()


SCRAPERS: dict[str, Callable[[], list[Scraped]]] = {
    "assemblyai": assemblyai.scrape,
    "aws": aws_polly.scrape,
    "azure": azure.scrape,
    "cartesia": cartesia.scrape,
    "deepgram": deepgram.scrape,
    "elevenlabs": elevenlabs.scrape,
    "google": _google,
    "inworld": inworld.scrape,
    "openai": openai.scrape,
    "plivo": plivo.scrape,
    "revai": revai.scrape,
    "rime": rime.scrape,
    "sarvam": sarvam.scrape,
    "smallestai": smallestai.scrape,
    "soniox": soniox.scrape,
    "speechmatics": speechmatics.scrape,
    "telnyx": telnyx.scrape,
    "twilio": twilio.scrape,
}
