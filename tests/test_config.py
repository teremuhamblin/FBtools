import os
import stat
import sys

import pytest

from fbtools import DEFAULT_API_VERSION
from fbtools.config import Config, config_dir, config_path


def test_defaults():
    cfg = Config.load()
    assert cfg.access_token is None
    assert cfg.api_version == DEFAULT_API_VERSION


def test_env_overrides_file(monkeypatch):
    Config(access_token="FILE", api_version="v20.0").save()
    monkeypatch.setenv("FBTOOLS_ACCESS_TOKEN", "ENV")
    monkeypatch.setenv("FBTOOLS_API_VERSION", "v99.0")
    cfg = Config.load()
    assert cfg.access_token == "ENV"
    assert cfg.api_version == "v99.0"


def test_unknown_keys_ignored():
    config_path().parent.mkdir(parents=True, exist_ok=True)
    config_path().write_text('{"access_token": "T", "obsolete": 1}', encoding="utf-8")
    assert Config.load().access_token == "T"


def test_corrupted_file_gives_clear_error():
    config_path().parent.mkdir(parents=True, exist_ok=True)
    config_path().write_text("{pas du json", encoding="utf-8")
    with pytest.raises(ValueError, match="illisible"):
        Config.load()


def test_non_object_file_rejected():
    config_path().parent.mkdir(parents=True, exist_ok=True)
    config_path().write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="invalide"):
        Config.load()


@pytest.mark.skipif(sys.platform == "win32", reason="permissions POSIX")
def test_saved_file_is_private():
    path = Config(access_token="secret").save()
    assert stat.S_IMODE(os.stat(path).st_mode) == 0o600


def test_xdg_config_home(monkeypatch, tmp_path):
    monkeypatch.delenv("FBTOOLS_CONFIG_DIR")
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert config_dir() == tmp_path / "xdg" / "fbtools"


def test_masking():
    m = Config(access_token="AAAAAA00000000zzzz", app_secret="short").masked()
    assert m["access_token"] == "AAAAAA…zzzz"
    assert m["app_secret"] == "****"
