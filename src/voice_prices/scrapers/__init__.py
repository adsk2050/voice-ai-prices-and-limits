"""Every scraper, by provider. Add a new one here."""

from __future__ import annotations

from collections.abc import Callable

from voice_prices.rows import Scraped
from voice_prices.scrapers import (
    assemblyai,
    aws_polly,
    aws_transcribe,
    azure,
    bland,
    bolna,
    cartesia,
    deepgram,
    elevenlabs,
    gladia,
    google,
    google_tts,
    inworld,
    knowlarity,
    openai,
    plivo,
    retell,
    revai,
    rime,
    sarvam,
    smallestai,
    soniox,
    speechmatics,
    telnyx,
    twilio,
    vapi,
)


def _aws() -> list[Scraped]:
    """AWS Transcribe and Polly pages."""
    return aws_transcribe.scrape() + aws_polly.scrape()


def _google() -> list[Scraped]:
    """Google's speech-to-text and text-to-speech pages."""
    return google.scrape() + google_tts.scrape()


SCRAPERS: dict[str, Callable[[], list[Scraped]]] = {
    "assemblyai": assemblyai.scrape,
    "aws": _aws,
    "azure": azure.scrape,
    "bland": bland.scrape,
    "bolna": bolna.scrape,
    "cartesia": cartesia.scrape,
    "deepgram": deepgram.scrape,
    "elevenlabs": elevenlabs.scrape,
    "gladia": gladia.scrape,
    "google": _google,
    "inworld": inworld.scrape,
    "knowlarity": knowlarity.scrape,
    "openai": openai.scrape,
    "plivo": plivo.scrape,
    "retell": retell.scrape,
    "revai": revai.scrape,
    "rime": rime.scrape,
    "sarvam": sarvam.scrape,
    "smallestai": smallestai.scrape,
    "soniox": soniox.scrape,
    "speechmatics": speechmatics.scrape,
    "telnyx": telnyx.scrape,
    "twilio": twilio.scrape,
    "vapi": vapi.scrape,
}
