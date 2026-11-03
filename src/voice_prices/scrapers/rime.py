"""Rime: Mist v3 and Coda v2 TTS and Rime STT, per plan, in dollars.

The page has two paid plan cards. "Flex" is pay as you go with no
monthly fee (``Flex Billed by minute, monthly to your card``); it is
stored as the ``pay-as-you-go`` plan. "Scale" costs ``$100 a month`` and
takes 20% off every rate. Each card lists each model as ``<model>
<kind> $a / min``. The STT price is followed by ``Free until Nov 19``:
the printed price applies from November 20, and STT is free until then.
TTS is also described per 1K characters further down; this module uses
the per-minute card price. Enterprise is "Volume pricing" with no
number, so it is skipped. Prism (speech to speech) has no category here
and is skipped. The page says concurrency limits apply but gives no
numbers. The page does not say whether tax is included.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount

PRICING_URL = "https://www.rime.ai/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"

# (plan id, card start, card end)
_CARDS = [
    ("pay-as-you-go", "Flex Billed by minute, monthly to your card", "Scale "),
    ("scale", "Scale Steady usage, 20% off every rate", "Enterprise "),
]
_SCALE_FEE = re.compile(rf"From {_MONEY} /min (?P<fee>{_MONEY}) a month")

# (product, category, anchor before the price, anchor after it)
_MODELS = [
    ("mist-v3", "tts", r"Mist v3 Text to speech", ""),
    ("coda-v2", "tts", r"Coda v2 Text to speech", ""),
    ("rime-stt", "stt", r"Rime STT Speech to text", r" Free until Nov 19"),
]


def _card(text: str, start: str, end: str) -> str:
    begin = text.find(start)
    if begin < 0:
        raise PageChangedError(f"no plan card starting {start!r}")
    stop = text.find(end, begin + len(start))
    if stop < 0:
        raise PageChangedError(f"no end of plan card {start!r}")
    return text[begin:stop]


def parse(text: str) -> list[Scraped]:
    """One per-minute price per model and plan."""
    rows: list[Scraped] = []
    for plan, start, end in _CARDS:
        card = _card(text, start, end)
        fee = None
        if plan == "scale":
            match = _SCALE_FEE.search(card)
            if match is None:
                raise PageChangedError("no Scale monthly fee")
            fee = {
                "amount": amount(match.group("fee")),
                "currency": "USD",
                "period": "month",
            }
        for product, category, before, after in _MODELS:
            match = re.search(
                rf"{before} (?P<price>{_MONEY}) / min{after}", card
            )
            if match is None:
                raise PageChangedError(f"no {plan} price for {product!r}")
            rows.append(
                Scraped(
                    category=category,
                    provider="rime",
                    product=product,
                    mode="any",
                    plan=plan,
                    amount=amount(match.group("price")),
                    currency="USD",
                    per=1,
                    unit="minute",
                    source_url=PRICING_URL,
                    evidence=match.group(0),
                    plan_fee=fee,
                )
            )
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
