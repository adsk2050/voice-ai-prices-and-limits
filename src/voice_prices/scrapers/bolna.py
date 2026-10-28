"""Bolna AI voice-agent platform: per-minute prices per plan, in US dollars.

The pricing page lists three plans: Pay-as-you-go, Pilots and Enterprise.

- Pay-as-you-go has no fixed price table. Its price is read from the FAQ:
  ``Bolna AI starts at $0.06 per minute (about ₹5.52) on pay-as-you-go``.
  That is a "starts at" price, and the evidence says so.
- The Pilot plan is a one-time package with two tiers: ``$500 for 12,000
  minutes (~4.2¢/min)`` and ``$300 for 6,500 minutes``. Each tier is kept
  as the page states it: the dollar amount per its number of minutes.
  Both tiers include ``up to 25 concurrent calls``.
- Enterprise is "Talk to sales", so it has no price.

The cent rates of the top-up slider are skipped: the page does not tie
them clearly to a payment tier. The page says nothing about tax.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.bolna.ai/pricing"

_PROVIDER = "bolna"
_PRODUCT = slug("Bolna AI")
_USD = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_PAYG = re.compile(
    rf"Bolna AI starts at (?P<price>{_USD}) per minute \(about [^)]*\) "
    r"on pay-as-you-go"
)
_PILOT_INTRO = "The Pilot plan is a one-time purchase"
_PILOT_TIER = re.compile(
    rf"(?P<price>{_USD}) for (?P<per>[0-9][0-9,]*) minutes"
    r"(?: \(~[0-9.]+¢/min\))?"
)
_CONCURRENT = re.compile(r"up to (?P<n>[0-9]+) concurrent calls")


def _row(
    plan: str,
    price: str,
    per: int,
    evidence: str,
    limits: dict[str, object] | None = None,
) -> Scraped:
    """One agent price row in USD per ``per`` minutes."""
    return Scraped(
        category="agent",
        provider=_PROVIDER,
        product=_PRODUCT,
        mode="any",
        plan=plan,
        amount=amount(price),
        currency="USD",
        per=per,
        unit="minute",
        source_url=PRICING_URL,
        evidence=evidence,
        limits=limits,
    )


def _pay_as_you_go(text: str) -> Scraped:
    """The "starts at" per-minute price for pay-as-you-go."""
    match = _PAYG.search(text)
    if match is None:
        raise PageChangedError("no pay-as-you-go 'starts at' price")
    # The match itself reads "starts at", so it is the evidence as is.
    return _row("pay-as-you-go", match.group("price"), 1, match.group(0))


def _pilot(text: str) -> list[Scraped]:
    """One row per Pilot tier, priced per its stated number of minutes."""
    start = text.find(_PILOT_INTRO)
    if start < 0:
        raise PageChangedError("no Pilot plan FAQ answer")
    end = text.find("How does pay-as-you-go pricing work?", start)
    section = text[start : end if end > 0 else len(text)]
    concurrent = _CONCURRENT.search(section)
    if concurrent is None:
        raise PageChangedError("no Pilot concurrency limit")
    limits = {
        "concurrent": int(concurrent.group("n")),
        "source_url": PRICING_URL,
        "evidence": concurrent.group(0),
    }
    rows = []
    for match in _PILOT_TIER.finditer(section):
        price = amount(match.group("price"))
        rows.append(
            _row(
                slug(f"pilot {price}"),
                match.group("price"),
                int(match.group("per").replace(",", "")),
                match.group(0),
                limits,
            )
        )
    if len(rows) < 2:
        raise PageChangedError("expected two Pilot tiers")
    return rows


def parse(text: str) -> list[Scraped]:
    """Pay-as-you-go and Pilot plan prices for Bolna voice agents."""
    if not text.strip():
        raise PageChangedError("empty page")
    return [_pay_as_you_go(text), *_pilot(text)]


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
