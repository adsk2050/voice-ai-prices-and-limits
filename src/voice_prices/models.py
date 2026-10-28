"""The data's one definition. ``schema/row.schema.json`` is generated from it.

Amounts are decimal strings in the currency the provider's page states,
never floats and never converted.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

Amount = Annotated[str, Field(pattern=r"^[0-9]+(\.[0-9]+)?$")]
Currency = Annotated[str, Field(pattern=r"^[A-Z]{3}$", examples=["INR"])]
Day = Annotated[str, Field(pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")]
Slug = Annotated[str, Field(pattern=r"^[a-z0-9.-]+$")]
Category = Literal["stt", "tts", "telephony"]
Unit = Literal[
    "character", "minute", "second", "hour", "token", "call", "request"
]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Price(_Model):
    """``amount`` ``currency`` per ``per`` ``unit``s."""

    amount: Amount
    currency: Currency
    per: Annotated[int | float, Field(gt=0)]
    unit: Unit


class PlanFee(_Model):
    """What the plan itself costs, before usage."""

    amount: Amount
    currency: Currency
    period: Literal["month", "year"]


class Billing(_Model):
    """How usage is rounded: a 60 s pulse, a minimum charge."""

    increment_seconds: Annotated[float | None, Field(gt=0)] = None
    minimum_seconds: Annotated[float | None, Field(ge=0)] = None


class Limits(_Model):
    """The plan's published limits."""

    requests_per_minute: Annotated[int | None, Field(ge=1)] = None
    concurrent: Annotated[int | None, Field(ge=1)] = None
    calls_per_second: Annotated[float | None, Field(gt=0)] = None
    source_url: str | None = None
    evidence: str | None = None


class PriceRow(_Model):
    """One price of one product, in one mode, on one plan."""

    model_config = ConfigDict(
        title="One price row", extra="forbid", frozen=True
    )

    id: Annotated[str, Field(pattern=r"^[a-z0-9.-]+(/[a-z0-9.-]+){3,}$")]
    category: Category
    provider: Slug
    product: Slug
    mode: Slug
    plan: Slug
    country: Annotated[str | None, Field(pattern=r"^[A-Z]{2}$")] = None
    price: Price
    plan_fee: PlanFee | None
    billing: Billing | None = None
    tax_included: bool | None = Field(
        description="false: the page says tax is extra. null: it does not say."
    )
    limits: Limits | None
    source_url: str
    evidence: Annotated[str, Field(min_length=1)]
    since: Day = Field(description="First day this repo saw this value.")

    def to_json(self) -> dict[str, object]:
        """The row as stored: optional fields left out when unset."""
        return self.model_dump(mode="json", exclude_none=True) | {
            "plan_fee": self.plan_fee and self.plan_fee.model_dump(),
            "tax_included": self.tax_included,
            "limits": self.limits
            and self.limits.model_dump(mode="json", exclude_none=True),
        }


class Checked(_Model):
    """When a provider's page was last read, and how it went."""

    checked_at: Day
    last_ok: Day | None = None
    status: Literal["ok", "failed"]
