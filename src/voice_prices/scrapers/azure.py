"""Azure AI Speech, from Microsoft's public retail price API (USD).

The API returns one item per meter. We keep the main speech-to-text and
text-to-speech meters in one region (East US); Speech prices are the
same in most regions. Each row's evidence is the meter as the API gives
it.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import httpx

from voice_prices.rows import PageChangedError, Scraped

API_URL = "https://prices.azure.com/api/retail/prices"
REGION = "eastus"
_FILTER = (
    "productName eq 'Azure Speech' and armRegionName eq 'eastus'"
    " and priceType eq 'Consumption'"
)

# meter name -> (category, product, mode)
_METERS = {
    "S1 Speech To Text": ("stt", "speech-to-text", "real-time"),
    "S1 Speech to Text Batch": ("stt", "speech-to-text", "batch"),
    "Fast Transcription Speech To Text": ("stt", "fast-transcription", "any"),
    "S1 Neural Text To Speech Characters": ("tts", "neural", "any"),
    "Neural HD Text to Speech Characters": ("tts", "neural-hd", "any"),
    "S1 Neural Long Audio Characters": ("tts", "neural-long-audio", "batch"),
}
# unitOfMeasure -> (per, unit)
_UNITS = {"1 Hour": (1, "hour"), "1M": (1_000_000, "character")}


def parse(items: list[dict[str, Any]]) -> list[Scraped]:
    """The kept meters from the API's items."""
    by_meter = {i["meterName"]: i for i in items}
    rows: list[Scraped] = []
    for meter, (category, product, mode) in _METERS.items():
        item = by_meter.get(meter)
        if item is None:
            raise PageChangedError(f"no meter {meter!r}")
        if item["unitOfMeasure"] not in _UNITS:
            raise PageChangedError(f"unknown unit {item['unitOfMeasure']!r}")
        per, unit = _UNITS[item["unitOfMeasure"]]
        price = format(Decimal(str(item["retailPrice"])).normalize(), "f")
        rows.append(
            Scraped(
                category=category,
                provider="azure",
                product=product,
                mode=mode,
                plan="pay-as-you-go",
                amount=price,
                currency=item["currencyCode"],
                per=per,
                unit=unit,
                source_url=API_URL,
                evidence=(
                    f"{meter}: {item['retailPrice']} {item['currencyCode']}"
                    f" per {item['unitOfMeasure']} ({item['armRegionName']})"
                ),
            )
        )
    return rows


def scrape() -> list[Scraped]:
    """Read every page of the API's answer, then parse it."""
    items: list[dict[str, Any]] = []
    url: str | None = API_URL
    params: dict[str, str] | None = {"$filter": _FILTER}
    while url:
        data = httpx.get(url, params=params, timeout=30).raise_for_status()
        body = data.json()
        items += body["Items"]
        url, params = body.get("NextPageLink"), None
    return parse(items)
