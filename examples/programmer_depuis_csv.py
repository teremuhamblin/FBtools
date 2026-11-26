"""Programme des publications Facebook à partir d'un fichier CSV.

Colonnes attendues : date (ISO 8601 avec fuseau), message, lien (facultatif).

    python examples/programmer_depuis_csv.py examples/publications.csv --page 1234567890
    python examples/programmer_depuis_csv.py examples/publications.csv --page 1234567890 --go
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
from pathlib import Path

from fbtools.client import GraphAPIError, GraphClient
from fbtools.config import Config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv", type=Path)
    parser.add_argument("--page", required=True, help="ID de la Page")
    parser.add_argument("--go", action="store_true", help="Envoyer réellement (sinon simulation)")
    args = parser.parse_args()

    cfg = Config.load()
    client = GraphClient(cfg.access_token or "", cfg.api_version, cfg.app_secret)
    errors = 0
    with args.csv.open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            when = int(datetime.fromisoformat(row["date"]).timestamp())
            label = f"{row['date']} · {row['message'][:40]}"
            if not args.go:
                print(f"[simulation] {label}")
                continue
            try:
                res = client.publish(args.page, row["message"], row.get("lien") or None, when)
                print(f"[programmée] {label} → {res.get('id')}")
            except GraphAPIError as exc:
                errors += 1
                print(f"[erreur] {label} : {exc}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
