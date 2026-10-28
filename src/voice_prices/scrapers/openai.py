"""OpenAI API pricing: per-minute prices of the transcription models, in USD.

The pricing page is mostly LLM, image and tool prices. Speech-to-text is
in the "Transcription models" table. Each row reads
``<model> <use case> <input> <output> $x / minute``. The input and output
columns are token prices or ``-``. The last column is the page's
"Estimated cost" per minute, and that is the price read here.

"Live transcription" rows are real-time. Plain "Transcription" rows have
one price for every mode. "Live translation" is speech translation, not
plain speech-to-text, so it is skipped. GPT-Live voice sessions and the
realtime audio-token models are speech-to-speech, so they are skipped too.
The page does not say whether tax is included, and it states no limits.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://platform.openai.com/docs/pricing"

_MONEY = r"\$[0-9][0-9,]*(?:\.[0-9]+)?"
_HEADER = "Model Use case Input Output Estimated cost"
_ROW = re.compile(
    rf"(?P<model>[a-z0-9][a-z0-9.-]*) "
    r"(?P<use>Live transcription|Live translation|Transcription) "
    rf"(?:{_MONEY}|-) (?:{_MONEY}|-) (?P<price>{_MONEY}) / minute"
)
_MODES = {"Live transcription": "real-time", "Transcription": "any"}


def _section(text: str) -> str:
    """The text of the "Transcription models" table, up to "Tools"."""
    head = text.find("Transcription models")
    start = text.find(_HEADER, head) if head >= 0 else -1
    if start < 0:
        raise PageChangedError("no transcription models table header")
    start += len(_HEADER)
    end = text.find("Tools", start)
    return text[start : end if end > 0 else len(text)]


def parse(text: str) -> list[Scraped]:
    """One STT row per transcription model, priced per minute."""
    section = _section(text)
    rows: list[Scraped] = []
    for match in _ROW.finditer(section):
        use = match.group("use")
        if use not in _MODES:
            continue  # live translation: not plain speech-to-text
        rows.append(
            Scraped(
                category="stt",
                provider="openai",
                product=slug(match.group("model")),
                mode=_MODES[use],
                plan="pay-as-you-go",
                amount=amount(match.group("price")),
                currency="USD",
                per=1,
                unit="minute",
                source_url=PRICING_URL,
                evidence=match.group(0),
            )
        )
    if not rows:
        raise PageChangedError("no rows in the transcription models table")
    return rows


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
