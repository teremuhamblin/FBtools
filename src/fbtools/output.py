"""Rendu des résultats : tableau, JSON ou CSV."""

from __future__ import annotations

import csv
import io
import json
from collections.abc import Iterable
from typing import Any


def flatten(row: dict[str, Any], prefix: str = "") -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in row.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(flatten(v, f"{key}."))
        elif isinstance(v, list):
            out[key] = json.dumps(v, ensure_ascii=False)
        else:
            out[key] = v
    return out


def to_json(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def to_csv(rows: Iterable[dict[str, Any]], columns: list[str] | None = None) -> str:
    flat = [flatten(r) for r in rows]
    cols = columns or sorted({k for r in flat for k in r})
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(flat)
    return buf.getvalue()


def to_table(rows: list[dict[str, Any]], columns: list[str], max_width: int = 60) -> str:
    flat = [flatten(r) for r in rows]
    if not flat:
        return "(aucun résultat)"

    def cell(v: Any) -> str:
        s = "" if v is None else str(v).replace("\n", " ")
        return s if len(s) <= max_width else s[: max_width - 1] + "…"

    widths = {c: max(len(c), *(len(cell(r.get(c))) for r in flat)) for c in columns}
    line = "  ".join(c.ljust(widths[c]) for c in columns)
    sep = "  ".join("-" * widths[c] for c in columns)
    body = ["  ".join(cell(r.get(c)).ljust(widths[c]) for c in columns) for r in flat]
    return "\n".join([line, sep, *body])


def render(rows: list[dict[str, Any]], fmt: str, columns: list[str]) -> str:
    if fmt == "json":
        return to_json(rows)
    if fmt == "csv":
        return to_csv(rows, columns)
    return to_table(rows, columns)
