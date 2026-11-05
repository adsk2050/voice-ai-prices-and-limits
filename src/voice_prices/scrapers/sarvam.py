"""Sarvam AI: Bulbul TTS and Saaras STT, per plan, in rupees.

The API pricing page has one table per category. Each row reads
``<service>, <mode> per <n> <unit> ₹a ₹b ₹c ₹d`` with one price per plan,
in the order of the table's header, and then again with each plan's
name in front. During an offer a plan shows two prices (list, then
offer) and the label carries a note (``Limited time, 50% off until 12
Nov``); the offer price is read, as that is what is paid today. The
plan fees are in the plan cards (``Pro ₹9,999 /month``). The docs pricing
page says prices exclude GST.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, mode, slug

PRICING_URL = "https://www.sarvam.ai/api-pricing"
DOCS_URL = "https://docs.sarvam.ai/api/getting-started/pricing"

_PLANS = ["Pay as you go", "Pro", "Growth", "Business"]
_MONEY = r"₹[0-9][0-9,]*(?:\.[0-9]+)?"
_UNITS = {"characters": "character", "minute": "minute"}

# (table heading, category, product for rows whose service names none)
_TABLES = [
    ("Text to speech", "tts", None),
    ("Speech to text", "stt", "saaras"),
]


def _table(text: str, heading: str) -> str:
    """The text of one table, from its header to the next table's."""
    header = f"{heading} Service " + " ".join(_PLANS)
    start = text.find(header)
    if start < 0:
        raise PageChangedError(f"no {heading!r} table header")
    start += len(header)
    end = text.find(" Service ", start)
    return text[start : end if end > 0 else len(text)]


def _plan_fees(text: str) -> dict[str, dict[str, str]]:
    fees = {}
    for plan in _PLANS:
        match = re.search(rf"{plan} ({_MONEY}) /month", text)
        if match is None:
            raise PageChangedError(f"no plan fee for {plan!r}")
        fees[slug(plan)] = {
            "amount": amount(match.group(1)),
            "currency": "INR",
            "period": "month",
        }
    return fees


def _row_pattern() -> re.Pattern[str]:
    """One table row: its label and unit, the prices in the columns, then
    the same prices again with each plan's name in front.

    The named copy is what is read. During an offer a plan shows two
    prices, the list price and then the offer price, and only the names
    say which prices belong to which plan.
    """
    named = " ".join(
        rf"{re.escape(plan)} (?P<list{i}>{_MONEY})(?: (?P<now{i}>{_MONEY}))?"
        for i, plan in enumerate(_PLANS)
    )
    return re.compile(
        rf"(?P<evidence>(?P<label>[A-Z][^₹]*?) per (?P<per>[0-9,]+ )?"
        rf"(?P<unit>characters|minute)(?: {_MONEY})+) {named}"
    )


_LANGUAGE_ID = "language-identification"


def _mode_word(text: str) -> str:
    """The mode at the start of *text*; any words after it are a note.

    ``"real-time Limited time, 50% off until 12 Nov"`` gives
    ``"real-time"``. ``"Batch with diarization"`` gives the whole text,
    as it is a mode of its own.
    """
    words = text.split()
    for n in range(len(words), 0, -1):
        word = " ".join(words[:n])
        if slug(word) == _LANGUAGE_ID:
            return word
        try:
            mode(word)
        except PageChangedError:
            continue
        return word
    raise PageChangedError(f"no mode in {text!r}: map it in rows.py")


def _service_and_mode(
    label: str, default_product: str | None
) -> tuple[str, str]:
    """Split a row label into product and mode.

    ``"Bulbul V4 Flash, streaming"`` gives ``("bulbul-v4-flash",
    "streaming")``. An STT row names no service, so ``"Batch"`` gives
    ``(default_product, "batch")``. A note after the mode, such as an
    offer's end date, is dropped.
    """
    if default_product is None:
        if "," not in label:
            raise PageChangedError(f"row with no service name: {label!r}")
        service, rest = (part.strip() for part in label.split(",", 1))
        return slug(service), _mode_word(rest)
    return default_product, _mode_word(label)


def parse(pricing_text: str, docs_text: str) -> list[Scraped]:
    """Every TTS and STT price on the page, one per plan."""
    fees = _plan_fees(pricing_text)
    tax_included = False if "exclude GST" in docs_text else None
    rows: list[Scraped] = []
    for heading, category, default_product in _TABLES:
        table = _table(pricing_text, heading)
        found = 0
        for match in _row_pattern().finditer(table):
            product, word = _service_and_mode(
                match.group("label"), default_product
            )
            if slug(word) == _LANGUAGE_ID:
                continue  # not speech-to-text itself
            per = int((match.group("per") or "1").replace(",", ""))
            evidence = match.group("evidence")
            for i, plan in enumerate(_PLANS):
                # The price paid today: the offer price when there is one.
                paid = match.group(f"now{i}") or match.group(f"list{i}")
                rows.append(
                    Scraped(
                        category=category,
                        provider="sarvam",
                        product=product,
                        mode=mode(word),
                        plan=slug(plan),
                        amount=amount(paid),
                        currency="INR",
                        per=per,
                        unit=_UNITS[match.group("unit")],
                        source_url=PRICING_URL,
                        evidence=evidence,
                        plan_fee=fees[slug(plan)],
                        tax_included=tax_included,
                    )
                )
            found += 1
        if found == 0:
            raise PageChangedError(f"no rows in the {heading!r} table")
    return rows


def scrape() -> list[Scraped]:
    """Fetch both pages and parse them."""
    return parse(fetch_text(PRICING_URL), fetch_text(DOCS_URL))
