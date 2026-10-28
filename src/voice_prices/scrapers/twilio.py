"""Twilio Programmable Voice, United States, pay-as-you-go, in US dollars.

The page holds per-minute call prices for each number type ("To make
calls" first, then "To receive calls"), BYOC trunking, phone number rental
per month, and an "Intelligent service pricing" list. That list has
transcription (batch and real-time), call recording, media streams and
premium text-to-speech priced per 100 characters. The page states a
default of 1 call per second. It gives no billing pulse and does not say
whether tax is included.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://www.twilio.com/en-us/voice/pricing/us"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_CALLS_HEADER = "Number type To make calls To receive calls"
_ROUTES = ["Local calls", "Toll-free calls", "Browser/app", "SIP interface"]
_TTS = ["Standard", "Neural", "Generative"]
_EXTRA = {"country": "US"}


def _find(pattern: str, text: str, what: str) -> re.Match[str]:
    match = re.search(pattern, text)
    if match is None:
        raise PageChangedError(f"no {what}")
    return match


def _row(
    category: str,
    product: str,
    mode_: str,
    match: re.Match[str],
    group: str,
    per: int,
    unit: str,
    limits: dict[str, object] | None = None,
) -> Scraped:
    return Scraped(
        category=category,
        provider="twilio",
        product=product,
        mode=mode_,
        plan="pay-as-you-go",
        amount=amount(match.group(group)),
        currency="USD",
        per=per,
        unit=unit,
        source_url=PRICING_URL,
        evidence=match.group(0),
        limits=limits,
        extra=dict(_EXTRA) if category == "telephony" else {},
    )


def _calls(text: str, limits: dict[str, object] | None) -> list[Scraped]:
    """Outbound and inbound per-minute prices per number type and BYOC."""
    start = text.find(_CALLS_HEADER)
    end = text.find("In depth pricing", start)
    if start < 0 or end < 0:
        raise PageChangedError("no calls table")
    section = text[start:end]
    found = [(route, section, "calls table") for route in _ROUTES] + [
        ("BYOC trunking", text, "BYOC table")
    ]
    rows: list[Scraped] = []
    for route, where, what in found:
        match = _find(
            rf"{re.escape(route)} (?P<out>{_MONEY}) / min "
            rf"(?P<in>{_MONEY}) / min",
            where,
            f"{route!r} in the {what}",
        )
        for word, group in (("outbound", "out"), ("inbound", "in")):
            rows.append(
                _row(
                    "telephony",
                    slug(route),
                    mode(word),
                    match,
                    group,
                    1,
                    "minute",
                    limits,
                )
            )
    return rows


def _fixed(text: str) -> list[Scraped]:
    """Number rental and per-minute voice add-ons."""
    numbers = text.find("Phone number pricing")
    if numbers < 0:
        raise PageChangedError("no phone number pricing section")
    rows = []
    for name in ("Local numbers", "Toll-free numbers"):
        match = _find(
            rf"{name} (?P<p>{_MONEY}) / mo\b", text[numbers:], f"{name!r}"
        )
        rows.append(
            _row("telephony", slug(name), "any", match, "p", 1, "month")
        )
    for name, pattern in (
        ("call-recording", rf"Call recording Recording (?P<p>{_MONEY}) / min"),
        ("media-streams", rf"Media Streams (?P<p>{_MONEY}) / min"),
        ("siprec", rf"SIPREC (?P<p>{_MONEY}) / min"),
    ):
        match = _find(pattern, text, name)
        rows.append(_row("telephony", name, "any", match, "p", 1, "minute"))
    return rows


def _speech(text: str) -> list[Scraped]:
    """Transcription (STT) and premium text-to-speech prices."""
    rows = []
    for word, label in (
        ("batch", "Batch"),
        ("realtime", r"Streaming \(Real-Time\)"),
    ):
        match = _find(
            rf"{label} Transcription (?P<p>{_MONEY}) / min",
            text,
            f"{word} transcription",
        )
        rows.append(
            _row(
                "stt",
                "conversation-intelligence-transcription",
                mode(word),
                match,
                "p",
                1,
                "minute",
            )
        )
    match = _find(
        rf"Transcription (?P<p>{_MONEY}) / min Answering",
        text,
        "call recording transcription",
    )
    rows.append(
        _row(
            "stt",
            "call-recording-transcription",
            "any",
            match,
            "p",
            1,
            "minute",
        )
    )
    tts = text.find("Text-to-Speech (TTS) - Premium")
    if tts < 0:
        raise PageChangedError("no premium TTS section")
    for name in _TTS:
        match = _find(
            rf"{name} (?P<p>{_MONEY}) / (?P<n>[0-9]+) chars",
            text[tts:],
            f"TTS {name!r}",
        )
        rows.append(
            _row(
                "tts",
                slug(f"Premium {name}"),
                "any",
                match,
                "p",
                int(match.group("n")),
                "character",
            )
        )
    return rows


def parse(text: str) -> list[Scraped]:
    """Every call, number, add-on, STT and TTS price on the page."""
    cps = _find(
        r"Calls per second ([0-9]+) Pay as you go Pricing Free",
        text,
        "calls per second",
    )
    limits = {
        "calls_per_second": float(cps.group(1)),
        "source_url": PRICING_URL,
        "evidence": cps.group(0),
    }
    return _calls(text, limits) + _fixed(text) + _speech(text)


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
