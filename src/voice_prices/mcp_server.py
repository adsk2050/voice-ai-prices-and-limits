"""An MCP server any agent can ask for voice AI prices and limits.

It reads the published data files: from GitHub by default, or from a
local folder or another URL given in ``VOICE_PRICES_DATA``. Files are
cached for an hour.

Run with uvx, from git::

    uvx --from git+https://github.com/adsk2050/voice-ai-prices-and-limits \
        voice-prices-mcp
"""

from __future__ import annotations

import json
import os
import time
from decimal import Decimal
from pathlib import Path
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer
from pydantic import BaseModel

from voice_prices.files import unwrap
from voice_prices.models import Category, Checked, PriceRow

DEFAULT_DATA = (
    "https://raw.githubusercontent.com/adsk2050/"
    "voice-ai-prices-and-limits/main/data"
)
CACHE_SECONDS = 3600
CATEGORIES: tuple[Category, ...] = ("stt", "tts", "telephony", "agent")

mcp = MCPServer(
    "voice-ai-prices-and-limits",
    instructions=(
        "Prices and published limits for speech-to-text, text-to-speech"
        " and telephony providers. Prices are in the currency the"
        " provider states; never assume a conversion."
    ),
)
_cache: dict[str, tuple[float, Any]] = {}


def _source() -> str:
    return os.environ.get("VOICE_PRICES_DATA", DEFAULT_DATA).rstrip("/")


def _file(name: str) -> Any:
    """One data file, parsed; from the cache when fresh."""
    hit = _cache.get(name)
    if hit is not None and time.monotonic() - hit[0] < CACHE_SECONDS:
        return hit[1]
    source = _source()
    if source.startswith(("http://", "https://")):
        response = httpx.get(f"{source}/{name}", timeout=30)
        response.raise_for_status()
        data = response.json()
    else:
        data = json.loads((Path(source) / name).read_text(encoding="utf-8"))
    data = unwrap(name, data)
    _cache[name] = (time.monotonic(), data)
    return data


def _rows(category: Category) -> list[PriceRow]:
    return [PriceRow.model_validate(r) for r in _file(f"{category}.json")]


class Provider(BaseModel):
    """A provider, what it covers, and how fresh its prices are."""

    provider: str
    categories: list[Category]
    rows: int
    checked: Checked | None


@mcp.tool()
def list_providers(category: Category | None = None) -> list[Provider]:
    """Providers with prices here, and when each was last checked.

    Args:
        category: "stt", "tts", "telephony" or "agent"; all when not given.
    """
    checked = {k: Checked(**v) for k, v in _file("checked.json").items()}
    found: dict[str, Provider] = {}
    for cat in [category] if category else CATEGORIES:
        for row in _rows(cat):
            entry = found.setdefault(
                row.provider,
                Provider(
                    provider=row.provider,
                    categories=[],
                    rows=0,
                    checked=checked.get(row.provider),
                ),
            )
            if cat not in entry.categories:
                entry.categories.append(cat)
            entry.rows += 1
    return sorted(found.values(), key=lambda p: p.provider)


@mcp.tool()
def get_prices(
    category: Category,
    provider: str | None = None,
    product: str | None = None,
    mode: str | None = None,
    plan: str | None = None,
) -> list[PriceRow]:
    """Price rows, filtered. Each price is in the currency its page states.

    Args:
        category: "stt", "tts", "telephony" or "agent".
        provider: e.g. "sarvam".
        product: e.g. "bulbul-v4-flash".
        mode: e.g. "real-time", "streaming", "batch".
        plan: e.g. "pay-as-you-go", "pro".
    """
    wanted = {
        "provider": provider,
        "product": product,
        "mode": mode,
        "plan": plan,
    }
    return [
        row
        for row in _rows(category)
        if all(v is None or getattr(row, k) == v for k, v in wanted.items())
    ]


class Ranked(BaseModel):
    """A row with its price for one unit, for sorting."""

    price_per_unit: str
    row: PriceRow


@mcp.tool()
def compare(
    category: Category, plan: str | None = "pay-as-you-go"
) -> dict[str, list[Ranked]]:
    """Cheapest first, grouped by currency and unit (never converted).

    Args:
        category: "stt", "tts", "telephony" or "agent".
        plan: only this plan; every plan when null.
    """
    groups: dict[str, list[Ranked]] = {}
    for row in _rows(category):
        if plan is not None and row.plan != plan:
            continue
        unit_price = Decimal(row.price.amount) / Decimal(str(row.price.per))
        key = f"{row.price.currency} per {row.price.unit}"
        groups.setdefault(key, []).append(
            Ranked(price_per_unit=f"{unit_price.normalize():f}", row=row)
        )
    for ranked in groups.values():
        ranked.sort(key=lambda r: Decimal(r.price_per_unit))
    return groups


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
