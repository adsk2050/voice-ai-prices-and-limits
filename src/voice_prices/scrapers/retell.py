"""Retell AI: voice-agent platform prices per minute, in US dollars.

The pricing page shows the voice agent price as a range
(``Price $0.07-$0.31/minute``). The page also lists the parts of a call.
The voice engine (``Retell Voice Infra $0.055/minute``) and the TTS voices
are under the ``Text-to-speech Notes Pricing`` table. The call agent add-ons
are priced per minute, per dial or per outbound call. The telephony rate
shown under ``Select Country`` is for the first country listed, United
States (Twilio). LLM, chat and SMS prices are ignored. Phone number rentals
are skipped because the page states no country for them. The page says
nothing about tax.
"""

from __future__ import annotations

import re

from voice_prices.page import fetch_text
from voice_prices.rows import PageChangedError, Scraped, amount, slug

PRICING_URL = "https://www.retellai.com/pricing"

_MONEY = r"\$ ?[0-9]+(?:\.[0-9]+)?"
_AGENT = re.compile(
    rf"Voice AI Pay-as-you-go Enterprise Price (?P<price>{_MONEY})-"
    rf"{_MONEY}/minute"
)
_CONCURRENT = re.compile(r"Concurrent calls (?P<n>[0-9]+) included")
_INFRA = re.compile(rf"Retell Voice Infra (?P<price>{_MONEY})/minute")
_VOICE = re.compile(
    rf"(?P<name>[A-Z][A-Za-z0-9. ]*?) (?P<price>{_MONEY})/minute"
)
_TEL = re.compile(
    r"Select Country Country United States \(Twilio\)[^$]*?"
    rf"(?P<price>{_MONEY}) /min"
)
_ADD_ON = re.compile(
    r"(?P<name>[A-Z][A-Za-z ]+?) (?P<free>First (?P<n>[0-9]+) minutes free )?"
    rf"\+?(?P<price>{_MONEY})/(?P<unit>minute|min|dial|outbound call)"
)
_ADD_ON_UNITS = {
    "minute": "minute",
    "min": "minute",
    "dial": "call",
    "outbound call": "call",
}


def _between(text: str, start: str, end: str) -> str:
    """The text after ``start`` and before the next ``end``."""
    i = text.find(start)
    if i < 0:
        raise PageChangedError(f"no {start!r}")
    i += len(start)
    j = text.find(end, i)
    if j < 0:
        raise PageChangedError(f"no {end!r} after {start!r}")
    return text[i:j]


def _row(
    category: str, product: str, match: re.Match[str], **kw: object
) -> Scraped:
    return Scraped(
        category=category,
        provider="retell",
        product=product,
        mode="any",
        plan="pay-as-you-go",
        amount=amount(match.group("price")),
        currency="USD",
        per=1,
        unit=kw.pop("unit", "minute"),  # type: ignore[arg-type]
        source_url=PRICING_URL,
        evidence=match.group(0),
        **kw,  # type: ignore[arg-type]
    )


def parse(text: str) -> list[Scraped]:
    """Voice agent, voice engine, TTS voices, add-ons and call rate."""
    agent = _AGENT.search(text)
    conc = _CONCURRENT.search(text)
    infra = _INFRA.search(text)
    tel = _TEL.search(text)
    if not (agent and conc and infra and tel):
        raise PageChangedError("missing agent, concurrency, infra or call rate")
    limits = {
        "concurrent": int(conc.group("n")),
        "source_url": PRICING_URL,
        "evidence": conc.group(0),
    }
    # A range: the lower bound, "$0.07-$0.31/minute", is the starting price.
    rows = [
        _row("agent", "voice-agent", agent, limits=limits),
        _row("agent", "retell-voice-infra", infra),
        _row("telephony", "retell-twilio", tel, extra={"country": "US"}),
    ]
    tts = _between(text, "Text-to-speech Notes Pricing ", " LLM Standard")
    voices = [
        _row("tts", slug(m.group("name")), m) for m in _VOICE.finditer(tts)
    ]
    if not voices:
        raise PageChangedError("no TTS voice prices")
    adds = _between(text, "Call Agent Add-ons Notes Extras ", " SMS ")
    extras = []
    for m in _ADD_ON.finditer(adds):
        volume = None
        if m.group("free"):
            # The free first tier has no printed price; only the paid one.
            volume = {"min": int(m.group("n")), "max": None, "unit": "minute"}
        extras.append(
            _row(
                "agent",
                slug(m.group("name")),
                m,
                unit=_ADD_ON_UNITS[m.group("unit")],
                volume=volume,
            )
        )
    if not extras:
        raise PageChangedError("no call agent add-on prices")
    return rows + voices + extras


def scrape() -> list[Scraped]:
    """Fetch the page and parse it."""
    return parse(fetch_text(PRICING_URL))
