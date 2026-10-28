"""Vapi: the voice-agent platform's own per-minute hosting fee, in USD.

The "Choose your Success Package" plan cards read ``No Success Package ...
Pre-paid, $0.05/min Vapi hosting.`` followed by the plan's features
(``4 concurrent calls``). Core and Pro state a monthly fee or a share of the
hosting fee but no per-minute price of their own, so they give no rows.
The transport fees (Twilio, Vonage, Telnyx) are charged by those providers
and name no country, so they are skipped. The page says nothing about tax.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://vapi.ai/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_PLAN = "No Success Package"
_HOSTING = re.compile(
    rf"(?P<plan>{_PLAN}) Get started for free.{{0,80}}?"
    rf"Pre-paid, (?P<price>{_MONEY})/min Vapi hosting"
)
_CONCURRENT = re.compile(r"(?P<n>[0-9]+) concurrent calls")


def _concurrency(text: str, start: int) -> dict[str, object] | None:
    """The plan's concurrent call limit, read from the card after the price."""
    card = text[start : text.find("Core For builders", start)]
    match = _CONCURRENT.search(card)
    if match is None:
        return None
    return {
        "concurrent": int(match.group("n")),
        "source_url": PRICING_URL,
        "evidence": match.group(0),
    }


def parse(text: str) -> list[Scraped]:
    """The per-minute Vapi hosting fee of the plan that states one."""
    match = _HOSTING.search(text)
    if match is None:
        raise PageChangedError("no per-minute Vapi hosting price")
    return [
        Scraped(
            category="agent",
            provider="vapi",
            product="vapi",
            mode="any",
            plan=slug(match.group("plan")),
            amount=amount(match.group("price")),
            currency="USD",
            per=1,
            unit="minute",
            source_url=PRICING_URL,
            evidence=match.group(0),
            limits=_concurrency(text, match.end()),
        )
    ]


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
