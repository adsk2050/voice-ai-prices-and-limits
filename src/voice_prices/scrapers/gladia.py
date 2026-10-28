"""Gladia speech-to-text (Solaria models), per hour, in euros.

The pricing page has an "Async rate per hour by monthly volume" table:
a header ``Monthly volume Solaria-1 Solaria-3`` and then one row per tier,
``0 - 100 hours 0.27€/hr 0.16€/hr`` ... ``10,000+ hours 0.21€/hr 0.12€/hr``.
The plan comparison table gives the Self-serve real-time rate
(``Real-time rate 0.68€/hr (0.0113€/min)``); it names no model. The FAQ
states the Self-serve concurrency limits. Enterprise is "Custom" (no
price). Add-ons (summarization, translation...) and Audio to LLM are not
transcription and are skipped. The page does not say whether tax is
included.
"""

from __future__ import annotations

import re
from typing import Any

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://www.gladia.io/pricing"

_PLAN = "Self-serve"
_MONEY = r"[0-9][0-9,]*(?:\.[0-9]+)?"
_HEADER = re.compile(r"Monthly volume (?P<a>Solaria-\d+) (?P<b>Solaria-\d+) ")
_TIER = re.compile(
    rf"(?P<lo>[0-9][0-9,]*)(?: - (?P<hi>[0-9][0-9,]*)|\+) hours "
    rf"(?P<a>{_MONEY})€/hr (?P<b>{_MONEY})€/hr"
)
_REAL_TIME = re.compile(
    rf"Real-time rate (?P<price>{_MONEY})€/hr \({_MONEY}€/min\)"
)
_LIMITS = re.compile(
    r"The Self-serve plan allows (?P<rt>[0-9]+) concurrent real-time "
    r"sessions and (?P<batch>[0-9]+) concurrent pre-recorded jobs"
)


def _num(text: str) -> int:
    return int(text.replace(",", ""))


def _limits(text: str) -> dict[str, dict[str, Any]]:
    match = _LIMITS.search(text)
    if match is None:
        raise PageChangedError("no Self-serve concurrency limits")
    return {
        word: {
            "concurrent": int(match.group(group)),
            "source_url": PRICING_URL,
            "evidence": match.group(0),
        }
        for word, group in (("real-time", "rt"), ("pre-recorded", "batch"))
    }


def _row(
    product: str,
    word: str,
    match: re.Match[str],
    group: str,
    limits: dict[str, Any],
    volume: dict[str, Any] | None = None,
) -> Scraped:
    return Scraped(
        category="stt",
        provider="gladia",
        product=product,
        mode=mode(word),
        plan=slug(_PLAN),
        amount=amount(match.group(group)),
        currency="EUR",
        per=1,
        unit="hour",
        source_url=PRICING_URL,
        evidence=match.group(0),
        limits=limits,
        volume=volume,
    )


def _async_tiers(text: str, limits: dict[str, Any]) -> list[Scraped]:
    header = _HEADER.search(text)
    if header is None:
        raise PageChangedError("no async volume table header")
    end = text.find("Top-up bonuses", header.end())
    table = text[header.end() : end if end > 0 else len(text)]
    tiers = list(_TIER.finditer(table))
    if not tiers or _num(tiers[0].group("lo")) != 0:
        raise PageChangedError("async volume tiers missing or not from 0")
    if tiers[-1].group("hi") is not None:
        raise PageChangedError("last async tier is not open-ended")
    rows: list[Scraped] = []
    for match in tiers:
        hi = match.group("hi")
        volume = {
            "min": _num(match.group("lo")),
            "max": None if hi is None else _num(hi),
            "unit": "hour",
        }
        for group in ("a", "b"):
            rows.append(
                _row(
                    slug(header.group(group)),
                    "batch",
                    match,
                    group,
                    limits,
                    volume,
                )
            )
    return rows


def parse(text: str) -> list[Scraped]:
    """Async tiered prices per model and the real-time price, Self-serve."""
    limits = _limits(text)
    rows = _async_tiers(text, limits["pre-recorded"])
    real_time = _REAL_TIME.search(text)
    if real_time is None:
        raise PageChangedError("no real-time rate")
    rows.append(
        _row(
            "real-time-speech-to-text",
            "real-time",
            real_time,
            "price",
            limits["real-time"],
        )
    )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
