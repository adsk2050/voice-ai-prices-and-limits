"""Deepgram: speech-to-text and text-to-speech prices, per plan, in USD.

The pricing page carries its whole rate card as schema.org JSON-LD: an
``OfferCatalog`` named ``Rates by product`` with one ``Offer`` per
product and plan. An offer's name reads ``<category>: <model>
(<mode>) — <plan>``, for example ``Speech-to-text: Nova-3 Monolingual
(Pre-recorded) — Growth``; TTS offers have no mode. The visible tables
show only one STT tab at a time, so the catalog is the one place that
has both streaming and pre-recorded prices. Each row's evidence is the
offer as the page gives it.

The FAQ (also in the JSON-LD) states streaming concurrency per plan:
``Pay as you go allows 150 concurrent streaming speech-to-text
connections and Growth 225``. The page no longer states a pre-recorded
limit. The Growth fee is given per year (``$4,000+ / year``). That is
not a monthly fee, so it is not recorded. The page says nothing on tax.

Skipped: STT add-ons, the Voice Agent API (agent platform) and Audio
Intelligence (LLM tokens).
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from typing import Any

from voice_prices.page import fetch_html
from voice_prices.rows import PageChangedError, Scraped, mode, slug

PRICING_URL = "https://deepgram.com/pricing"

_PLANS = ["Pay as you go", "Growth"]
# Billed on top of transcription, not a transcription price.
_ADD_ONS = {
    "Redaction",
    "Keyterm Prompting",
    "Entity Detection",
    "Speaker Diarization",
    "Smart Formatting",
}
# Offer category -> (row category, per, unit, unitText on the page)
_CATEGORIES = {
    "Speech-to-text": ("stt", 1, "minute", "minute"),
    "Text-to-speech": ("tts", 1000, "character", "1,000 characters"),
}
_OFFER = re.compile(
    r"(?P<category>[^:]+): (?P<model>.+?)(?: \((?P<mode>[^)]+)\))?"
    r" — (?P<plan>.+)"
)
_LIMITS = re.compile(
    r"Pay as you go allows (?P<c0>[0-9]+) concurrent streaming "
    r"speech-to-text connections and Growth (?P<c1>[0-9]+)"
)
_LD_JSON = re.compile(
    r"<script[^>]*application/ld\+json[^>]*>(.*?)</script>", re.S
)


def _graph(html: str) -> list[dict[str, Any]]:
    """Every JSON-LD node on the page."""
    nodes: list[dict[str, Any]] = []
    for block in _LD_JSON.findall(html):
        data = json.loads(block)
        nodes += data.get("@graph", [data]) if isinstance(data, dict) else data
    return nodes


def _offers(nodes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for node in nodes:
        if node.get("@type") == "OfferCatalog" and node.get("name") == (
            "Rates by product"
        ):
            return node["itemListElement"]
    raise PageChangedError("no 'Rates by product' offer catalog")


def _limits(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Streaming concurrency per plan, from the FAQ answers."""
    for node in nodes:
        if node.get("@type") != "FAQPage":
            continue
        for question in node.get("mainEntity", []):
            answer = question.get("acceptedAnswer", {}).get("text", "")
            match = _LIMITS.search(answer)
            if match:
                return {
                    plan: {
                        "concurrent": int(match.group(f"c{i}")),
                        "source_url": PRICING_URL,
                        "evidence": match.group(0),
                    }
                    for i, plan in enumerate(_PLANS)
                }
    raise PageChangedError("no concurrency limits")


def _product(category: str, model: str) -> str:
    # "Flux STT English" -> "flux-english"; "Flux TTS" stays "flux-tts".
    if category == "stt":
        model = model.replace(" STT", "")
    return slug(model)


def parse(html: str) -> list[Scraped]:
    """STT prices per model, mode and plan; TTS prices per model and plan."""
    nodes = _graph(html)
    limits = _limits(nodes)
    rows: list[Scraped] = []
    for offer in _offers(nodes):
        match = _OFFER.fullmatch(offer["name"])
        if match is None:
            raise PageChangedError(f"unreadable offer name {offer['name']!r}")
        if match["category"] not in _CATEGORIES or match["model"] in _ADD_ONS:
            continue
        category, per, unit, unit_text = _CATEGORIES[match["category"]]
        spec = offer["priceSpecification"]
        if spec.get("unitText") != unit_text:
            raise PageChangedError(f"unknown unit {spec.get('unitText')!r}")
        if match["plan"] not in _PLANS:
            raise PageChangedError(f"unknown plan {match['plan']!r}")
        word = match["mode"] or "any"
        rows.append(
            Scraped(
                category=category,
                provider="deepgram",
                product=_product(category, match["model"]),
                mode=mode(word),
                plan=slug(match["plan"]),
                amount=format(Decimal(str(spec["price"])).normalize(), "f"),
                currency=spec["priceCurrency"],
                per=per,
                unit=unit,
                source_url=PRICING_URL,
                evidence=(
                    f"{offer['name']}: {spec['price']} "
                    f"{spec['priceCurrency']} per {unit_text}"
                ),
                limits=limits[match["plan"]] if word == "Streaming" else None,
            )
        )
    if not any(r.category == "stt" for r in rows):
        raise PageChangedError("no STT offers")
    if not any(r.category == "tts" for r in rows):
        raise PageChangedError("no TTS offers")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_html(PRICING_URL))
