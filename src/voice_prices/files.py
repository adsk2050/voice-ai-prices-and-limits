"""Reading and writing the files in ``data/``.

Every file is an object: ``schema_version``, then its content under
one key (``rows`` or ``providers``). A reader checks the version before
it uses anything else, so a change of shape fails loudly instead of
being read wrong.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from voice_prices.models import SCHEMA_VERSION

_PROVIDER_FILES = ("checked.json", "unavailable.json")


class SchemaVersionError(ValueError):
    """A data file has a schema version this code does not know."""


def key(name: str) -> str:
    """Where the content sits in the file called *name*."""
    return "providers" if name in _PROVIDER_FILES else "rows"


def unwrap(name: str, document: Any) -> Any:
    """The content of a parsed data file, after checking its version.

    Raises:
        SchemaVersionError: The version is missing or not ``SCHEMA_VERSION``.
    """
    version = (
        document.get("schema_version") if isinstance(document, dict) else None
    )
    if version != SCHEMA_VERSION:
        raise SchemaVersionError(
            f"{name}: schema_version {version!r}, expected {SCHEMA_VERSION}"
        )
    return document[key(name)]


def load(path: Path, empty: Any) -> Any:
    """The content of the data file at *path*, or *empty* if it is absent."""
    if not path.exists():
        return empty
    return unwrap(path.name, json.loads(path.read_text(encoding="utf-8")))


def dump(path: Path, content: Any) -> None:
    """Write *content* to the data file at *path*, with the version."""
    document = {"schema_version": SCHEMA_VERSION, key(path.name): content}
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
        newline="\n",
    )
