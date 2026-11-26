"""Tests des commandes CLI avec un client API simulé."""

import json

import pytest
from click.testing import CliRunner

from fbtools import cli as cli_mod
from fbtools.cli import cli, main
from fbtools.client import GraphAPIError


class StubClient:
    api_version = "v27.0"

    def __init__(self, *a, **kw):
        self.published = None

    def me(self):
        return {"id": "1", "name": "Ana"}

    def permissions(self):
        return [
            {"permission": "pages_show_list", "status": "granted"},
            {"permission": "read_insights", "status": "declined"},
        ]

    def pages(self):
        return [{"id": "42", "name": "Ma Page", "category": "Blog", "access_token": "SECRET"}]

    def posts(self, page_id, limit=25):
        return [{"id": f"{page_id}_1", "message": "Salut", "created_time": "t"}]

    def publish(self, page_id, message, link, ts):
        return {"id": f"{page_id}_9"}

    def delete_post(self, post_id):
        return {"success": True}

    def comments(self, post_id, limit=None):
        return [{"id": "c1", "from": {"id": "7", "name": "Léa"}, "message": "Bravo"}]

    def insights(self, page_id, metrics, period, since, until):
        return [
            {
                "name": "page_follows",
                "period": "day",
                "values": [{"end_time": "2026-11-02", "value": 5}],
            }
        ]


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setattr(cli_mod, "GraphClient", StubClient)
    r = CliRunner()
    r.invoke(cli, ["config", "set-token", "--token", "TOKEN", "--app-secret", "S"])
    r.invoke(cli, ["config", "set-page", "42"])
    return r


def test_whoami(runner):
    out = runner.invoke(cli, ["whoami"]).output
    assert "Ana (id 1)" in out
    assert "pages_show_list" in out
    assert "read_insights" not in out


def test_pages_list_hides_tokens(runner):
    out = runner.invoke(cli, ["pages", "list", "-f", "json"]).output
    assert json.loads(out)[0]["name"] == "Ma Page"
    assert "SECRET" not in out


def test_posts_list_uses_default_page(runner):
    out = runner.invoke(cli, ["posts", "list", "-f", "csv"]).output
    assert "42_1" in out


def test_publish_with_confirmation(runner):
    r = runner.invoke(cli, ["posts", "publish", "-m", "Hello"], input="y\n")
    assert r.exit_code == 0
    assert "Publiée : 42_9" in r.output


def test_publish_aborted(runner):
    r = runner.invoke(cli, ["posts", "publish", "-m", "Hello"], input="n\n")
    assert r.exit_code == 1


def test_publish_scheduled_from_file(runner, tmp_path):
    f = tmp_path / "msg.txt"
    f.write_text("  Annonce  \n", encoding="utf-8")
    r = runner.invoke(
        cli, ["posts", "publish", "--message-file", str(f), "--at", "2099-01-01T09:00+01:00", "-y"]
    )
    assert "Programmée : 42_9" in r.output


def test_publish_requires_content(runner):
    r = runner.invoke(cli, ["posts", "publish"])
    assert r.exit_code == 2
    assert "--message" in r.output


def test_bad_date(runner):
    r = runner.invoke(cli, ["posts", "publish", "-m", "x", "--at", "demain"])
    assert "Format attendu" in r.output


def test_delete(runner):
    assert "Supprimée." in runner.invoke(cli, ["posts", "delete", "42_1", "-y"]).output


def test_comments_export_csv_and_json(runner, tmp_path):
    out = runner.invoke(cli, ["comments", "export", "42_1"]).output
    assert "Léa" in out
    target = tmp_path / "c.json"
    r = runner.invoke(cli, ["comments", "export", "42_1", "-o", str(target)])
    assert "1 commentaires exportés" in r.output
    assert json.loads(target.read_text(encoding="utf-8"))[0]["id"] == "c1"


def test_insights_table_and_json(runner):
    assert "page_follows" in runner.invoke(cli, ["insights"]).output
    out = runner.invoke(cli, ["insights", "-f", "json", "--metric", "page_follows"]).output
    assert json.loads(out)[0]["name"] == "page_follows"


def test_set_version_adds_prefix(runner):
    assert "v28.0" in runner.invoke(cli, ["config", "set-version", "28.0"]).output


def test_missing_page(monkeypatch):
    monkeypatch.setattr(cli_mod, "GraphClient", StubClient)
    r = CliRunner()
    r.invoke(cli, ["config", "set-token", "--token", "T"])
    assert "set-page" in r.invoke(cli, ["posts", "list"]).output


@pytest.mark.parametrize(
    ("exc", "code"), [(GraphAPIError("KO", code=190), 2), (ValueError("mauvais"), 1)]
)
def test_main_maps_errors_to_exit_codes(monkeypatch, capsys, exc, code):
    def boom(**kw):
        raise exc

    monkeypatch.setattr(cli_mod, "cli", boom)
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == code
    assert "Erreur" in capsys.readouterr().err
