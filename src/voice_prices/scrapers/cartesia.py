"""Cartesia: Sonic TTS and Ink STT prices per plan, and telephony, in USD.

The pricing page sells monthly plans (Free $0, Pro $5, Startup $49,
Scale $299) that include credits. The FAQ gives each paid plan's overage
rate (``At pro tier, it's $65 per 1M credits.``) and says ``1 credit
equals 1 character`` for Sonic TTS. That is a price per 1000000
characters. For Ink STT the only plain price is ``One hour of audio is
only $0.39 on the Scale plan.``. The compare table gives concurrent
requests per plan for each model. Telephony is ``$0.014 per minute when
using a Cartesia-provided phone number``. Agent call-duration prices and
LLM prices are agent-platform prices and are skipped. The page does not
say whether tax is included.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://cartesia.ai/pricing"

_PLANS = ["Free", "Pro", "Startup", "Scale"]
_PAID = ["Pro", "Startup", "Scale"]
_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_CONCURRENCY = (
    r"{heading} (?P<model>{prefix}-[0-9][0-9.]*) .*? Concurrent requests "
    r"(?P<c0>[0-9]+) (?P<c1>[0-9]+) (?P<c2>[0-9]+) (?P<c3>[0-9]+) Custom"
)


def _search(pattern: str, text: str, what: str) -> re.Match[str]:
    match = re.search(pattern, text)
    if match is None:
        raise PageChangedError(f"no {what}")
    return match


def _fee(text: str, plan: str) -> dict[str, str]:
    match = _search(rf"{plan} ({_MONEY}) /mo Select {plan}", text, "fee")
    return {
        "amount": amount(match.group(1)),
        "currency": "USD",
        "period": "month",
    }


def _model(text: str, heading: str, prefix: str) -> tuple[str, dict]:
    """The model name and concurrent requests per plan, from the table."""
    match = _search(
        _CONCURRENCY.format(heading=heading, prefix=prefix),
        text,
        f"{heading} concurrency row",
    )
    limits = {}
    for i, plan in enumerate(_PLANS):
        evidence = f"Concurrent requests {match.group('c0')} " + " ".join(
            match.group(f"c{j}") for j in range(1, 4)
        )
        limits[plan] = {
            "concurrent": int(match.group(f"c{i}")),
            "source_url": PRICING_URL,
            "evidence": evidence,
        }
    return slug(match.group("model")), limits


def _row(
    category: str,
    product: str,
    mode: str,
    plan: str,
    match: re.Match[str],
    per: int,
    unit: str,
    **kw,
) -> Scraped:
    return Scraped(
        category=category,
        provider="cartesia",
        product=product,
        mode=mode,
        plan=plan,
        amount=amount(match.group("price")),
        currency="USD",
        per=per,
        unit=unit,
        source_url=PRICING_URL,
        evidence=match.group(0),
        **kw,
    )


def parse(text: str) -> list[Scraped]:
    """TTS overage per plan, STT hourly price, telephony per minute."""
    if "1 credit equals 1 character" not in text:
        raise PageChangedError("no credit-to-character rate")
    tts, tts_limits = _model(text, "Text to Speech", "Sonic")
    stt, stt_limits = _model(text, "Speech to Text", "Ink")
    rows: list[Scraped] = []
    for plan in _PAID:
        match = _search(
            rf"At {plan.lower()} tier, it's (?P<price>{_MONEY}) per 1M "
            r"credits\.",
            text,
            f"{plan} overage rate",
        )
        rows.append(
            _row(
                "tts",
                tts,
                "any",
                slug(plan),
                match,
                1000000,
                "character",
                plan_fee=_fee(text, plan),
                limits=tts_limits[plan],
            )
        )
    match = _search(
        rf"One hour of audio is only (?P<price>{_MONEY}) on the Scale plan\.",
        text,
        "STT hourly price",
    )
    rows.append(
        _row(
            "stt",
            stt,
            "any",
            "scale",
            match,
            1,
            "hour",
            plan_fee=_fee(text, "Scale"),
            limits=stt_limits["Scale"],
        )
    )
    match = _search(
        rf"Telephony (?P<price>{_MONEY}) per minute when using a "
        r"Cartesia-provided phone number",
        text,
        "telephony price",
    )
    # Cartesia-provisioned numbers are US numbers.
    rows.append(
        _row(
            "telephony",
            "cartesia-provided-number",
            "any",
            "pay-as-you-go",
            match,
            1,
            "minute",
            extra={"country": "US"},
        )
    )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
