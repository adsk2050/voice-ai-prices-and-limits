"""Deepgram: speech-to-text and text-to-speech prices, per plan, in USD.

The pricing page has two-column tables, Pay As You Go and Growth, for each
of the streaming STT, pre-recorded STT and TTS sections. Each section also
has a one-column copy, which is skipped. An STT row reads ``<model> i
<description> <price> <price>``. A price is either ``$a/min`` or ``Current
price $a/min Regular price $b/min``. For a promotion, the current price is
used and the evidence shows both prices. A TTS row reads ``<model>
$a/1k characters $b/1k characters``.

The overview states concurrency per plan: REST for pre-recorded audio and
WSS for streaming. The Growth fee is given per year (``$4K+ / year``). That
is not a monthly fee, so it is not recorded. The page says nothing on tax.

Skipped: STT add-ons, the Voice Agent API (agent platform) and Audio
Intelligence (LLM tokens).
"""

from __future__ import annotations

import re
from typing import Any

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://deepgram.com/pricing"

_PLANS = ["Pay As You Go", "Growth"]
_HEAD = "Model Pay As You Go Growth "
_NAME = r"(?P<name>[A-Z][A-Za-z0-9.-]*(?: [A-Z][A-Za-z0-9.-]*)?)"

# (start marker, end marker, page's mode word)
_STT = [
    ("Streaming pricing " + _HEAD, "Streaming pricing , single", "streaming"),
    (
        "Pre-Recorded pricing " + _HEAD,
        "Pre-Recorded pricing , single",
        "pre-recorded",
    ),
]
_TTS = ("Text to Speech ", "Calculate the Text-to-Speech")


def _price(group: str) -> str:
    return (
        rf"(?:Current price )?(?P<{group}>\$[0-9]+(?:\.[0-9]+)?)/min"
        r"(?: Regular price \$[0-9.]+/min)?"
    )


_STT_ROW = re.compile(rf"{_NAME}(?: i [^$]*?)? {_price('p0')} {_price('p1')}")
_TTS_ROW = re.compile(
    r"(?P<name>[A-Z][A-Za-z0-9.-]*(?: TTS)?) "
    r"(?P<p0>\$[0-9.]+)/1k characters (?P<p1>\$[0-9.]+)/1k characters"
)
_LIMITS = re.compile(
    r"Up to (?P<r0>[0-9]+) for the REST API Up to (?P<r1>[0-9]+) for the "
    r"REST API Up to (?P<w0>[0-9]+) for the WSS API Up to (?P<w1>[0-9]+) "
    r"for the WSS API"
)


def _section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    if begin < 0:
        raise PageChangedError(f"no section starting {start!r}")
    begin += len(start)
    stop = text.find(end, begin)
    if stop < 0:
        raise PageChangedError(f"no end of section {end!r}")
    return text[begin:stop]


def _limits(text: str) -> dict[str, dict[str, Any]]:
    """Concurrency per (plan index, mode word)."""
    match = _LIMITS.search(text)
    if match is None:
        raise PageChangedError("no concurrency limits")
    out: dict[str, dict[str, Any]] = {}
    for i in range(len(_PLANS)):
        for word, key in (("streaming", "w"), ("pre-recorded", "r")):
            out[f"{i}/{word}"] = {
                "concurrent": int(match.group(f"{key}{i}")),
                "source_url": PRICING_URL,
                "evidence": match.group(0),
            }
    return out


def _rows(
    matches: list[re.Match[str]],
    category: str,
    word: str,
    per: int,
    unit: str,
    limits: dict[str, dict[str, Any]],
) -> list[Scraped]:
    return [
        Scraped(
            category=category,
            provider="deepgram",
            product=slug(match.group("name")),
            mode=mode(word),
            plan=slug(plan),
            amount=amount(match.group(f"p{i}")),
            currency="USD",
            per=per,
            unit=unit,
            source_url=PRICING_URL,
            evidence=match.group(0),
            limits=limits.get(f"{i}/{word}"),
        )
        for match in matches
        for i, plan in enumerate(_PLANS)
    ]


def parse(text: str) -> list[Scraped]:
    """STT prices per model, mode and plan; TTS prices per model and plan."""
    limits = _limits(text)
    rows: list[Scraped] = []
    for start, end, word in _STT:
        found = list(_STT_ROW.finditer(_section(text, start, end)))
        if not found:
            raise PageChangedError(f"no {word} STT rows")
        rows += _rows(found, "stt", word, 1, "minute", limits)
    tts = _section(text, *_TTS)
    head = tts.find(_HEAD)
    if head < 0:
        raise PageChangedError("no TTS table header")
    found = list(_TTS_ROW.finditer(tts[head + len(_HEAD) :]))
    if not found:
        raise PageChangedError("no TTS rows")
    rows += _rows(found, "tts", "any", 1000, "character", {})
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
