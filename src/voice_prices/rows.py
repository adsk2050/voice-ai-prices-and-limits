"""What a scraper returns, and the error it raises when a page changed."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


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

    def to_row(self, checked_at: str, since: str) -> dict[str, Any]:
        """The row as stored in ``data/<category>.json``."""
        row: dict[str, Any] = {
            "id": self.id,
            "category": self.category,
            "provider": self.provider,
            "product": self.product,
            "mode": self.mode,
            "plan": self.plan,
            "price": {
                "amount": self.amount,
                "currency": self.currency,
                "per": self.per,
                "unit": self.unit,
            },
            "plan_fee": self.plan_fee,
            "tax_included": self.tax_included,
            "limits": self.limits,
            "source_url": self.source_url,
            "evidence": self.evidence,
            "checked_at": checked_at,
            "since": since,
        }
        row.update(self.extra)
        return row


def slug(text: str) -> str:
    """``"Bulbul V4 Flash"`` -> ``"bulbul-v4-flash"``."""
    return re.sub(r"[^a-z0-9.]+", "-", text.lower()).strip("-")


def amount(text: str) -> str:
    """``"₹1,99,999"`` or ``"$0.05"`` -> ``"199999"`` / ``"0.05"``."""
    digits = re.sub(r"[^0-9.]", "", text)
    if not re.fullmatch(r"[0-9]+(\.[0-9]+)?", digits):
        raise PageChangedError(f"not an amount: {text!r}")
    return digits
