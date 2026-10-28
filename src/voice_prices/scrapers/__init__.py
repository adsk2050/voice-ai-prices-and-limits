"""Every scraper, by provider. Add a new one here."""

from __future__ import annotations

from collections.abc import Callable

from voice_prices.rows import Scraped
from voice_prices.scrapers import plivo, sarvam, smallestai

SCRAPERS: dict[str, Callable[[], list[Scraped]]] = {
    "plivo": plivo.scrape,
    "sarvam": sarvam.scrape,
    "smallestai": smallestai.scrape,
}
