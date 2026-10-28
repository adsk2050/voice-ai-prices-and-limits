"""The update run: what changes the data, and what only moves dates."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from voice_prices import files, update
from voice_prices.rows import Scraped

ROOT = Path(__file__).resolve().parents[1]


def _row(amount: str) -> Scraped:
    return Scraped(
        category="tts",
        provider="acme",
        product="voice-1",
        mode="real-time",
        plan="pay-as-you-go",
        amount=amount,
        currency="USD",
        per=1000,
        unit="character",
        source_url="https://example.com/pricing",
        evidence=f"Voice 1 ${amount} per 1,000 characters",
    )


@pytest.fixture
def data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "data").mkdir()
    shutil.copytree(ROOT / "schema", tmp_path / "schema")
    monkeypatch.setattr(update, "ROOT", tmp_path)
    monkeypatch.setattr(update, "DATA", tmp_path / "data")
    monkeypatch.setattr(update, "CHECKED", tmp_path / "data" / "checked.json")
    return tmp_path / "data"


def _scraper(monkeypatch: pytest.MonkeyPatch, result: object) -> None:
    def scrape() -> list[Scraped]:
        if isinstance(result, Exception):
            raise result
        return result  # type: ignore[return-value]

    monkeypatch.setattr(update, "SCRAPERS", {"acme": scrape})


def test_same_price_next_day_changes_only_checked(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _scraper(monkeypatch, [_row("0.05")])
    update.update(["acme"], "2026-10-28")
    before = (data / "tts.json").read_text(encoding="utf-8")

    changes, failed = update.update(["acme"], "2026-10-29")

    assert (changes, failed) == ([], [])
    assert (data / "tts.json").read_text(encoding="utf-8") == before
    checked = files.load(data / "checked.json", {})
    assert checked["acme"]["checked_at"] == "2026-10-29"


def test_a_new_price_is_a_change_with_a_new_since(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _scraper(monkeypatch, [_row("0.05")])
    update.update(["acme"], "2026-10-28")
    _scraper(monkeypatch, [_row("0.04")])

    changes, _ = update.update(["acme"], "2026-10-29")

    assert len(changes) == 1 and "0.05 USD" in changes[0]
    row = files.load(data / "tts.json", [])[0]
    assert (row["price"]["amount"], row["since"]) == ("0.04", "2026-10-29")


def test_an_unknown_mode_fails_only_that_provider(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from voice_prices.rows import PageChangedError, mode

    with pytest.raises(PageChangedError):
        mode("hyper-realtime")
    good = _row("0.05")
    bad = Scraped(**{**good.__dict__, "provider": "other", "mode": "odd"})
    monkeypatch.setattr(
        update, "SCRAPERS", {"acme": lambda: [good], "other": lambda: [bad]}
    )

    changes, failed = update.update(["acme", "other"], "2026-10-28")

    assert failed == ["other"]
    assert len(changes) == 1 and "acme" in changes[0]


def test_a_broken_scraper_keeps_old_rows(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _scraper(monkeypatch, [_row("0.05")])
    update.update(["acme"], "2026-10-28")
    _scraper(monkeypatch, RuntimeError("page moved"))

    changes, failed = update.update(["acme"], "2026-10-29")

    assert (changes, failed) == ([], ["acme"])
    rows = files.load(data / "tts.json", [])
    assert rows[0]["price"]["amount"] == "0.05"
    assert rows[0]["status"] == "failed"
    assert rows[0]["error"] == "RuntimeError: page moved"
    checked = files.load(data / "checked.json", {})
    assert checked["acme"] == {
        "checked_at": "2026-10-29",
        "last_ok": "2026-10-28",
        "status": "failed",
    }


def test_a_fixed_scraper_clears_failed_without_a_change(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _scraper(monkeypatch, [_row("0.05")])
    update.update(["acme"], "2026-10-28")
    _scraper(monkeypatch, RuntimeError("page moved"))
    update.update(["acme"], "2026-10-29")
    _scraper(monkeypatch, [_row("0.05")])

    changes, failed = update.update(["acme"], "2026-10-30")

    assert (changes, failed) == ([], [])
    row = files.load(data / "tts.json", [])[0]
    assert (row["status"], row["since"]) == ("ok", "2026-10-28")
    assert "error" not in row


def test_a_row_gone_from_the_page_is_kept_as_missing_once(
    data: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _scraper(monkeypatch, [_row("0.05")])
    update.update(["acme"], "2026-10-28")
    _scraper(monkeypatch, [])

    first, _ = update.update(["acme"], "2026-10-29")
    again, _ = update.update(["acme"], "2026-10-30")

    assert len(first) == 1 and "gone from the page" in first[0]
    assert again == []
    row = files.load(data / "tts.json", [])[0]
    assert row["status"] == "missing"
    assert row["error"] == "not on the page on 2026-10-29"


def test_an_unknown_schema_version_is_refused(tmp_path: Path) -> None:
    path = tmp_path / "tts.json"
    path.write_text('{"schema_version": 99, "rows": []}', encoding="utf-8")

    with pytest.raises(files.SchemaVersionError):
        files.load(path, [])
