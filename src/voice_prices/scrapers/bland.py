"""Bland AI: voice-agent per-minute talk time rate, per plan, in dollars.

The pricing page has plan cards (``Start 2 credits + an inbound number
($15/mo value). $0.14 /min $0 platform fee``, ``Build ... $0.12 /min
$299/month platform fee``) and a "Compare plans" table whose "Usage +
scale" rows give, per plan in the order Start, Build, Enterprise:
``Talk Time Rate $0.14/min $0.12/min Custom``, the transfer rate and
``Concurrent calls 10 calls 50 calls Custom``. Enterprise is custom and
has no price. Transfer minutes (time a transferred call stays on Bland)
are an agent price as well. Telephony is billed separately; no tax note.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.bland.ai/pricing"

_PLANS = ["Start", "Build"]
_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"

_TALK = re.compile(
    rf"Talk Time Rate (?P<p0>{_MONEY})/min (?P<p1>{_MONEY})/min Custom"
)
_TRANSFER = re.compile(
    rf"Transfer Time Rate (?P<p0>{_MONEY})/min (?P<p1>{_MONEY})/min Custom"
)
_CONCURRENT = re.compile(
    r"Concurrent calls (?P<p0>[0-9,]+) calls (?P<p1>[0-9,]+) calls Custom"
)
# A plan card: its name, then text not reaching another card, then the
# per-minute price and the platform fee.
_FEE = re.compile(
    r"(?P<plan>Start|Build) (?:(?!Start |Build ).){0,200}?"
    rf"{_MONEY} /min (?P<fee>{_MONEY})(?:/month)? platform fee"
)


def _need(pattern: re.Pattern[str], text: str, what: str) -> re.Match[str]:
    match = pattern.search(text)
    if match is None:
        raise PageChangedError(f"no {what}")
    return match


def _plan_fees(text: str) -> dict[str, dict[str, str]]:
    """Plan fee per plan slug, from the plan cards."""
    fees: dict[str, dict[str, str]] = {}
    for m in _FEE.finditer(text):
        fees.setdefault(
            slug(m.group("plan")),
            {
                "amount": amount(m.group("fee")),
                "currency": "USD",
                "period": "month",
            },
        )
    for plan in _PLANS:
        if slug(plan) not in fees:
            raise PageChangedError(f"no platform fee for {plan!r}")
    return fees


def parse(text: str) -> list[Scraped]:
    """Talk time and transfer time per minute, one row per plan."""
    talk = _need(_TALK, text, "talk time rate row")
    transfer = _need(_TRANSFER, text, "transfer time rate row")
    concurrent = _need(_CONCURRENT, text, "concurrent calls row")
    fees = _plan_fees(text)
    rows: list[Scraped] = []
    for i, plan in enumerate(_PLANS):
        limits = {
            "concurrent": int(concurrent.group(f"p{i}").replace(",", "")),
            "source_url": PRICING_URL,
            "evidence": concurrent.group(0),
        }
        for product, match in (
            ("bland-agent", talk),
            ("bland-agent-transfer", transfer),
        ):
            rows.append(
                Scraped(
                    category="agent",
                    provider="bland",
                    product=product,
                    mode="any",
                    plan=slug(plan),
                    amount=amount(match.group(f"p{i}")),
                    currency="USD",
                    per=1,
                    unit="minute",
                    source_url=PRICING_URL,
                    evidence=match.group(0),
                    plan_fee=fees[slug(plan)],
                    tax_included=None,
                    limits=limits,
                )
            )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
