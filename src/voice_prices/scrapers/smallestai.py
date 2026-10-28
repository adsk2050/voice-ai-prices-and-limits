"""Smallest AI: Lightning TTS and Pulse STT, in dollars.

The models pricing page lists a comparison table (pay as you go next to
Enterprise, which is "Custom") and repeats the pay-as-you-go column once
more for small screens. We read the first table only. Rows look like
``Pulse (Pre-Recorded) ~$0.003/minute Custom`` and
``Lightning V3.1 ~$0.175/10K characters Custom``. The limits rows are
``Concurrency for STT 100 concurrent streams``,
``Concurrency for TTS 15 concurrent streams`` and ``RPM for TTS APIs 100``.
The page does not give a plan fee or say whether tax is included.
"""

from __future__ import annotations

import re
from typing import Any

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://smallest.ai/pricing/models"
PLAN = "pay-as-you-go"

_STT_ROW = re.compile(
    r"(?P<name>Pulse(?: Pro)?) \((?P<mode>[A-Za-z-]+)\)"
    r" ~(?P<price>\$[0-9.]+)/minute"
)
_TTS_ROW = re.compile(
    r"(?P<name>Lightning V[0-9.]+(?: Pro)?)"
    r" ~(?P<price>\$[0-9.]+)/10K characters"
)
_STT_CONCURRENT = re.compile(r"Concurrency for STT (\d+) concurrent streams")
_TTS_CONCURRENT = re.compile(r"Concurrency for TTS (\d+) concurrent streams")
_TTS_RPM = re.compile(r"RPM for TTS APIs (\d+)")


def _first_table(text: str) -> str:
    """The first comparison table: up to where the page repeats it."""
    header = "Speech to Text Pulse (Pre-Recorded)"
    start = text.find(header)
    if start < 0:
        raise PageChangedError("no speech-to-text pricing table")
    end = text.find(header, start + len(header))
    return text[start : end if end > 0 else len(text)]


def _find(pattern: re.Pattern[str], table: str, what: str) -> re.Match[str]:
    match = pattern.search(table)
    if match is None:
        raise PageChangedError(f"no {what} on the page")
    return match


def _limits(table: str, *, stt: bool) -> dict[str, Any]:
    concurrent = _find(
        _STT_CONCURRENT if stt else _TTS_CONCURRENT, table, "concurrency"
    )
    limits: dict[str, Any] = {
        "concurrent": int(concurrent.group(1)),
        "source_url": PRICING_URL,
    }
    evidence = [concurrent.group(0)]
    if not stt:
        rpm = _find(_TTS_RPM, table, "TTS requests per minute")
        limits["requests_per_minute"] = int(rpm.group(1))
        evidence.append(rpm.group(0))
    limits["evidence"] = "; ".join(evidence)
    return limits


def parse(text: str) -> list[Scraped]:
    """Every Lightning TTS and Pulse STT price on the page."""
    table = _first_table(text)
    stt_limits = _limits(table, stt=True)
    tts_limits = _limits(table, stt=False)
    rows: list[Scraped] = []
    for match in _STT_ROW.finditer(table):
        rows.append(
            Scraped(
                category="stt",
                provider="smallestai",
                product=slug(match.group("name")),
                mode=mode(match.group("mode")),
                plan=PLAN,
                amount=amount(match.group("price")),
                currency="USD",
                per=1,
                unit="minute",
                source_url=PRICING_URL,
                evidence=match.group(0),
                limits=stt_limits,
            )
        )
    stt_count = len(rows)
    for match in _TTS_ROW.finditer(table):
        rows.append(
            Scraped(
                category="tts",
                provider="smallestai",
                product=slug(match.group("name")),
                mode="any",  # the page gives one price for every mode
                plan=PLAN,
                amount=amount(match.group("price")),
                currency="USD",
                per=10000,
                unit="character",
                source_url=PRICING_URL,
                evidence=match.group(0),
                limits=tts_limits,
            )
        )
    if stt_count == 0:
        raise PageChangedError("no Pulse rows in the table")
    if len(rows) == stt_count:
        raise PageChangedError("no Lightning rows in the table")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the models pricing page and parse it."""
    return parse(fetch_text(PRICING_URL))
