"""Gestion de la configuration locale (~/.config/fbtools/config.json).

Les variables d'environnement ont priorité sur le fichier :
  FBTOOLS_ACCESS_TOKEN, FBTOOLS_APP_SECRET, FBTOOLS_API_VERSION, FBTOOLS_CONFIG_DIR
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path

from . import DEFAULT_API_VERSION


def config_dir() -> Path:
    custom = os.environ.get("FBTOOLS_CONFIG_DIR")
    if custom:
        return Path(custom)
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "fbtools"


def config_path() -> Path:
    return config_dir() / "config.json"


@dataclass
class Config:
    access_token: str | None = None
    app_secret: str | None = None
    api_version: str = DEFAULT_API_VERSION
    default_page_id: str | None = None

    @classmethod
    def load(cls) -> Config:
        data: dict = {}
        path = config_path()
        if path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
        cfg = cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        cfg.access_token = os.environ.get("FBTOOLS_ACCESS_TOKEN", cfg.access_token)
        cfg.app_secret = os.environ.get("FBTOOLS_APP_SECRET", cfg.app_secret)
        cfg.api_version = os.environ.get("FBTOOLS_API_VERSION", cfg.api_version)
        return cfg

    def save(self) -> Path:
        path = config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        try:
            os.chmod(path, 0o600)  # le jeton est un secret
        except OSError:
            pass
        return path

    def masked(self) -> dict:
        def mask(v: str | None) -> str | None:
            if not v:
                return v
            return v[:6] + "…" + v[-4:] if len(v) > 12 else "****"

        d = asdict(self)
        d["access_token"] = mask(self.access_token)
        d["app_secret"] = mask(self.app_secret)
        return d
