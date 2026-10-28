"""The README's coverage table, generated from the data files.

The table sits between two markers in ``README.md``; the daily run
rewrites it, and a test fails when it is out of date.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

START = "<!-- coverage:start -->"
END = "<!-- coverage:end -->"
_CATEGORY = {
    "stt": "Speech-to-text",
    "tts": "Text-to-speech",
    "telephony": "Telephony",
}


def _rows(data: Path) -> list[dict[str, Any]]:
    rows = []
    for category in _CATEGORY:
        path = data / f"{category}.json"
        if path.exists():
            rows += json.loads(path.read_text(encoding="utf-8"))
    return rows


def _per(price: dict[str, Any]) -> str:
    """``1000`` characters -> ``"1,000 characters"``; ``1`` -> ``"minute"``."""
    if price["per"] == 1:
        return price["unit"]
    return f"{price['per']:,g} {price['unit']}s"


def table(data: Path) -> str:
    """One line per provider and product: modes, plans, price range."""
    checked = json.loads((data / "checked.json").read_text(encoding="utf-8"))
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in _rows(data):
        groups[(row["category"], row["provider"], row["product"])].append(row)
    lines = [
        "| Category | Provider | Product | Modes | Plans | Price"
        " | Last checked |",
        "|---|---|---|---|---|---|---|",
    ]
    order = list(_CATEGORY)
    for (category, provider, product), rows in sorted(
        groups.items(), key=lambda kv: (order.index(kv[0][0]), kv[0][1:])
    ):
        modes = sorted({r["mode"] for r in rows})
        fee = {
            r["plan"]: float((r["plan_fee"] or {"amount": "0"})["amount"])
            for r in rows
        }
        plans = sorted(fee, key=lambda plan: (fee[plan], plan))
        amounts = sorted({float(r["price"]["amount"]) for r in rows})
        p = rows[0]["price"]
        span = (
            f"{amounts[0]:g}"
            if len(amounts) == 1
            else f"{amounts[0]:g}–{amounts[-1]:g}"
        )
        state = checked.get(provider, {})
        last = state.get("checked_at", "never")
        if state.get("status") == "failed":
            last += " (scraper broken)"
        lines.append(
            f"| {_CATEGORY[category]} | {provider} | {product}"
            f" | {', '.join(modes)} | {', '.join(plans)}"
            f" | {span} {p['currency']} per {_per(p)}"
            f" | {last} |"
        )
    return "\n".join(lines)


def rewrite(readme: Path, data: Path) -> bool:
    """Put the current table into *readme*. Returns whether it changed."""
    text = readme.read_text(encoding="utf-8")
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new = f"{head}{START}\n{table(data)}\n{END}{tail}"
    if new == text:
        return False
    readme.write_text(new, encoding="utf-8", newline="\n")
    return True
