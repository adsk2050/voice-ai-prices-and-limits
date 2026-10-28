"""Run the scrapers and rewrite ``data/*.json``.

A row whose price is unchanged keeps its ``since`` date and gets today's
``checked_at``. A changed or new row starts a new ``since``. A provider
whose scraper fails keeps its old rows untouched, and the run exits
non-zero so the failure is seen. Changes are written to
``changes.md`` for the pull request's description.

Usage: ``voice-prices update [provider ...]``
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import traceback
from pathlib import Path
from typing import Any

import jsonschema

from voice_prices.scrapers import SCRAPERS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CATEGORIES = ("stt", "tts", "telephony")


def _load(category: str) -> list[dict[str, Any]]:
    path = DATA / f"{category}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save(category: str, rows: list[dict[str, Any]]) -> None:
    rows.sort(key=lambda r: r["id"])
    (DATA / f"{category}.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _validator() -> jsonschema.Validator:
    schema = json.loads(
        (ROOT / "schema" / "row.schema.json").read_text(encoding="utf-8")
    )
    return jsonschema.Draft202012Validator(schema)


def _same_price(a: dict[str, Any], b: dict[str, Any]) -> bool:
    keys = ("price", "plan_fee", "tax_included", "limits")
    return all(a.get(k) == b.get(k) for k in keys)


def _price_text(row: dict[str, Any]) -> str:
    p = row["price"]
    return f"{p['amount']} {p['currency']} per {p['per']:g} {p['unit']}"


def update(providers: list[str], today: str) -> tuple[list[str], list[str]]:
    """Scrape *providers* and merge into the data files.

    Returns:
        (change lines, failed providers)
    """
    old = {c: {r["id"]: r for r in _load(c)} for c in CATEGORIES}
    new = {c: dict(rows) for c, rows in old.items()}
    changes: list[str] = []
    failed: list[str] = []
    validator = _validator()
    for provider in providers:
        try:
            scraped = SCRAPERS[provider]()
        except Exception:  # noqa: BLE001 - one provider must not stop the rest
            traceback.print_exc()
            failed.append(provider)
            continue
        seen: set[str] = set()
        for item in scraped:
            before = old[item.category].get(item.id)
            since = today
            if before is not None and _same_price(
                before, item.to_row(today, today)
            ):
                since = before["since"]
            row = item.to_row(today, since)
            validator.validate(row)
            new[item.category][item.id] = row
            seen.add(item.id)
            if before is None:
                changes.append(f"- new: `{item.id}` {_price_text(row)}")
            elif since == today:
                changes.append(
                    f"- changed: `{item.id}` {_price_text(before)}"
                    f" -> {_price_text(row)}. Evidence: {row['evidence']}"
                )
        for category in CATEGORIES:
            for row_id, row in list(new[category].items()):
                if row["provider"] == provider and row_id not in seen:
                    changes.append(f"- gone from the page: `{row_id}`")
                    del new[category][row_id]
    for category in CATEGORIES:
        _save(category, list(new[category].values()))
    return changes, failed


def main() -> None:
    parser = argparse.ArgumentParser(prog="voice-prices")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("update", help="scrape and rewrite data/*.json")
    run.add_argument("providers", nargs="*", help="default: all")
    args = parser.parse_args()

    providers = args.providers or sorted(SCRAPERS)
    today = dt.datetime.now(dt.UTC).date().isoformat()
    changes, failed = update(providers, today)
    report = ["## Price changes", "", *(changes or ["- none"])]
    if failed:
        report += ["", "## Scrapers that failed", ""]
        report += [f"- {p}" for p in failed]
    (ROOT / "changes.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    sys.exit(1 if failed else 0)
