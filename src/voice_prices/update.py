"""Run the scrapers and rewrite ``data/*.json``.

A row changes only when its price, plan fee, tax flag or limits change;
it then gets a new ``since`` date. When each provider was last checked
lives in ``data/checked.json``, so a day with no price change touches
only that file. A provider whose scraper fails keeps its old rows, is
marked failed there, and the run exits non-zero.

The run writes ``changes.md`` (the pull request's description) and, on
GitHub Actions, the outputs ``price_changed`` and ``failed``.

Usage: ``voice-prices update [provider ...]``
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import traceback
from pathlib import Path
from typing import Any

from voice_prices.models import PriceRow
from voice_prices.scrapers import SCRAPERS

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
CATEGORIES = ("stt", "tts", "telephony")
CHECKED = DATA / "checked.json"


def _read(path: Path, empty: Any) -> Any:
    if not path.exists():
        return empty
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _same_price(a: dict[str, Any], b: dict[str, Any]) -> bool:
    keys = ("price", "plan_fee", "tax_included", "limits")
    return all(a.get(k) == b.get(k) for k in keys)


def _price_text(row: dict[str, Any]) -> str:
    p = row["price"]
    return f"{p['amount']} {p['currency']} per {p['per']:g} {p['unit']}"


def update(providers: list[str], today: str) -> tuple[list[str], list[str]]:
    """Scrape *providers* and merge into the data files.

    Returns:
        (price change lines, failed providers)
    """
    old = {
        c: {r["id"]: r for r in _read(DATA / f"{c}.json", [])}
        for c in CATEGORIES
    }
    new = {c: dict(rows) for c, rows in old.items()}
    checked: dict[str, dict[str, str]] = _read(CHECKED, {})
    changes: list[str] = []
    failed: list[str] = []
    for provider in providers:
        try:
            scraped = SCRAPERS[provider]()
        except Exception:  # noqa: BLE001 - one provider must not stop the rest
            traceback.print_exc()
            failed.append(provider)
            checked[provider] = {
                **checked.get(provider, {}),
                "checked_at": today,
                "status": "failed",
            }
            continue
        seen: set[str] = set()
        for item in scraped:
            before = old[item.category].get(item.id)
            row = item.to_row(since=today)
            if before is not None and _same_price(before, row):
                row["since"] = before["since"]
            new[item.category][item.id] = row
            seen.add(item.id)
            if before is None:
                changes.append(f"- new: `{item.id}` {_price_text(row)}")
            elif row != before:
                changes.append(
                    f"- changed: `{item.id}` {_price_text(before)}"
                    f" -> {_price_text(row)}. Evidence: {row['evidence']}"
                )
        for category in CATEGORIES:
            for row_id, row in list(new[category].items()):
                if row["provider"] == provider and row_id not in seen:
                    changes.append(f"- gone from the page: `{row_id}`")
                    del new[category][row_id]
        checked[provider] = {
            "checked_at": today,
            "last_ok": today,
            "status": "ok",
        }
    for category in CATEGORIES:
        rows = sorted(new[category].values(), key=lambda r: r["id"])
        _write(DATA / f"{category}.json", rows)
    _write(CHECKED, checked)
    return changes, failed


def _github_outputs(changes: list[str], failed: list[str]) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as out:
        out.write(f"price_changed={'true' if changes else 'false'}\n")
        out.write(f"failed={' '.join(failed)}\n")


def schema_json() -> str:
    """``schema/row.schema.json``, generated from :class:`PriceRow`."""
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        **PriceRow.model_json_schema(),
    }
    return json.dumps(schema, indent=2, sort_keys=True) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(prog="voice-prices")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("update", help="scrape and rewrite data/*.json")
    run.add_argument("providers", nargs="*", help="default: all")
    sub.add_parser("schema", help="regenerate schema/row.schema.json")
    args = parser.parse_args()

    if args.command == "schema":
        (ROOT / "schema" / "row.schema.json").write_text(
            schema_json(), encoding="utf-8", newline="\n"
        )
        return

    providers = args.providers or sorted(SCRAPERS)
    today = dt.datetime.now(dt.UTC).date().isoformat()
    changes, failed = update(providers, today)
    report = ["## Price changes", "", *(changes or ["- none"])]
    if failed:
        report += ["", "## Scrapers that failed", ""]
        report += [f"- {p}" for p in failed]
    (ROOT / "changes.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    _github_outputs(changes, failed)
    sys.exit(1 if failed else 0)
