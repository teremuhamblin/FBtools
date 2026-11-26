import json

from click.testing import CliRunner

from fbtools.cli import cli
from fbtools.output import to_csv


def test_version():
    r = CliRunner().invoke(cli, ["--version"])
    assert "1.0.0" in r.output


def test_config_roundtrip():
    runner = CliRunner()
    assert (
        runner.invoke(cli, ["config", "set-token", "--token", "EAABxxxxxxxxxxxxxx1234"]).exit_code
        == 0
    )
    assert runner.invoke(cli, ["config", "set-page", "42"]).exit_code == 0
    shown = json.loads(runner.invoke(cli, ["config", "show"]).output)
    assert shown["default_page_id"] == "42"
    assert shown["access_token"].endswith("1234")
    assert "…" in shown["access_token"]


def test_missing_token_message():
    r = CliRunner().invoke(cli, ["whoami"])
    assert r.exit_code != 0
    assert "set-token" in r.output


def test_publish_dry_run():
    runner = CliRunner()
    runner.invoke(cli, ["config", "set-token", "--token", "T"])
    r = runner.invoke(cli, ["posts", "publish", "--page", "1", "-m", "Salut", "--dry-run"])
    assert r.exit_code == 0
    assert json.loads(r.output)["dry_run"] is True


def test_schedule_in_past_rejected():
    runner = CliRunner()
    runner.invoke(cli, ["config", "set-token", "--token", "T"])
    r = runner.invoke(
        cli,
        [
            "posts",
            "publish",
            "--page",
            "1",
            "-m",
            "x",
            "--at",
            "2020-01-01T10:00+01:00",
            "--dry-run",
        ],
    )
    assert r.exit_code != 0
    assert "futur" in r.output


def test_csv_flattens_nested():
    out = to_csv([{"id": "1", "from": {"name": "Ana"}}], ["id", "from.name"])
    assert out.splitlines()[1] == "1,Ana"
