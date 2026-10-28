"""Plivo voice calls in India, per minute, in rupees.

The India pricing page is server-rendered. Its "Voice Calls" table has one
row per route type, ``<route> ₹a/min ₹b/min`` with the outbound price
first and the inbound price second. The note under the table gives the
billing pulse (``Pulse is 30 seconds.``). Number rental is a fixed charge
per number per month; add-ons are priced per minute or per a few seconds.
The page does not say whether tax is included, and it states no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.plivo.com/voice/pricing/in/"

_MONEY = r"₹[0-9][0-9,]*(?:\.[0-9]+)?"
_ROUTES = ["Domestic Calls", "Browser SDKs and WebRTC"]
_HEADER = "To Make Calls (Outbound) To Receive Calls (Inbound)"
_MODES = ["outbound", "inbound"]


def _section(text: str) -> str:
    """The text of the "Voice Calls" table, up to the next section."""
    start = text.find(_HEADER)
    if start < 0:
        raise PageChangedError("no voice calls table header")
    start += len(_HEADER)
    end = text.find("Phone Number Rental", start)
    return text[start : end if end > 0 else len(text)]


def _pulse_seconds(section: str) -> float:
    match = re.search(r"Pulse is ([0-9]+) seconds", section)
    if match is None:
        raise PageChangedError("no billing pulse")
    return float(match.group(1))


_RENTAL = re.compile(rf"(?P<name>Domestic Numbers) (?P<price>{_MONEY})/month")
_ADD_ON = re.compile(
    rf"(?P<name>[A-Z][A-Za-z ]+?) (?:\* )?(?P<price>{_MONEY})/ ?"
    r"(?:(?P<per>[0-9]+) )?(?P<unit>min|seconds)(?![a-z])"
)
_ADD_ON_UNITS = {"min": "minute", "seconds": "second"}


def _fixed(text: str) -> list[Scraped]:
    """Number rental and add-on services, one price each."""
    rental = _RENTAL.search(text)
    if rental is None:
        raise PageChangedError("no number rental price")
    # The table starts after its "Service Price" header.
    start = text.find("Service Price ", text.find("Add-On Services Per-minute"))
    end = text.find("* Call recording", start)
    if start < 0 or end < 0:
        raise PageChangedError("no add-on services table")
    found = [(rental, "phone-number", 1, "month")]
    for match in _ADD_ON.finditer(text[start + len("Service Price ") : end]):
        found.append(
            (
                match,
                slug(match.group("name")),
                int(match.group("per") or 1),
                _ADD_ON_UNITS[match.group("unit")],
            )
        )
    if len(found) == 1:
        raise PageChangedError("no add-on service rows")
    return [
        Scraped(
            category="telephony",
            provider="plivo",
            product=product,
            mode="any",
            plan="pay-as-you-go",
            amount=amount(match.group("price")),
            currency="INR",
            per=per,
            unit=unit,
            source_url=PRICING_URL,
            evidence=match.group(0),
            extra={"country": "IN"},
        )
        for match, product, per, unit in found
    ]


def parse(text: str) -> list[Scraped]:
    """Call prices per route and direction, number rental and add-ons."""
    section = _section(text)
    pulse = _pulse_seconds(section)
    rows: list[Scraped] = []
    for route in _ROUTES:
        match = re.search(
            rf"{route} (?P<out>{_MONEY})/min (?P<in>{_MONEY})/min", section
        )
        if match is None:
            raise PageChangedError(f"no price for {route!r}")
        for mode, group in zip(_MODES, ("out", "in"), strict=True):
            rows.append(
                Scraped(
                    category="telephony",
                    provider="plivo",
                    product=slug(route),
                    mode=mode,
                    plan="pay-as-you-go",
                    amount=amount(match.group(group)),
                    currency="INR",
                    per=1,
                    unit="minute",
                    source_url=PRICING_URL,
                    evidence=f"{match.group(0)} Pulse is {pulse:g} seconds.",
                    extra={
                        "country": "IN",
                        "billing": {"increment_seconds": pulse},
                    },
                )
            )
    return rows + _fixed(text)


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
