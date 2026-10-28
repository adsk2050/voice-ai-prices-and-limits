"""Inworld: TTS-2 and STT 1 prices per plan, in US dollars.

The pricing page compares plans in a table headed ``Pricing per 1M
characters``. Its rows read ``Realtime TTS-2 $a $b $c $d $e As low as $f``,
with one price per plan in the header's order (On-Demand, Creator, Builder,
Developer, Growth, Enterprise). Plan fees are in the same header
(``Creator $25/mo``). The STT 1 hourly price is only in the plan cards, as
``STT 1 $0.15 $0.10/hr``: a struck-out list price, then the plan's price.
The page does not say whether tax is included. It states no numeric limits.
LLM Inference prices are ignored.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://inworld.ai/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_PLANS = ["On-Demand", "Creator", "Builder", "Developer", "Growth"]
_CARDS = [
    "On-Demand Evaluation",
    "Creator Content",
    "Builder Popular",
    "Developer Production",
    "Growth Large",
    "Enterprise Custom",
]
_HEADER = re.compile(
    r"Text-to-Speech On-Demand Start free "
    + " ".join(
        rf"{p}(?: Popular)? (?P<f{i}>{_MONEY})/mo"
        for i, p in enumerate(_PLANS[1:], 1)
    )
    + r" Enterprise Custom Pricing per 1M characters"
)
_TTS = re.compile(
    r"(?P<word>Realtime) (?P<name>TTS-2(?: Flash)?) "
    + " ".join(rf"(?P<p{i}>{_MONEY})" for i in range(len(_PLANS)))
    + rf"(?: As low as (?P<ent>{_MONEY}))?"
)
_STT = re.compile(rf"STT 1 (?:{_MONEY} )?(?P<price>{_MONEY})/hr")


def _row(
    category: str,
    product: str,
    mode_: str,
    plan: str,
    price: str,
    per: int,
    unit: str,
    evidence: str,
    fee: dict[str, str] | None,
) -> Scraped:
    return Scraped(
        category=category,
        provider="inworld",
        product=product,
        mode=mode_,
        plan=plan,
        amount=amount(price),
        currency="USD",
        per=per,
        unit=unit,
        source_url=PRICING_URL,
        evidence=evidence,
        plan_fee=fee,
    )


def _fees(text: str) -> tuple[dict[str, dict[str, str]], int]:
    """Plan fees by plan slug, and where the TTS table starts."""
    header = _HEADER.search(text)
    if header is None:
        raise PageChangedError("no Text-to-Speech compare table header")
    if not re.search(r"On-Demand Evaluation and prototyping \$0 pay as", text):
        raise PageChangedError("no On-Demand $0 plan card")
    fees = {"on-demand": {"amount": "0", "currency": "USD", "period": "month"}}
    for i, plan in enumerate(_PLANS[1:], 1):
        fees[slug(plan)] = {
            "amount": amount(header.group(f"f{i}")),
            "currency": "USD",
            "period": "month",
        }
    return fees, header.end()


def _tts(text: str, start: int, fees: dict) -> list[Scraped]:
    rows: list[Scraped] = []
    for match in _TTS.finditer(text[start : start + 400]):
        product, word, ev = (
            slug(match.group("name")),
            match.group("word"),
            (match.group(0)),
        )
        for i, plan in enumerate(_PLANS):
            rows.append(
                _row(
                    "tts",
                    product,
                    mode(word),
                    slug(plan),
                    match.group(f"p{i}"),
                    1000000,
                    "character",
                    ev,
                    fees[slug(plan)],
                )
            )
        if match.group("ent"):  # "As low as": the lowest Enterprise rate
            rows.append(
                _row(
                    "tts",
                    product,
                    mode(word),
                    "enterprise",
                    match.group("ent"),
                    1000000,
                    "character",
                    ev,
                    None,
                )
            )
    if len(rows) < 2 * len(_PLANS):
        raise PageChangedError("TTS-2 or TTS-2 Flash row missing")
    return rows


def _stt(text: str, fees: dict) -> list[Scraped]:
    starts = [text.find(card) for card in _CARDS]
    if min(starts) < 0 or starts != sorted(starts):
        raise PageChangedError("plan cards missing or reordered")
    rows = []
    for plan, start, end in zip(_PLANS, starts, starts[1:], strict=False):
        match = _STT.search(text[start:end])
        if match is None:
            raise PageChangedError(f"no STT 1 price on the {plan} card")
        rows.append(
            _row(
                "stt",
                "stt-1",
                "any",
                slug(plan),
                match.group("price"),
                1,
                "hour",
                match.group(0),
                fees[slug(plan)],
            )
        )
    return rows


def parse(text: str) -> list[Scraped]:
    """TTS-2, TTS-2 Flash and STT 1 prices, one row per plan."""
    fees, start = _fees(text)
    return _tts(text, start, fees) + _stt(text, fees)


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
