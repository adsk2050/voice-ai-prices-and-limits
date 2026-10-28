"""Knowlarity voice plans in India: toll-free and missed-call numbers.

The page lists plan cards as text. Toll-free plans read ``<Name> Plan Rs
<fee> /Year ... Toll free incoming charges Rs. <x> per minute Outgoing
calling charges <n> p/ 30 sec``. The missed-call plan reads ``Application
Rental/ Missed call number Rs <fee> per month``. Prices given in paise
(``70 p/ 30 sec``, ``3 p``) are skipped: paise is not an ISO currency and
prices are never converted. Prepaid plans price calls only in paise, and
contact center plans are priced per agent, so neither gives a row.
The page states no tax and no limits.
"""

from __future__ import annotations

import re
from typing import Any

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.knowlarity.com/pricing/voice"

_MONEY = r"[0-9][0-9,]*(?:\.[0-9]+)?"
_TOLL_FREE = re.compile(
    rf"(?P<plan>[A-Z][a-z]+(?: Plus)?) Plan Rs (?P<fee>{_MONEY}) /Year "
    r"FREE monthly incoming.*?Toll [Ff]ree incoming charges "
    rf"(?P<ev>Rs\. (?P<inb>{_MONEY}) per minute)"
)
_MISSED = re.compile(
    rf"Application Rental/ Missed call number Rs (?P<fee>{_MONEY}) per month"
)


def _row(
    product: str,
    mode: str,
    plan: str,
    price: str,
    unit: str,
    evidence: str,
    plan_fee: dict[str, str] | None,
) -> Scraped:
    extra: dict[str, Any] = {"country": "IN"}
    return Scraped(
        category="telephony",
        provider="knowlarity",
        product=product,
        mode=mode,
        plan=plan,
        amount=price,
        currency="INR",
        per=1,
        unit=unit,
        source_url=PRICING_URL,
        evidence=evidence,
        plan_fee=plan_fee,
        extra=extra,
    )


def _section(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    if begin < 0:
        raise PageChangedError(f"no {start!r} section")
    stop = text.find(end, begin)
    return text[begin : stop if stop > 0 else len(text)]


def parse(text: str) -> list[Scraped]:
    """Toll-free inbound per-minute charges and the missed-call rental."""
    rows: list[Scraped] = []
    toll = _section(text, "Toll Free Number Plan Detail", "Prepaid Plan")
    for m in _TOLL_FREE.finditer(toll):
        fee = {
            "amount": amount(m.group("fee")),
            "currency": "INR",
            "period": "year",
        }
        evidence = (
            f"{m.group('plan')} Plan Rs {m.group('fee')} /Year ... "
            f"{m.group('ev')}"
        )
        # Evidence must be an exact substring: use the price part only.
        rows.append(
            _row(
                "toll-free-number",
                "inbound",
                slug(m.group("plan")),
                amount(m.group("inb")),
                "minute",
                m.group("ev"),
                fee,
            )
        )
        del evidence
    if len(rows) != 3:
        raise PageChangedError("expected 3 toll-free plans")
    m = _MISSED.search(text)
    if m is None:
        raise PageChangedError("no missed call number rental")
    rows.append(
        _row(
            "missed-call-number",
            "any",
            "monthly-plan",
            amount(m.group("fee")),
            "month",
            m.group(0),
            None,
        )
    )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page (its TLS setup fails checks) and parse it."""
    return parse(fetch_text(PRICING_URL, verify_tls=False))
