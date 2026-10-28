"""Google Cloud Text-to-Speech prices, in US dollars.

The page has three tables. "Gemini-TTS" prices each model per 1 million
text tokens (input) and per 1 million audio tokens (output). Some
preview models list two rows: a price "through" a date and a later
price "starting" on a date. Only the current ("through" or undated) row
is kept. "Latest TTS models" and "Legacy TTS models" price voices per
character and, in brackets, per 1 million characters; the per-million
figure is used. No plans, limits or tax statement are given.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://cloud.google.com/text-to-speech/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_SKU = r"\(sku: ?[A-Z0-9-]+\)"

_GEMINI = re.compile(
    rf"(?P<name>Gemini [0-9][^*]*?)"
    r"(?:\*\* through (?P<through>[A-Za-z]+ [0-9]+, [0-9]{4})"
    r"| starting (?P<start>[A-Za-z]+ [0-9]+, [0-9]{4}))?"
    rf" Not available Input tokens: (?P<input>{_MONEY}) per 1 million "
    rf"text tokens\* {_SKU}\.? Output tokens: (?P<output>{_MONEY}) per "
    r"1 million audio tokens"
)

# A voice name: words after "reached " or a previous row's ") ", never
# running over table headings ("Legacy TTS models Model ...").
_WORD = r"(?!models\b|Model\b|reached\b)[A-Za-z0-9:()-]+"
_VOICE = re.compile(
    r"(?:(?<=reached )|(?<=\) ))"
    rf"(?P<name>[A-Z][A-Za-z0-9:()-]*(?: {_WORD})*?) voices? ?{_SKU} "
    r"(?:0 to [0-9]+ million characters|Not available) "
    r"US\$[0-9.]+ per character "
    r"\(US(?P<price>\$[0-9][0-9,]*(?:\.[0-9]+)?) ?per 1 million characters\)"
)


def _row(product: str, price: str, unit: str, evidence: str) -> Scraped:
    return Scraped(
        category="tts",
        provider="google",
        product=product,
        mode="any",
        plan="pay-as-you-go",
        amount=amount(price),
        currency="USD",
        per=1000000,
        unit=unit,
        source_url=PRICING_URL,
        evidence=evidence,
    )


def _gemini(text: str) -> list[Scraped]:
    """Token prices of the Gemini-TTS models, current rows only."""
    rows: list[Scraped] = []
    for match in _GEMINI.finditer(text):
        if match.group("start") or "starting" in match.group("name"):
            continue  # a future price, not in effect yet
        # One row may name several models sharing a price.
        names = re.split(r" (?=Gemini [0-9])", match.group("name").strip())
        for name in names:
            base = slug(name)
            for group, suffix in (
                ("input", "text-input"),
                ("output", "audio-output"),
            ):
                rows.append(
                    _row(
                        f"{base}-{suffix}",
                        match.group(group),
                        "token",
                        match.group(0),
                    )
                )
    if not rows:
        raise PageChangedError("no Gemini-TTS token prices")
    return rows


def _voices(text: str) -> list[Scraped]:
    """Per-character voice prices, as stated per 1 million characters."""
    rows = [
        _row(
            slug(match.group("name")),
            match.group("price"),
            "character",
            match.group(0),
        )
        for match in _VOICE.finditer(text)
    ]
    if not rows:
        raise PageChangedError("no per-character voice prices")
    names = {row.product for row in rows}
    for expected in ("wavenet", "standard", "neural2"):
        if expected not in names:
            raise PageChangedError(f"no price for {expected!r} voices")
    return rows


def parse(text: str) -> list[Scraped]:
    """Every TTS price on the page: Gemini tokens and voice characters."""
    if "Pricing table" not in text:
        raise PageChangedError("no pricing table")
    return _gemini(text) + _voices(text)


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
