"""What a scraper returns, and the error it raises when a page changed."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from voice_prices.models import Price, PriceRow


class PageChangedError(Exception):
    """A scraper could not find what it expects on the page.

    Raised instead of guessing: a wrong price is worse than a missing one.
    """


@dataclass(frozen=True)
class Scraped:
    """One price as read from a page, before dates are added.

    ``amount`` is a decimal string in the page's own currency.
    """

    category: str
    provider: str
    product: str
    mode: str
    plan: str
    amount: str
    currency: str
    per: int | float
    unit: str
    source_url: str
    evidence: str
    plan_fee: dict[str, str] | None = None
    tax_included: bool | None = None
    limits: dict[str, Any] | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return f"{self.provider}/{self.product}/{self.mode}/{self.plan}"

    def to_row(self, since: str) -> dict[str, Any]:
        """The row as stored in ``data/<category>.json``.

        Raises:
            pydantic.ValidationError: The row breaks the schema.
        """
        return PriceRow(
            id=self.id,
            category=self.category,
            provider=self.provider,
            product=self.product,
            mode=self.mode,
            plan=self.plan,
            price=Price(
                amount=self.amount,
                currency=self.currency,
                per=self.per,
                unit=self.unit,
            ),
            plan_fee=self.plan_fee,
            tax_included=self.tax_included,
            limits=self.limits,
            source_url=self.source_url,
            evidence=self.evidence,
            since=since,
            **self.extra,
        ).to_json()


_MODES = {
    "real-time": "real-time",
    "realtime": "real-time",
    "streaming": "streaming",
    "websocket": "websocket",
    "batch": "batch",
    "pre-recorded": "batch",
    "prerecorded": "batch",
    "batch-with-diarization": "batch-with-diarization",
    "inbound": "inbound",
    "outbound": "outbound",
    "any": "any",
}


def mode(text: str) -> str:
    """The page's word for a mode, as one of the fixed modes.

    Raises:
        PageChangedError: A word not mapped yet. Add it to ``_MODES``.
    """
    key = slug(text)
    if key not in _MODES:
        raise PageChangedError(f"unknown mode {text!r}: map it in rows.py")
    return _MODES[key]


def slug(text: str) -> str:
    """``"Bulbul V4 Flash"`` -> ``"bulbul-v4-flash"``."""
    return re.sub(r"[^a-z0-9.]+", "-", text.lower()).strip("-")


def amount(text: str) -> str:
    """``"₹1,99,999"`` or ``"$0.05"`` -> ``"199999"`` / ``"0.05"``."""
    digits = re.sub(r"[^0-9.]", "", text)
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", digits):
        raise PageChangedError(f"not an amount: {text!r}")
    return digits
