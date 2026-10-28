"""Telnyx Voice API (Call Control): call minutes, add-ons, STT and TTS.

The page lists the base call rate per line (``Make outbound calls $0.002
per minute + the SIP Trunking fee for outbound calls``), then an "Optional
features" table of ``<name> $x per <unit>`` rows that mixes voice add-ons,
STT engines (per minute) and TTS voices (per character). Number rental is
in the "Usually bought with" cards (``$1.00 / NUMBER/MO``). Prices are pay
as you go, in USD, for US calls. The Growth and Enterprise plans state a
discount but no rates, so they get no rows. Tax is not stated as included
or extra, and no limits are given per plan.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://telnyx.com/pricing/call-control"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_LINES = re.compile(
    rf"(?P<name>Make outbound calls|Local number|Toll-free number) "
    rf"(?P<price>{_MONEY}) per minute \+ the SIP Trunking fee for "
    r"(?P<mode>outbound|inbound) calls"
)
_FEATURE = re.compile(
    rf"(?P<name>[A-Z][^$]*?) (?P<price>{_MONEY}) per "
    r"(?P<unit>leg per minute|participant, per minute|minute|character"
    r"|call|invocation)(?![a-z])"
)
_NUMBER = re.compile(
    rf"(?P<name>Phone Numbers|Toll Free Numbers) [^$]*?"
    rf"(?P<price>{_MONEY}) / NUMBER/MO"
)
# Text inside the features table that is not part of a priced row.
_NOISE = re.compile(
    r"Conversational AI View comprehensive pricing |Secure media Free "
    r"|[A-Za-z ]+ BYO API key \(billed by \w+\) "
)
_FEATURES_HEADER = "Optional features Line Pay as you go "
_UNITS = {"character": "character", "call": "call"}


def _row(
    category: str,
    name: str,
    word: str,
    price: str,
    unit: str,
    evidence: str,
    telephony: bool,
) -> Scraped:
    return Scraped(
        category=category,
        provider="telnyx",
        product=slug(name),
        mode=word,
        plan="pay-as-you-go",
        amount=amount(price),
        currency="USD",
        per=1,
        unit=unit,
        source_url=PRICING_URL,
        evidence=evidence,
        extra={"country": "US"} if telephony else {},
    )


def _features(text: str) -> list[Scraped]:
    start = text.find(_FEATURES_HEADER)
    end = text.find("Machine readable", start)
    if start < 0 or end < 0:
        raise PageChangedError("no optional features table")
    section = _NOISE.sub("", text[start + len(_FEATURES_HEADER) : end])
    rows: list[Scraped] = []
    for match in _FEATURE.finditer(section):
        name, unit = match.group("name"), match.group("unit")
        if unit == "invocation":
            continue  # no clear unit in the fixed list
        evidence = match.group(0)
        if evidence not in text:
            raise PageChangedError(f"row not found verbatim: {evidence!r}")
        if unit == "character":
            category = "tts"
        elif re.search(r"STT$", name):
            category = "stt"
        else:
            category = "telephony"
        # Keep the STT/TTS suffix in the product: "Telnyx STT" and
        # "Telnyx TTS" would otherwise share one id.
        rows.append(
            _row(
                category,
                name,
                "any",
                match.group("price"),
                _UNITS.get(unit, "minute"),
                evidence,
                category == "telephony",
            )
        )
    for category in ("stt", "tts", "telephony"):
        if not any(r.category == category for r in rows):
            raise PageChangedError(f"no {category} rows in features table")
    return rows


def parse(text: str) -> list[Scraped]:
    """Call minutes, add-ons, numbers, STT and TTS, pay as you go."""
    rows: list[Scraped] = []
    for match in _LINES.finditer(text):
        rows.append(
            _row(
                "telephony",
                match.group("name"),
                mode(match.group("mode")),
                match.group("price"),
                "minute",
                match.group(0),
                True,
            )
        )
    if len(rows) != 3:
        raise PageChangedError(f"expected 3 call lines, got {len(rows)}")
    numbers = list(_NUMBER.finditer(text))
    if len(numbers) != 2:
        raise PageChangedError("no phone number rental prices")
    for match in numbers:
        rows.append(
            _row(
                "telephony",
                match.group("name"),
                "any",
                match.group("price"),
                "month",
                match.group(0),
                True,
            )
        )
    rows += _features(text)
    ids = [r.id for r in rows]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise PageChangedError(f"duplicate ids: {sorted(dupes)}")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
