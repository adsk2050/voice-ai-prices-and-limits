"""Fetch a pricing page and reduce it to plain text."""

from __future__ import annotations

import html
import re

import httpx

_USER_AGENT = (
    "voice-ai-prices-and-limits/0.1"
    " (+https://github.com/adsk2050/voice-ai-prices-and-limits)"
)


def to_text(markup: str) -> str:
    """The page's visible text on one line, whitespace collapsed."""
    markup = re.sub(r"<(script|style)\b.*?</\1>", " ", markup, flags=re.S)
    text = html.unescape(re.sub(r"<[^>]+>", " ", markup))
    return re.sub(r"\s+", " ", text).strip()


def fetch_text(url: str, *, verify_tls: bool = True) -> str:
    """Download *url* and return its visible text.

    Args:
        url: The page.
        verify_tls: False only for a site whose certificate chain is
            incomplete (browsers repair it, HTTP clients do not). The
            page is public and read-only, and every price must still
            match the page's own text.

    Raises:
        httpx.HTTPError: The page could not be fetched.
    """
    response = httpx.get(
        url,
        headers={"User-Agent": _USER_AGENT},
        follow_redirects=True,
        timeout=30,
        verify=verify_tls,
    )
    response.raise_for_status()
    return to_text(response.text)
